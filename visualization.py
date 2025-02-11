import plotly.graph_objects as go
import streamlit as st


def plot_brother_guest_distribution(df):
    """
    Create an interactive bar chart showing number of guests per brother with
    options to display different numbers of brothers.

    Parameters:
    df (pandas.DataFrame): DataFrame containing 'brother' column

    Returns:
    plotly.graph_objects.Figure: Plotly figure object
    """
    # Calculate guest counts and sort
    guest_counts = df.groupby("brother").size().sort_values(ascending=False)

    # Create selection box for number of brothers to display
    display_options = {"Top 5": 5, "Top 10": 10, "Top 15": 15, "All": len(guest_counts)}

    selected_display = st.selectbox(
        "Select number of brothers to display:",
        options=list(display_options.keys()),
        index=0,  # Default to first option
    )

    # Get number of brothers to display
    n_brothers = display_options[selected_display]

    # Filter data based on selection
    displayed_counts = guest_counts.head(n_brothers)

    # Create horizontal bar chart using graph_objects
    fig = go.Figure(
        go.Bar(
            x=displayed_counts.values.tolist(),
            y=displayed_counts.index.tolist(),
            orientation="h",
            marker_color="rgb(79, 70, 229)",  # Indigo color for consistency
        )
    )

    # Update layout
    fig.update_layout(
        title=f"Guests per Brother ({selected_display})",
        xaxis_title="Number of Guests",
        yaxis_title="Brother Name",
        yaxis={"categoryorder": "total ascending"},
        height=max(
            400, len(displayed_counts) * 25
        ),  # Dynamic height based on number of bars
        showlegend=False,
    )

    return fig


def plot_gender_ratio(df):
    """Create pie chart showing gender distribution"""
    gender_counts = df["gender"].value_counts()

    fig = go.Figure(
        go.Pie(labels=gender_counts.index, values=gender_counts.values, hole=0.4)
    )

    fig.update_layout(title="Gender Distribution", showlegend=True)

    return fig


def plot_campus_distribution(df):
    campus_counts = df["campus_status"].value_counts()
    fig = go.Figure(
        go.Pie(labels=campus_counts.index, values=campus_counts.values, hole=0.4)
    )
    fig.update_layout(title="On-Campus vs Off-Campus Guests")
    return fig


def plot_class_distribution(df):
    """Create bar chart showing number of guests per brother's class."""
    # Extract year from the brothers nested data
    if "brothers" in df.columns:
        # Extract year from the brothers dictionary
        years = df["brothers"].apply(lambda x: x.get("year") if x else None)
    else:
        years = df.get("year")

    if years is None or years.isna().all():
        return go.Figure().update_layout(title="No class year data available")

    class_counts = years.value_counts().sort_index()

    fig = go.Figure(go.Bar(x=class_counts.index.astype(str), y=class_counts.values))
    fig.update_layout(
        title="Guests by Brother's Class",
        xaxis_title="Class Year",
        yaxis_title="Number of Guests",
        xaxis=dict(dtick=1),
    )
    return fig
