import streamlit as st
import pandas as pd
from dataclasses import dataclass


@dataclass
class SearchState:
    query: str = ""
    status_filter: str = "all"
    location_filter: str = "all"


def handle_guest_status_update(supabase, guest_name: str, new_status: str) -> bool:
    """Handle updating a guest's status in the database"""
    try:
        response = (
            supabase.table("guests")
            .update({"check_in_status": new_status})
            .eq("name", guest_name)
            .execute()
        )
        return bool(response.data)
    except Exception as e:
        st.error(f"Error updating guest status: {str(e)}")
        return False


def create_guest_list_component(supabase, filtered_df: pd.DataFrame):
    """Creates a guest list component with improved button handling"""
    if filtered_df.empty:
        st.info("No guests found matching your search criteria.")
        return

    # Use a container for better organization
    with st.container():
        for index, row in filtered_df.iterrows():
            col1, col2 = st.columns([4, 1])

            # Display guest information
            col1.write(
                f"**{row['name']}** (Brother: {row['brothers']['name']}, Status: {row['check_in_status']})"
            )

            is_checked_in = row["check_in_status"] == "Checked In"
            button_text = "❌ Check Out" if is_checked_in else "✅ Check In"
            new_status = "Not Checked In" if is_checked_in else "Checked In"

            # Simplified button handling without session state
            if col2.button(
                button_text,
                key=f"button_{row['name']}_{index}",
                use_container_width=True,
            ):
                if handle_guest_status_update(supabase, row["name"], new_status):
                    st.toast(
                        f"Successfully {'checked out' if is_checked_in else 'checked in'} {row['name']}"
                    )
                    st.rerun()


def load_filtered_data(supabase, search_state: SearchState):
    """Load filtered guest data from the database"""
    query = supabase.table("guests").select("*, brothers!inner(*)")

    if search_state.query:
        query = query.text_search("name_tsv", search_state.query)

    if search_state.status_filter != "all":
        status_map = {"checked-in": "Checked In", "not-checked-in": "Not Checked In"}
        query = query.eq("check_in_status", status_map[search_state.status_filter])

    if search_state.location_filter != "all":
        location_map = {"on-campus": "On Campus", "off-campus": "Off Campus"}
        query = query.eq("campus_status", location_map[search_state.location_filter])

    response = query.execute()
    return pd.DataFrame(response.data) if response.data else pd.DataFrame()


def create_search_component():
    """Create the search interface component"""
    search_container = st.container()

    if "search_state" not in st.session_state:
        st.session_state.search_state = SearchState()

    with search_container:
        col1, col2 = st.columns([3, 1])
        with col1:
            search_query = st.text_input(
                "🔍",
                value=st.session_state.search_state.query,
                placeholder="Search guests...",
                label_visibility="collapsed",
            )

        with st.expander("Filters", expanded=False):
            status_filter = st.selectbox(
                "Status",
                options=["all", "checked-in", "not-checked-in"],
                format_func=lambda x: {
                    "all": "All Statuses",
                    "checked-in": "Checked In",
                    "not-checked-in": "Not Checked In",
                }[x],
                index=["all", "checked-in", "not-checked-in"].index(
                    st.session_state.search_state.status_filter
                ),
            )
            location_filter = st.selectbox(
                "Location",
                options=["all", "on-campus", "off-campus"],
                format_func=lambda x: {
                    "all": "All Locations",
                    "on-campus": "On Campus",
                    "off-campus": "Off Campus",
                }[x],
                index=["all", "on-campus", "off-campus"].index(
                    st.session_state.search_state.location_filter
                ),
            )

        if search_query or status_filter != "all" or location_filter != "all":
            if st.button("Clear Filters"):
                search_query = ""
                status_filter = "all"
                location_filter = "all"
                st.session_state.search_state = SearchState()
                st.rerun()

        st.session_state.search_state = SearchState(
            query=search_query,
            status_filter=status_filter,
            location_filter=location_filter,
        )

        if status_filter != "all" or location_filter != "all":
            active_filters = []
            if status_filter != "all":
                active_filters.append(f"Status: {status_filter}")
            if location_filter != "all":
                active_filters.append(f"Location: {location_filter}")
            st.caption(f"Active filters: {', '.join(active_filters)}")

    return st.session_state.search_state
