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


@st.cache_data(ttl=300)
def _fetch_guest_data(_supabase):
    """Fetch guest data and store in cache."""
    try:
        response = _supabase.table("guests").select("*, brothers!inner(*)").execute()
        if not response.data:
            return pd.DataFrame()

        df = pd.DataFrame(response.data)
        df["name_lower"] = df["name"].str.lower()
        df["brother_name_lower"] = df["brothers"].apply(
            lambda x: x["name"].lower() if isinstance(x, dict) and "name" in x else ""
        )

        return df
    except Exception as e:
        st.error(f"Error fetching guest data: {str(e)}")
        return pd.DataFrame()


def load_filtered_data(supabase, search_state: SearchState) -> pd.DataFrame:
    """Apply search and filtering to guest data."""
    if "guest_data" not in st.session_state:
        st.session_state.guest_data = _fetch_guest_data(supabase)

    df = st.session_state.guest_data.copy()
    if df.empty:
        return df

    df["name_lower"] = df["name"].apply(lambda x: " ".join(x.split()).lower())
    df["brother_name_lower"] = df["brothers"].apply(
        lambda x: " ".join(x.split()).lower()
    )

    if search_state.query:
        query_lower = search_state.query.lower()
        df = df[
            df["name_lower"].str.contains(query_lower, na=False)
            | df["brother_name_lower"].str.contains(query_lower, na=False)
        ]

    if search_state.status_filter != "all":
        status_map = {"checked-in": "Checked In", "not-checked-in": "Not Checked In"}
        df = df[df["check_in_status"] == status_map[search_state.status_filter]]

    if search_state.location_filter != "all":
        location_map = {"on-campus": "On Campus", "off-campus": "Off Campus"}
        df = df[df["campus_status"] == location_map[search_state.location_filter]]

    return df


def handle_guest_status_update(supabase, guest_name: str, new_status: str):
    """Update guest check-in status."""
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

        if response.data:
            guest_index = st.session_state.guest_data[
                st.session_state.guest_data["name"] == guest_name
            ].index
            if not guest_index.empty:
                st.session_state.guest_data.at[guest_index[0], "check_in_status"] = (
                    new_status
                )
                st.session_state.guest_data.at[guest_index[0], "check_in_time"] = (
                    update_data["check_in_time"]
                )
            return True
        return False
    except Exception as e:
        st.error(f"Error updating guest status: {str(e)}")
        return False


def create_guest_list_component(supabase, filtered_df: pd.DataFrame):
    """Guest list with better status updates."""
    if filtered_df.empty:
        st.info("No guests found.")
        return

    for index, row in filtered_df.iterrows():
        with st.container():
            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(f"### {row['name']}")
                st.markdown(
                    f"**Brother:** {row['brothers']['name']}  \n"
                    f"**Status:** {row['check_in_status']}  \n"
                    f"**Location:** {row['campus_status']}\n"
                    "---"
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
                if handle_guest_status_update(supabase, row["name"], new_status):
                    st.toast(f"{row['name']} is now {new_status}.", icon="✅")


def create_search_component() -> SearchState:
    """Enhanced search interface with better performance."""
    if "search_state" not in st.session_state:
        st.session_state.search_state = SearchState()

    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            search_query = st.text_input(
                "🔍 Search",
                value=st.session_state.search_state.query,
                placeholder="Search guests or brothers...",
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

        if search_query or status_filter != "all" or location_filter != "all":
            if st.button("Clear Filters"):
                st.session_state.search_state = SearchState()
                st.rerun()

        st.session_state.search_state = SearchState(
            query=search_query,
            status_filter=status_filter,
            location_filter=location_filter,
        )

        active_filters = [
            f"Status: {status_filter}" if status_filter != "all" else "",
            f"Location: {location_filter}" if location_filter != "all" else "",
        ]
        active_filters = [f for f in active_filters if f]
        if active_filters:
            st.caption(f"Active filters: {', '.join(active_filters)}")

    return st.session_state.search_state


# --------- Quick Add Guest Feature ---------
def quick_add_guest(supabase):
    """Quick add guest UI."""
    with st.form("quick_add_form"):
        new_guest_name = st.text_input("Guest Name", "")
        host_name = st.text_input("Host (Brother Name)", "")
        campus_status = st.selectbox("On/Off Campus", ["On Campus", "Off Campus"])
        submit_button = st.form_submit_button("Add Guest")

        if submit_button and new_guest_name and host_name:
            response = (
                supabase.table("guests")
                .insert(
                    {
                        "name": new_guest_name,
                        "brother": host_name,  # Ensure structure matches DB
                        "campus_status": campus_status,
                        "check_in_status": "Not Checked In",
                        "late_add": 1,
                    }
                )
                .execute()
            )

            if response.error:
                st.error("Failed to add guest.")
            else:
                st.success(f"Guest {new_guest_name} added successfully!")
                st.cache_data.clear()
                st.rerun()
