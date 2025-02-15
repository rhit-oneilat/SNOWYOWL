import datetime
import streamlit as st


def create_add_guest_component(supabase):
    """Component to add a new guest to the database."""
    with st.form("add_guest_form"):
        guest_name = st.text_input("Guest Name").strip()
        host_name = st.text_input("Brother Name (Check Spelling)").strip()
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
                        "check_in_time": datetime.datetime.utcnow().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),  # Ensure timestamp format
                    },
                ).execute()

                st.write(response)  # Print full response to debug

                if response.data is True:  # Ensure correct response handling
                    st.success(f"Guest {guest_name.upper()} added successfully!")
                    st.rerun()
                else:
                    st.error("Failed to add guest. Please try again.")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")  # Print full error message
