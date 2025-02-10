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
from streamlit_autorefresh import st_autorefresh
from rapidfuzz import process

# Supabase credentials
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]


supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Hardcoded username and password
USERNAME = "door"
PASSWORD = "pgd1848"


# Authentication function
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

        st.stop()  # Prevents further execution until login


check_auth()


# Fetch guest data from Supabase
def load_guest_data():
    response = supabase.table("guests").select("*").execute()
    return pd.DataFrame(response.data) if response.data else pd.DataFrame()


# Initialize session state
if "monitor" not in st.session_state:
    st.session_state.monitor = PartyMonitor()

st.session_state.guest_data = load_guest_data()

st.title("SNOWYOWL")

# Auto-refresh every 2 seconds
st_autorefresh(interval=2000, key="data_refresh")

# File Uploaders in Sidebar
st.sidebar.header("📂 Guest Lists")
on_campus_file = st.sidebar.file_uploader("Upload On-Campus Guest List", type=["csv"])
off_campus_file = st.sidebar.file_uploader("Upload Off-Campus Guest List", type=["csv"])

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
        search_query = st.text_input("Search Guest by Name")

        status_filter = st.selectbox(
            "Filter by Status", ["All", "Checked In", "Not Checked In"]
        )
        location_filter = st.selectbox(
            "Filter by Location", ["All", "On Campus", "Off Campus"]
        )

        filtered_df = st.session_state.guest_data.copy()

        # Apply search filter
        if search_query:
            guest_names = filtered_df["name"].dropna().astype(str).tolist()
            matches = process.extract(search_query, guest_names, limit=5)
            matched_names = [match[0] for match in matches if match[1] > 70]

            if matched_names:
                filtered_df = filtered_df[filtered_df["name"].isin(matched_names)]
            else:
                st.warning("No matching guests found.")
                filtered_df = pd.DataFrame()

        # Apply dropdown filters
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df["check_in_status"] == status_filter]

        if location_filter != "All":
            filtered_df = filtered_df[filtered_df["campus_status"] == location_filter]

        # Display Table
        st.write("### Guest List")
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
                    st.success(f"{row['name']} has been checked in!")
                    time.sleep(1)
                    st.rerun()
            else:
                if col2.button("❌ Check Out", key=f"checkout_{index}"):
                    supabase.table("guests").update(
                        {"check_in_status": "Not Checked In"}
                    ).eq("name", row["name"]).execute()
                    st.success(f"{row['name']} has been checked out!")
                    time.sleep(1)
                    st.rerun()
