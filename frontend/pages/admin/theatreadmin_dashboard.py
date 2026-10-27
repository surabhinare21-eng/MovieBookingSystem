
import json
import pandas as pd
import streamlit as st
from common import api


st.set_page_config(
    page_title="Superadmin Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)


def response_to_dataframe(data):
    """Convert common API response formats into a DataFrame safely."""

    if isinstance(data, list):
        return pd.DataFrame(data)

    if isinstance(data, dict):
        # Handle common API response wrappers.
        for key in ("data", "shows", "results", "items"):
            if key in data:
                records = data[key]

                if isinstance(records, list):
                    return pd.DataFrame(records)

                if isinstance(records, dict):
                    return pd.DataFrame([records])

                return pd.DataFrame()

        return pd.DataFrame([data]) if data else pd.DataFrame()

    return pd.DataFrame()


def normalize_columns(df):
    """Normalize column names and common naming variations."""

    df = df.copy()

    # Remove accidental spaces around column names.
    df.columns = df.columns.astype(str).str.strip()

    # Map common backend naming conventions to dashboard labels.
    aliases = {
        "screen_name": "Screen Name",
        "screen name": "Screen Name",
        "movie_title": "Movie Title",
        "movie title": "Movie Title",
        "movie_name": "Movie Title",
        "movie name": "Movie Title",
        "language": "Language",
        "duration": "Duration",
    }

    rename_map = {}

    for column in df.columns:
        normalized = column.strip().lower()
        if normalized in aliases:
            rename_map[column] = aliases[normalized]

    return df.rename(columns=rename_map)


def theatreadmin_dashboard_page():
    theatre_id = st.session_state.get("theatre_id")

    if not theatre_id:
        st.warning("Theatre ID not found. Please select My Theatre first.")
        st.stop()

    st.title("Theatre Name")
    st.subheader("Theatre City")
    st.divider()

    # --------------------------------------------------
    # Dashboard metrics
    # --------------------------------------------------

    col1, col2, col3, col4, col5 = st.columns(5)

    ok, data, error = api(
        method="GET",
        path="/get_analytics_superadmin/total_movies",
    )

    with col1:
        if ok:
            st.metric(label="Total Movies", value=data)
        else:
            st.metric(label="Total Movies", value="—")

    ok, data, error = api(
        method="GET",
        path="/get_analytics_superadmin/total_screens",
        params={"admin_id": theatre_id},
    )

    with col2:
        if ok:
            st.metric(label="Total Screens", value=data)
        else:
            st.metric(label="Total Screens", value="—")

    ok, data, error = api(
        method="GET",
        path="/get_analytics_superadmin/total_shows",
        params={"admin_id": theatre_id},
    )

    with col3:
        if ok:
            st.metric(label="Total Shows", value=data)
        else:
            st.metric(label="Total Shows", value="—")

    ok, data, error = api(
        method="GET",
        path="/get_analytics_superadmin/theatre_name",
        params={"admin_id": theatre_id},
    )

    with col4:
        if ok:
            st.metric(label="Your Theatre", value=data)
        else:
            st.metric(label="Your Theatre", value="—")

    ok, data, error = api(
        method="GET",
        path="/get_analytics_superadmin/city_name",
        params={"admin_id": theatre_id},
    )

    with col5:
        if ok:
            st.metric(label="Your City", value=data)
        else:
            st.metric(label="Your City", value="—")

    st.divider()

    # --------------------------------------------------
    # Movie list and city list
    # --------------------------------------------------

    table_col1, table_col2 = st.columns(2)

    ok_movies, movie_data, movie_error = api(
        "GET",
        "/get_analytics/get_movies_list",
    )

    with table_col1:
        st.subheader("Movie List")

        if ok_movies:
            df_movies = response_to_dataframe(movie_data)

            if not df_movies.empty:
                if (
                    "Movie Name" not in df_movies.columns
                    and len(df_movies.columns) == 1
                ):
                    df_movies.columns = ["Movie Name"]

                st.dataframe(df_movies, width="stretch")
            else:
                st.info("No movies found.")
        else:
            st.error(
                f"Could not load movies: "
                f"{movie_error or 'Unknown error'}"
            )

    ok_cities, city_data, city_error = api(
        "GET",
        "/get_analytics_superadmin/get_cities_list",
    )

    with table_col2:
        st.subheader("City List")

        if ok_cities:
            df_cities = response_to_dataframe(city_data)

            if not df_cities.empty:
                if (
                    "City Name" not in df_cities.columns
                    and len(df_cities.columns) == 1
                ):
                    df_cities.columns = ["City Name"]

                st.dataframe(df_cities, width="stretch")
            else:
                st.info("No cities found.")
        else:
            st.error(
                f"Could not load cities: "
                f"{city_error or 'Unknown error'}"
            )

    st.divider()

    # --------------------------------------------------
    # Screens and scheduled movies
    # --------------------------------------------------

    ok_shows, show_data, show_error = api(
        "GET",
        "/get_analytics_superadmin/get_screen_shows_list",
        params={"admin_id": theatre_id},
    )

    st.subheader("Screens & Scheduled Movies")

    if ok_shows:
        df_shows = response_to_dataframe(show_data)
        df_shows = normalize_columns(df_shows)

        required_columns = [
            "Screen Name",
            "Movie Title",
            "Language",
            "Duration",
        ]

        if df_shows.empty:
            st.info("No scheduled shows found.")

        else:
            # Report missing columns instead of crashing.
            missing_columns = [
                column
                for column in required_columns
                if column not in df_shows.columns
            ]

            if missing_columns:
                st.warning(
                    "The API response is missing expected columns: "
                    + ", ".join(missing_columns)
                )

                st.write(
                    "Columns returned by API:",
                    df_shows.columns.tolist(),
                )

                st.write("Raw scheduled-show data:")
                st.dataframe(df_shows, width="stretch")

            else:
                df_shows = df_shows[required_columns]
                st.dataframe(df_shows, width="stretch")

    else:
        st.error(
            f"Unable to load scheduled shows: "
            f"{show_error or 'Unknown error'}"
        )
