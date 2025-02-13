import plotly.graph_objects as go
import streamlit as st
import pandas as pd

from visualization import (
    plot_brother_guest_distribution,
    plot_campus_distribution,
    plot_class_distribution,
    plot_gender_ratio,
)


def create_dashboard_component(filtered_df: pd.DataFrame):
    """Enhanced dashboard component combining existing and new visualizations."""
    if filtered_df.empty:
        st.info("No guest data available for dashboard.")
        return

    # Calculate key metrics
    total_guests = len(filtered_df)
    checked_in_guests = len(filtered_df[filtered_df["check_in_status"] == "Checked In"])
    capacity_pct = (checked_in_guests / total_guests) * 100 if total_guests > 0 else 0
    late_adds = filtered_df["late_add"].sum()

    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Current Capacity",
            f"{checked_in_guests}/{total_guests}",
            f"{capacity_pct:.1f}%",
        )

    with col2:
        st.metric(
            "Quick Adds",
            str(late_adds),
            help="Number of guests added after initial list",
        )

    # Campus status breakdown for checked-in guests
    checked_in_df = filtered_df[filtered_df["check_in_status"] == "Checked In"]
    campus_breakdown = checked_in_df["campus_status"].value_counts()
    on_campus = campus_breakdown.get("On Campus", 0)
    off_campus = campus_breakdown.get("Off Campus", 0)
    on_campus_pct = (
        (on_campus / checked_in_guests) * 100 if checked_in_guests > 0 else 0
    )
    F_guests = (checked_in_df["gender"] == "F").sum()
    M_guests = (checked_in_df["gender"] == "M").sum()
    F_pct = (F_guests / checked_in_guests) * 100 if checked_in_guests > 0 else 0

    with col3:
        st.metric(
            "Checked-In Location Split",
            f"{on_campus}/{off_campus}",
            f"{on_campus_pct:.1f}% On Campus",
        )

    with col4:
        st.metric(
            "Checked-In Gender Split", f"{F_guests}/{M_guests}", f"{F_pct:.1f}% F"
        )
    # Create tabs for different chart categories
    tab1, tab2 = st.tabs(["Live Check-Ins", "Listed Guest Distribution"])

    with tab1:
        # Check-ins over time
        st.subheader("Check-ins Over Time")
        time_data = checked_in_df[checked_in_df["check_in_time"].notna()].copy()
        if not time_data.empty:
            time_data["check_in_time"] = pd.to_datetime(time_data["check_in_time"])
            time_data = time_data.sort_values("check_in_time")

            y_values = list(range(1, len(time_data) + 1))

            fig = go.Figure(
                go.Scatter(
                    x=time_data["check_in_time"],
                    y=y_values,
                    mode="lines",
                    name="Cumulative Check-ins",
                )
            )
            fig.update_layout(
                title="Cumulative Check-ins",
                xaxis_title="Time",
                yaxis_title="Total Check-ins",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No check-in time data available")

    with tab2:
        # First row of charts
        col1, col2 = st.columns(2)

        with col1:
            # Brother distribution chart
            st.plotly_chart(
                plot_brother_guest_distribution(filtered_df), use_container_width=True
            )
            st.plotly_chart(
                plot_class_distribution(filtered_df), use_container_width=True
            )

        with col2:
            # Second row split into two charts
            st.plotly_chart(plot_gender_ratio(filtered_df), use_container_width=True)
            st.plotly_chart(
                plot_campus_distribution(filtered_df), use_container_width=True
            )
