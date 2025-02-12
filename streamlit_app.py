import streamlit as st
import pandas as pd
from supabase import create_client
from logic import PartyMonitor
from visualization import (
    plot_brother_guest_distribution,
    plot_gender_ratio,
    plot_class_distribution,
    plot_campus_distribution,
)
from streamlit_autorefresh import st_autorefresh  # type: ignore
from search_component import (
    create_guest_list_component,
    create_search_component,
    load_filtered_data,
    quick_add_guest,
)

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
    response = (
        supabase.table("guests")
        .select("*, brothers!inner(*)")  # Use inner join to get all brothers data
        .execute()
    )
    if response.data:
        df = pd.DataFrame(response.data)
        return df
    return pd.DataFrame()


st.session_state.guest_data = load_initial_data()

st.title("SNOWYOWL")

# Auto-refresh every 10 seconds
st_autorefresh(interval=10000, key="data_refresh")


# Create tabs
tab1, tab2 = st.tabs(["📊 Dashboard", "📜 Guest List & Check-In"])

# ---------------- Dashboard Tab ----------------
with tab1:
    if st.session_state.guest_data.empty:
        st.info("Upload guest lists to see the dashboard.")
    else:
        processed_df = st.session_state.guest_data
        stats = st.session_state.monitor.get_real_time_stats(processed_df)

        # Display metrics at the top
        metric_cols = st.columns(len(stats))
        for col, (key, value) in zip(metric_cols, stats.items()):
            col.metric(key, value)

        # Create two rows with two columns each for the plots
        row1_col1, row1_col2 = st.columns(2)
        row2_col1, row2_col2 = st.columns(2)

        # Place plots in the grid
        with row1_col1:
            st.plotly_chart(
                plot_brother_guest_distribution(processed_df), use_container_width=True
            )

        with row1_col2:
            st.plotly_chart(plot_gender_ratio(processed_df), use_container_width=True)

        with row2_col1:
            st.plotly_chart(
                plot_class_distribution(processed_df), use_container_width=True
            )

        with row2_col2:
            st.plotly_chart(
                plot_campus_distribution(processed_df), use_container_width=True
            )
# ---------------- Guest List & Check-In Tab ----------------
with tab2:
    if st.session_state.guest_data.empty:
        st.info("No guest data available.")
    else:
        st.subheader("Guest List & Check-In")
        with st.expander("Quick Add", expanded=False):
            quick_add_guest(supabase)
        search_state = create_search_component()
        filtered_data = load_filtered_data(supabase, search_state)
        create_guest_list_component(supabase, filtered_data)
