import plotly.graph_objects as go


def plot_brother_guest_distribution(df):
    """Create bar chart showing number of guests per brother"""
    guest_counts = df.groupby("brother").size().sort_values(ascending=True)

    fig = go.Figure(
        go.Bar(x=guest_counts.values, y=guest_counts.index, orientation="h")
    )

    fig.update_layout(
        title="Guests per Brother",
        xaxis_title="Number of Guests",
        yaxis_title="Brother Name",
        height=max(400, len(guest_counts) * 25),
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
    if "year" not in df.columns or df["year"].isna().all():
        return go.Figure().update_layout(title="No class year data available")

    class_counts = df["year"].value_counts().sort_index()

    fig = go.Figure(go.Bar(x=class_counts.index.astype(str), y=class_counts.values))
    fig.update_layout(
        title="Guests by Brother's Class",
        xaxis_title="Class Year",
        yaxis_title="Number of Guests",
        xaxis=dict(dtick=1),
    )
    return fig
