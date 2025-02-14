import streamlit as st
import pandas as pd
from supabase import create_client
from dashboard_component import create_dashboard_component
from search_component import (
    create_guest_list_component,
    create_search_component,
    load_filtered_data,
)
from add_guest_component import create_add_guest_component

# Supabase credentials
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

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


# Load initial data
def load_initial_data():
    response = supabase.table("guests").select("*, brothers!inner(*)").execute()
    if response.data:
        return pd.DataFrame(response.data)
    return pd.DataFrame()


st.session_state.guest_data = load_initial_data()

st.title("SNOWYOWL")

if st.button("Refresh Data 🔄"):
    st.session_state.guest_data = load_initial_data()
    st.rerun()

# Create tabs
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📜 Guest List & Check-In", "➕ Add Guest"])

# Dashboard Tab
with tab1:
    if st.session_state.guest_data.empty:
        st.info("Upload guest lists to see the dashboard.")
    else:
        processed_df = st.session_state.guest_data
        create_dashboard_component(processed_df)

# Guest List & Check-In Tab
with tab2:
    if st.session_state.guest_data.empty:
        st.info("No guest data available.")
    else:
        st.subheader("Guest List & Check-In")
        search_state = create_search_component()
        filtered_data = load_filtered_data(supabase, search_state)
        create_guest_list_component(supabase, filtered_data)

# Add Guest Tab
with tab3:
    st.subheader("Add Guest")
    create_add_guest_component(supabase)
