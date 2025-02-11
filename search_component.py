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
def _fetch_guest_data(_supabase):
    """Fetch all guest data with caching"""
    try:
        response = _supabase.table("guests").select("*, brothers!inner(*)").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching guest data: {str(e)}")
        return pd.DataFrame()


def load_filtered_data(supabase, search_state: SearchState) -> pd.DataFrame:
    """Load and filter guest data"""
    df = _fetch_guest_data(supabase)
    if df.empty:
        return df

    if search_state.query:
        query_lower = search_state.query.lower()
        name_match = df["name"].str.lower().str.contains(query_lower, na=False)
        brother_match = df["brothers"].apply(
            lambda x: query_lower in x["name"].lower() if x else False
        )
        df = df[name_match | brother_match]

    if search_state.status_filter != "all":
        status_map = {"checked-in": "Checked In", "not-checked-in": "Not Checked In"}
        df = df[df["check_in_status"] == status_map[search_state.status_filter]]

    if search_state.location_filter != "all":
        location_map = {"on-campus": "On Campus", "off-campus": "Off Campus"}
        df = df[df["campus_status"] == location_map[search_state.location_filter]]

    if search_state.brother_filter != "all":
        df = df[
            df["brothers"].apply(lambda x: x["name"] == search_state.brother_filter)
        ]

    return df


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

                is_checked_in = row["check_in_status"] == "Checked In"
                button_text = "❌ Check Out" if is_checked_in else "✅ Check In"
                new_status = "Not Checked In" if is_checked_in else "Checked In"

                if col2.button(
                    button_text,
                    key=f"button_{row['name']}_{index}",
                    use_container_width=True,
                ):
                    confirm_key = f"confirm_{row['name']}_{index}"
                    st.session_state[confirm_key] = not st.session_state.get(
                        confirm_key, False
                    )

                if st.session_state.get(f"confirm_{row['name']}_{index}", False):
                    if st.checkbox(
                        f"Confirm {new_status.lower()} {row['name']}",
                        key=f"confirm_box_{row['name']}_{index}",
                    ):
                        if handle_guest_status_update(
                            supabase, row["name"], new_status
                        ):
                            st.toast(
                                f"Successfully updated {row['name']} to {new_status}",
                                icon="✅",
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
                ["all", "checked-in", "not-checked-in"],
                index=["all", "checked-in", "not-checked-in"].index(
                    st.session_state.search_state.status_filter
                ),
            )
            location_filter = st.selectbox(
                "Location",
                ["all", "on-campus", "off-campus"],
                index=["all", "on-campus", "off-campus"].index(
                    st.session_state.search_state.location_filter
                ),
            )
            brother_filter = "all"

        if search_query or status_filter != "all" or location_filter != "all":
            if st.button("Clear Filters"):
                search_query, status_filter, location_filter = "", "all", "all"
                st.session_state.search_state = SearchState()
                st.rerun()

        st.session_state.search_state = SearchState(
            query=search_query,
            status_filter=status_filter,
            location_filter=location_filter,
            brother_filter=brother_filter,
        )
        active_filters = [
            f"Status: {status_filter}" if status_filter != "all" else "",
            f"Location: {location_filter}" if location_filter != "all" else "",
        ]
        active_filters = [f for f in active_filters if f]
        if active_filters:
            st.caption(f"Active filters: {', '.join(active_filters)}")

    return st.session_state.search_state
