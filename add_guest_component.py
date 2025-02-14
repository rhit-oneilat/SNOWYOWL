import streamlit as st
from datetime import datetime


def create_add_guest_component(supabase):
    """Component to add a new guest to the database."""
    with st.form("add_guest_form"):
        guest_name = st.text_input("Guest Name").strip()
        host_name = st.text_input("Host Name (Check Spelling)").strip()
        campus_status = st.selectbox("Campus Status", ["On Campus", "Off Campus"])
        gender = st.selectbox("Gender", ["M", "F"])
        submit_button = st.form_submit_button("Add Guest")

        if submit_button and guest_name and host_name:
            try:
                response = supabase.rpc(
                    "add_guest",
                    {
                        "guest_name": guest_name.upper(),
                        "host_name": host_name,
                        "campus_status": campus_status,
                        "gender": gender,
                        "check_in_time": datetime.utcnow().isoformat(),
                    },
                ).execute()

                if response.data:
                    st.success(f"Guest {guest_name.upper()} added successfully!")
                    st.experimental_rerun()
                else:
                    st.error("Failed to add guest. Please try again.")
            except Exception as e:
                error_message = str(getattr(e, "error", "Unknown error"))
                if "brother" in error_message:
                    st.error(f"Error: Brother '{host_name}' not found. Check spelling.")
                else:
                    st.error("An unexpected error occurred. Please try again.")
