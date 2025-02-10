# search_component.py
import streamlit as st
from dataclasses import dataclass
import supabase
import pandas as pd


@dataclass
class SearchState:
    query: str = ""
    status_filter: str = "all"
    location_filter: str = "all"


def create_search_component():
    # Create container for search component
    search_container = st.container()

    # Initialize session state for search
    if "search_state" not in st.session_state:
        st.session_state.search_state = SearchState()

    # Create columns for search and filters
    with search_container:
        # Search input with icon
        col1, col2 = st.columns([3, 1])
        with col1:
            search_query = st.text_input(
                "🔍",
                value=st.session_state.search_state.query,
                placeholder="Search guests...",
                label_visibility="collapsed",
            )

        # Expander for filters
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

        # Clear filters button
        if search_query or status_filter != "all" or location_filter != "all":
            if st.button("Clear Filters"):
                search_query = ""
                status_filter = "all"
                location_filter = "all"
                st.session_state.search_state = SearchState()
                st.rerun()

        # Update session state
        st.session_state.search_state = SearchState(
            query=search_query,
            status_filter=status_filter,
            location_filter=location_filter,
        )

        # Display active filters
        if status_filter != "all" or location_filter != "all":
            active_filters = []
            if status_filter != "all":
                active_filters.append(f"Status: {status_filter}")
            if location_filter != "all":
                active_filters.append(f"Location: {location_filter}")
            st.caption(f"Active filters: {', '.join(active_filters)}")

    return st.session_state.search_state


# Updated load_guest_data function
def load_guest_data(search_state: SearchState):
    query = supabase.table("guests").select("*")

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
