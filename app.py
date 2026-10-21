import pandas as pd
import plotly.express as px
import streamlit as st


# --------------------------------------------------
# PAGE CONFIGURATION
# ---------------------SS-----------------------------

st.set_page_config(
    page_title="ChartPulse",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        [data-testid="stMetric"] {
            background-color: #181818;
            border: 1px solid #2f2f2f;
            padding: 18px;
            border-radius: 14px;
        }

        [data-testid="stMetricLabel"] {
            color: #b3b3b3;
        }

        [data-testid="stMetricValue"] {
            color: #1DB954;
        }

        section[data-testid="stSidebar"] {
            background-color: #121212;
        }

        div[data-testid="stExpander"] {
            border: 1px solid #2f2f2f;
            border-radius: 12px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# FILE AND COLUMN SETTINGS
# --------------------------------------------------

# Change this only if your CSV has a different filename.
CSV_FILE = "charts_albums_weekly.csv"


@st.cache_data
def load_data():
    data = pd.read_csv(CSV_FILE, low_memory=False)

    # Remove extra spaces and standardize column names.
    data.columns = (
        data.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    return data


def find_column(columns, possible_names):
    """Find a column using a list of possible column names."""
    for name in possible_names:
        if name in columns:
            return name
    return None


# --------------------------------------------------
# LOAD THE DATA
# --------------------------------------------------

try:
    df = load_data()

except FileNotFoundError:
    st.error(
        f"Could not find '{CSV_FILE}'. Make sure the CSV is in the "
        "same folder as app.py, or update CSV_FILE in the code."
    )
    st.stop()

except Exception as error:
    st.error(f"The CSV could not be loaded: {error}")
    st.stop()


# --------------------------------------------------
# AUTOMATICALLY IDENTIFY IMPORTANT COLUMNS
# --------------------------------------------------

country_column = find_column(
    df.columns,
    ["country", "country_code", "market", "region"]
)

date_column = find_column(
    df.columns,
    ["date", "chart_date", "week", "week_start", "snapshot_date"]
)

rank_column = find_column(
    df.columns,
    ["rank", "position", "chart_position", "current_rank"]
)

song_column = find_column(
    df.columns,
    ["track_name", "song_name", "title", "track", "song"]
)

artist_column = find_column(
    df.columns,
    ["artist_name", "artist", "artists", "performer"]
)

streams_column = find_column(
    df.columns,
    ["streams", "stream_count", "listeners", "plays"]
)


required_columns = {
    "country": country_column,
    "date": date_column,
    "rank": rank_column,
    "song": song_column,
    "artist": artist_column,
}

missing_columns = [
    name for name, column in required_columns.items()
    if column is None
]

if missing_columns:
    st.error(
        "ChartPulse could not identify these required fields: "
        + ", ".join(missing_columns)
    )

    st.write("Columns found in your CSV:")
    st.code(", ".join(df.columns))

    st.info(
        "Update the possible column names in the "
        "'AUTOMATICALLY IDENTIFY IMPORTANT COLUMNS' section."
    )

    st.stop()


# --------------------------------------------------
# CLEAN THE DATA
# --------------------------------------------------

df = df.dropna(
    subset=[
        country_column,
        date_column,
        rank_column,
        song_column,
        artist_column,
    ]
).copy()

df[date_column] = pd.to_datetime(
    df[date_column],
    errors="coerce"
)

df[rank_column] = pd.to_numeric(
    df[rank_column],
    errors="coerce"
)

if streams_column:
    df[streams_column] = pd.to_numeric(
        df[streams_column],
        errors="coerce"
    )

df = df.dropna(
    subset=[
        date_column,
        rank_column,
    ]
)

df[country_column] = (
    df[country_column]
    .astype(str)
    .str.strip()
    .str.lower()
)

df[song_column] = (
    df[song_column]
    .astype(str)
    .str.strip()
)

df[artist_column] = (
    df[artist_column]
    .astype(str)
    .str.strip()
)


# --------------------------------------------------
# COUNTRY NAMES
# --------------------------------------------------

country_names = {
    "ar": "Argentina",
    "at": "Austria",
    "au": "Australia",
    "be": "Belgium",
    "br": "Brazil",
    "ca": "Canada",
    "ch": "Switzerland",
    "cl": "Chile",
    "co": "Colombia",
    "cz": "Czech Republic",
    "de": "Germany",
    "dk": "Denmark",
    "do": "Dominican Republic",
    "ec": "Ecuador",
    "es": "Spain",
    "fi": "Finland",
    "fr": "France",
    "gb": "United Kingdom",
    "global": "Global",
    "gt": "Guatemala",
    "hk": "Hong Kong",
    "hu": "Hungary",
    "id": "Indonesia",
    "ie": "Ireland",
    "in": "India",
    "it": "Italy",
    "jp": "Japan",
    "kz": "Kazakhstan",
    "mx": "Mexico",
    "my": "Malaysia",
    "ng": "Nigeria",
    "nl": "Netherlands",
    "no": "Norway",
    "nz": "New Zealand",
    "pe": "Peru",
    "ph": "Philippines",
    "pk": "Pakistan",
    "pl": "Poland",
    "pt": "Portugal",
    "py": "Paraguay",
    "ro": "Romania",
    "sa": "Saudi Arabia",
    "se": "Sweden",
    "sg": "Singapore",
    "sk": "Slovakia",
    "sv": "El Salvador",
    "th": "Thailand",
    "tr": "Turkey",
    "tw": "Taiwan",
    "us": "United States",
    "vn": "Vietnam",
    "za": "South Africa",
}

df["country_name"] = df[country_column].map(country_names)

df["country_name"] = df["country_name"].fillna(
    df[country_column].str.upper()
)


# --------------------------------------------------
# DASHBOARD HEADER
# --------------------------------------------------

st.title("🎵 ChartPulse")
st.caption(
    "Explore Spotify chart rankings across countries and dates."
)

st.divider()


# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.title("🎛️ Chart Filters")
st.sidebar.caption("Use the options below to update the dashboard.")

available_countries = sorted(
    df["country_name"].dropna().unique()
)

default_country = (
    available_countries.index("United States")
    if "United States" in available_countries
    else 0
)

selected_country = st.sidebar.selectbox(
    "Country or market",
    options=available_countries,
    index=default_country,
)

country_df = df[
    df["country_name"] == selected_country
].copy()

available_dates = sorted(
    country_df[date_column].dropna().dt.date.unique(),
    reverse=True,
)

if not available_dates:
    st.warning(
        f"No chart dates are available for {selected_country}."
    )
    st.stop()

selected_date = st.sidebar.selectbox(
    "Chart date",
    options=available_dates,
    index=0,
    format_func=lambda value: value.strftime("%B %d, %Y"),
)

number_of_songs = st.sidebar.slider(
    "Number of songs to display",
    min_value=5,
    max_value=20,
    value=10,
    step=5,
)

st.sidebar.divider()

st.sidebar.markdown(
    """
    **About ChartPulse**

    ChartPulse is an interactive dashboard for exploring
    music rankings across different countries and dates.
    """
)


# --------------------------------------------------
# FILTER THE DATA
# --------------------------------------------------

filtered_df = country_df[
    country_df[date_column].dt.date == selected_date
].copy()

filtered_df = (
    filtered_df
    .sort_values(rank_column)
    .drop_duplicates(
        subset=[song_column, artist_column],
        keep="first"
    )
    .head(number_of_songs)
)

if filtered_df.empty:
    st.warning(
        "No chart information is available for the selected filters."
    )
    st.stop()

top_song = filtered_df.iloc[0]


# --------------------------------------------------
# SUMMARY METRIC CARDS
# --------------------------------------------------

metric1, metric2, metric3, metric4 = st.columns(4)

metric1.metric(
    label="🏆 Number One Song",
    value=str(top_song[song_column]),
)

metric2.metric(
    label="🎤 Number One Artist",
    value=str(top_song[artist_column]),
)

metric3.metric(
    label="🌎 Selected Market",
    value=selected_country,
)

metric4.metric(
    label="📅 Chart Date",
    value=selected_date.strftime("%b %d, %Y"),
)


# --------------------------------------------------
# CHART HEADING
# --------------------------------------------------

st.subheader(f"Top {len(filtered_df)} Songs in {selected_country}")

st.caption(
    f"Chart rankings for {selected_date.strftime('%B %d, %Y')}"
)


# --------------------------------------------------
# PREPARE THE CHART
# --------------------------------------------------

chart_df = filtered_df.copy()

chart_df["song_and_artist"] = (
    chart_df[song_column]
    + " • "
    + chart_df[artist_column]
)

# Create a visual score so that rank 1 has the longest bar.
chart_df["chart_score"] = (
    chart_df[rank_column].max()
    + 1
    - chart_df[rank_column]
)

chart_df = chart_df.sort_values(
    rank_column,
    ascending=False
)


# --------------------------------------------------
# CREATE THE CHART
# --------------------------------------------------

hover_data = {
    "song_and_artist": False,
    song_column: True,
    artist_column: True,
    rank_column: True,
    "chart_score": False,
}

if streams_column:
    hover_data[streams_column] = ":,.0f"

fig = px.bar(
    chart_df,
    x="chart_score",
    y="song_and_artist",
    orientation="h",
    color="chart_score",
    color_continuous_scale=[
        "#179443",
        "#1DB954",
        "#57D47D",
    ],
    custom_data=[rank_column],
    hover_data=hover_data,
)

fig.update_traces(
    texttemplate="#%{customdata[0]}",
    textposition="inside",
    hovertemplate=(
        "<b>%{y}</b><br>"
        "Chart position: #%{customdata[0]}"
        "<extra></extra>"
    ),
)

fig.update_layout(
    height=max(500, len(chart_df) * 48),
    margin=dict(l=10, r=20, t=20, b=10),
    xaxis_title=None,
    yaxis_title=None,
    coloraxis_showscale=False,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(size=14),
    hoverlabel=dict(
        bgcolor="#181818",
        font_color="white",
    ),
)

fig.update_xaxes(
    visible=False,
    showgrid=False,
)

fig.update_yaxes(
    tickfont=dict(size=13),
)

st.plotly_chart(
    fig,
    use_container_width=True,
)


# --------------------------------------------------
# DATA TABLE
# --------------------------------------------------

with st.expander("📋 View chart data"):
    display_columns = [
        rank_column,
        song_column,
        artist_column,
    ]

    if streams_column:
        display_columns.append(streams_column)

    display_df = filtered_df[display_columns].copy()

    rename_columns = {
        rank_column: "Rank",
        song_column: "Song",
        artist_column: "Artist",
    }

    if streams_column:
        rename_columns[streams_column] = "Streams"

    display_df = display_df.rename(
        columns=rename_columns
    )

    display_df["Rank"] = (
        display_df["Rank"]
        .astype(int)
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )


# --------------------------------------------------
# DOWNLOAD BUTTON
# --------------------------------------------------

download_df = filtered_df[
    [
        rank_column,
        song_column,
        artist_column,
        country_column,
        date_column,
    ]
].copy()

download_csv = download_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇️ Download selected chart",
    data=download_csv,
    file_name=(
        f"chartpulse_"
        f"{selected_country.lower().replace(' ', '_')}_"
        f"{selected_date}.csv"
    ),
    mime="text/csv",
)


# --------------------------------------------------
# FOOTER
