import streamlit as st
import pandas as pd
import time
from supabase import create_client
from logic import PartyMonitor
from visualization import (
    plot_brother_guest_distribution,
    plot_gender_ratio,
    plot_class_distribution,
    plot_campus_distribution,
)
from streamlit_autorefresh import st_autorefresh  # type: ignore
from search_component import SearchState, create_search_component

# Supabase credentials
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Hardcoded username and password
USERNAME = "door"
PASSWORD = "pgd1848"


def check_auth():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        with st.form("Login Form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                if username == USERNAME and password == PASSWORD:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Invalid credentials")

        st.stop()


check_auth()

# Initialize session state
if "monitor" not in st.session_state:
    st.session_state.monitor = PartyMonitor()


# Modified to load initial data without filters
def load_initial_data():
    response = supabase.table("guests").select("*").execute()
    return pd.DataFrame(response.data) if response.data else pd.DataFrame()


st.session_state.guest_data = load_initial_data()

st.title("SNOWYOWL")

# Auto-refresh every 10 seconds
st_autorefresh(interval=10000, key="data_refresh")

# File Uploaders in Sidebar
st.sidebar.header("📂 Guest Lists")
on_campus_file = st.sidebar.file_uploader("Upload On-Campus Guest List", type=["csv"])
off_campus_file = st.sidebar.file_uploader("Upload Off-Campus Guest List", type=["csv"])

if on_campus_file and off_campus_file:
    # Read CSVs
    on_campus_df = pd.read_csv(on_campus_file)
    off_campus_df = pd.read_csv(off_campus_file)

    # Process guests
    on_melted = on_campus_df.melt(var_name="brother", value_name="name").dropna()
    off_melted = off_campus_df.melt(var_name="brother", value_name="name").dropna()

    on_melted["campus_status"] = "On Campus"
    off_melted["campus_status"] = "Off Campus"

    all_guests = pd.concat([on_melted, off_melted])

    # Standardize guest names
    all_guests["name"] = all_guests["name"].str.upper()

    # Assign check-in status
    all_guests["check_in_status"] = "Not Checked In"

    # Convert to dictionary for Supabase upsert
    guest_records = all_guests.to_dict(orient="records")

    # Upsert into Supabase
    supabase.table("guests").upsert(guest_records).execute()

    # Get current guests in the database
    existing_guest_data = load_initial_data()

    # Find guests in the database but NOT in the new upload
    to_delete = existing_guest_data[
        ~existing_guest_data["name"].isin(all_guests["name"])
    ]

    # Bulk delete missing guests
    if not to_delete.empty:
        supabase.table("guests").delete().in_(
            "name", to_delete["name"].tolist()
        ).execute()

    # Refresh the data
    st.session_state.guest_data = load_initial_data()
    st.success("Guest list updated successfully!")
    time.sleep(1)
    st.rerun()


# Create tabs
tab1, tab2 = st.tabs(["📊 Dashboard", "📜 Guest List & Check-In"])

# ---------------- Dashboard Tab ----------------
with tab1:
    if st.session_state.guest_data.empty:
        st.info("Upload guest lists to see the dashboard.")
    else:
        processed_df = st.session_state.guest_data
        stats = st.session_state.monitor.get_real_time_stats(processed_df)
        metric_cols = st.columns(len(stats))
        for col, (key, value) in zip(metric_cols, stats.items()):
            col.metric(key, value)
        st.plotly_chart(
            plot_brother_guest_distribution(processed_df), use_container_width=True
        )
        st.plotly_chart(plot_gender_ratio(processed_df), use_container_width=True)
        st.plotly_chart(plot_class_distribution(processed_df), use_container_width=True)
        st.plotly_chart(
            plot_campus_distribution(processed_df), use_container_width=True
        )

# ---------------- Guest List & Check-In Tab ----------------
with tab2:
    if st.session_state.guest_data.empty:
        st.info("No guest data available.")
    else:
        st.subheader("Guest List & Check-In")

        # Use the new search component
        search_state = create_search_component()

        # Load filtered data
        def load_filtered_data(search_state: SearchState):
            query = supabase.table("guests").select("*")

            if search_state.query:
                query = query.text_search("name_tsv", search_state.query)

            if search_state.status_filter != "all":
                status_map = {
                    "checked-in": "Checked In",
                    "not-checked-in": "Not Checked In",
                }
                query = query.eq(
                    "check_in_status", status_map[search_state.status_filter]
                )

            if search_state.location_filter != "all":
                location_map = {"on-campus": "On Campus", "off-campus": "Off Campus"}
                query = query.eq(
                    "campus_status", location_map[search_state.location_filter]
                )

            response = query.execute()
            return pd.DataFrame(response.data) if response.data else pd.DataFrame()

        filtered_df = load_filtered_data(search_state)

        # Display Table
        st.write("### Guest List")
        if filtered_df.empty:
            st.info("No guests found matching your search criteria.")
        else:
            for index, row in filtered_df.iterrows():
                col1, col2 = st.columns([4, 1])
                col1.write(
                    f"**{row['name']}** (Brother: {row['brother']}, Status: {row['check_in_status']})"
                )
                if row["check_in_status"] == "Not Checked In":
                    if col2.button("✅ Check In", key=f"checkin_{index}"):
                        supabase.table("guests").update(
                            {"check_in_status": "Checked In"}
                        ).eq("name", row["name"]).execute()
                        st.rerun()

                else:
                    if col2.button("❌ Check Out", key=f"checkout_{index}"):
                        supabase.table("guests").update(
                            {"check_in_status": "Not Checked In"}
                        ).eq("name", row["name"]).execute()
                        st.rerun()
