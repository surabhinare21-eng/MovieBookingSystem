
from datetime import datetime, timedelta

import streamlit as st

from common import (
    api,
    active_text,
    flash,
    show_table,
)


def shows_page():
    st.subheader("Show Scheduling")
    st.caption("Schedule and manage movie shows for your theatre.")

    # Fetch movies and screens.
    movies_ok, movies, _ = api("GET", "/movies/")
    screens_ok, screens, _ = api("GET", "/screens/")

    if not movies_ok:
        st.error(f"Unable to load movies: {movies}")
        return

    if not screens_ok:
        st.error(f"Unable to load screens: {screens}")
        return

    if not movies:
        st.warning("No movies are available. Add a movie before scheduling a show.")
        return

    if not screens:
        st.warning("No screens are available. Create a screen before scheduling a show.")
        return

    # Display movie titles while retaining movie IDs.
    movie_options = {
        f"{movie['movie_title']} (ID: {movie['movie_id']})": movie
        for movie in movies
    }

    # Display screen names while retaining screen IDs.
    screen_options = {
        f"{screen['screen_name']} ({screen['seat_layout_name']})":
            screen["screen_id"]
        for screen in screens
    }

    with st.expander("Schedule a new show", expanded=True):
        with st.form("create_show_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            selected_movie_label = col1.selectbox(
                "Select Movie",
                options=list(movie_options.keys()),
            )

            selected_screen = col2.selectbox(
                "Select Screen",
                options=list(screen_options.keys()),
            )

            selected_movie = movie_options[selected_movie_label]

            # Movie duration is expected in HH:MM:SS format.
            duration_string = selected_movie.get("movie_duration", "02:30:00")

            try:
                duration_hours, duration_minutes, duration_seconds = map(
                    int,
                    duration_string.split(":"),
                )

                movie_duration = timedelta(
                    hours=duration_hours,
                    minutes=duration_minutes,
                    seconds=duration_seconds,
                )
            except (ValueError, AttributeError, TypeError):
                st.error("The selected movie has an invalid duration.")
                movie_duration = timedelta(0)

            col3, col4 = st.columns(2)

            show_language = col3.selectbox(
                "Language",
                ["English", "Hindi", "Marathi", "Other"],
            )

            show_format = col4.selectbox(
                "Format",
                ["2D", "3D", "IMAX", "4DX"],
            )

            col5, col6 = st.columns(2)

            start_date = col5.date_input(
                "Show date",
                key="show_start_date",
            )

            start_time = col6.time_input(
                "Start time",
                key="show_start_time",
            )

            start_datetime = datetime.combine(
                start_date,
                start_time,
            )

            end_datetime = start_datetime + movie_duration

            st.info(
                f"**Movie duration:** {duration_hours:02d}:"
                f"{duration_minutes:02d}:{duration_seconds:02d}"
                f"  |  **Expected end time:** "
                f"{end_datetime.strftime('%d %b %Y, %I:%M %p')}"
            )

            submitted = st.form_submit_button(
                "Schedule show",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            if movie_duration.total_seconds() <= 0:
                st.error("The selected movie must have a valid duration.")
                return

            selected_screen_id = screen_options[selected_screen]

            payload = {
                "show_start_time": start_datetime.isoformat(),
                "show_end_time": end_datetime.isoformat(),
                "show_status": True,
                "show_language": show_language,
                "show_format": show_format,
                "screen_id": selected_screen_id,
                "movie_id": selected_movie["movie_id"],
            }

            ok, data, _ = api(
                "POST",
                "/shows/",
                json=payload,
            )

            if ok:
                flash("Show scheduled successfully.")
                st.rerun()
            else:
                st.error(data)

    st.divider()
    
    header_col, button_col = st.columns([5, 1])

    with header_col:
        st.subheader("scheduled shows")

    with button_col:
        if st.button(
            "hide" if st.session_state.get("show_shows_list", False) else "view",
            key="toggle_shows_list",
        ):
            st.session_state.show_shows_list = (
                not st.session_state.get("show_shows_list", False)
            )

    if not st.session_state.get("show_shows_list", False):
        return

    # if st.button("Refresh shows", key="refresh_shows"):
    #     st.rerun()

    ok, shows, _ = api("GET", "/shows/")

    if not ok:
        st.error(shows)
        return

    if not shows:
        st.info("No shows have been scheduled yet.")
        return

    # Create lookup dictionaries for display.
    movie_names = {
        movie["movie_id"]: movie["movie_title"]
        for movie in movies
    }

    screen_names = {
        screen["screen_id"]: screen["screen_name"]
        for screen in screens
    }

    rows = []

    for show in shows:
        rows.append({
            "Show ID": show["show_id"],
            "Movie": movie_names.get(
                show["movie_id"],
                f"Unknown Movie (ID: {show['movie_id']})",
            ),
            "Screen": screen_names.get(
                show["screen_id"],
                f"Screen ID {show['screen_id']}",
            ),
            "Start Time": show["show_start_time"],
            "End Time": show["show_end_time"],
            "Language": show["show_language"],
            "Format": show["show_format"],
            "Status": active_text(show["show_status"]),
        })

    show_table(
        rows,
        {
            "Show ID": "Show ID",
            "Movie": "Movie Name",
            "Screen": "Screen",
            "Start Time": "Start Time",
            "End Time": "End Time",
            "Language": "Language",
            "Format": "Format",
            "Status": "Status",
        },
    )

    st.subheader("Manage show status")

    show_ids = [show["show_id"] for show in shows]

    selected_id = st.selectbox(
        "Select show",
        show_ids,
        key="manage_show_id",
    )

    selected_show = next(
        show for show in shows
        if show["show_id"] == selected_id
    )

    currently_active = selected_show["show_status"]

    st.write(f"Current status: {active_text(currently_active)}")

    button_label = (
        "Deactivate show"
        if currently_active
        else "Activate show"
    )

    if st.button(button_label, key="toggle_show_status"):
        ok, data, _ = api(
            "PATCH",
            f"/shows/{selected_id}/status",
            json={"show_status": not currently_active},
        )

        if ok:
            flash("Show status updated successfully.")
            st.rerun()
        else:
            st.error(data)
