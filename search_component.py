import streamlit as st
import pandas as pd
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SearchState:
    query: str = ""
    status_filter: str = "all"
    location_filter: str = "all"
    brother_filter: str = "all"


@st.cache_data(ttl=300)  # Cache data for 5 minutes
def load_filtered_data(supabase, search_state: SearchState) -> pd.DataFrame:
    """Load and filter guest data with caching"""
    try:
        # Fetch all data with brother information
        response = supabase.table("guests").select("*, brothers!inner(*)").execute()
        df = pd.DataFrame(response.data) if response.data else pd.DataFrame()

        if df.empty:
            return df

        # Apply filters
        if search_state.query:
            query_lower = search_state.query.lower()
            name_match = df["name"].str.lower().str.contains(query_lower, na=False)
            brother_match = df["brothers"].apply(
                lambda x: x["name"].lower().contains(query_lower) if x else False
            )
            df = df[name_match | brother_match]

        if search_state.status_filter != "all":
            status_map = {
                "checked-in": "Checked In",
                "not-checked-in": "Not Checked In",
            }
            df = df[df["check_in_status"] == status_map[search_state.status_filter]]

        if search_state.location_filter != "all":
            location_map = {"on-campus": "On Campus", "off-campus": "Off Campus"}
            df = df[df["campus_status"] == location_map[search_state.location_filter]]

        if search_state.brother_filter != "all":
            df = df[
                df["brothers"].apply(lambda x: x["name"] == search_state.brother_filter)
            ]

        return df
    except Exception as e:
        st.error(f"Error fetching guest data: {str(e)}")
        return pd.DataFrame()


def handle_guest_status_update(supabase, guest_name: str, new_status: str) -> bool:
    """Handle updating a guest's status in the database"""
    try:
        update_data = {
            "check_in_status": new_status,
            "check_in_time": datetime.now().isoformat()
            if new_status == "Checked In"
            else None,
        }

        response = (
            supabase.table("guests")
            .update(update_data)
            .eq("name", guest_name)
            .execute()
        )
        return bool(response.data)
    except Exception as e:
        st.error(f"Error updating guest status: {str(e)}")
        return False


def create_guest_list_component(supabase, filtered_df: pd.DataFrame):
    """Creates a guest list component with improved status updates and confirmation"""
    if filtered_df.empty:
        st.info("No guests found matching your search criteria.")
        return

    with st.container():
        for index, row in filtered_df.iterrows():
            with st.container():
                col1, col2 = st.columns([4, 1])

                # Guest information with improved formatting
                with col1:
                    st.markdown(f"### {row['name']}")
                    st.markdown(
                        f"**Brother:** {row['brothers']['name']}  \n"
                        f"**Status:** {row['check_in_status']}  \n"
                        f"**Location:** {row['campus_status']}"
                    )
                    if row.get("check_in_time"):
                        st.caption(
                            f"Last check-in: {pd.to_datetime(row['check_in_time']).strftime('%Y-%m-%d %H:%M:%S')}"
                        )

                # Status update button with confirmation
                is_checked_in = row["check_in_status"] == "Checked In"
                button_text = "❌ Check Out" if is_checked_in else "✅ Check In"
                new_status = "Not Checked In" if is_checked_in else "Checked In"

                if col2.button(
                    button_text,
                    key=f"button_{row['name']}_{index}",
                    use_container_width=True,
                ):
                    action = "check out" if is_checked_in else "check in"
                    if st.modal(f"Confirm {action}").checkbox(
                        f"Are you sure you want to {action} {row['name']}?"
                    ):
                        if handle_guest_status_update(
                            supabase, row["name"], new_status
                        ):
                            st.toast(
                                f"Successfully {action}ed {row['name']}", icon="✅"
                            )
                            st.rerun()
                st.divider()


def create_search_component() -> SearchState:
    """Create the enhanced search interface component"""
    if "search_state" not in st.session_state:
        st.session_state.search_state = SearchState()

    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            search_query = st.text_input(
                "🔍",
                value=st.session_state.search_state.query,
                placeholder="Search guests or brothers...",
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

            # Brother filter will be populated from the available data
            brother_filter = "all"  # Default to all brothers

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
            brother_filter=brother_filter,
        )

        # Show active filters
        active_filters = []
        if status_filter != "all":
            active_filters.append(f"Status: {status_filter}")
        if location_filter != "all":
            active_filters.append(f"Location: {location_filter}")
        if active_filters:
            st.caption(f"Active filters: {', '.join(active_filters)}")

    return st.session_state.search_state
