
import streamlit as st
from datetime import date, datetime

from common import api


def theatres_page():
    """Display theatres and show timings for the selected city and movie."""

    st.subheader("Choose Your Theatre")
    st.caption("Select a theatre and show timing to continue to seat selection.")

    city_id = st.session_state.get("booking_city_id")
    movie_id = st.session_state.get("booking_movie_id")

    if city_id is None:
        st.warning("Please select a city first.")
        if st.button("Back to Cities"):
            st.session_state.booking_step = "cities"
            st.rerun()
        return

    if movie_id is None:
        st.warning("Please select a movie first.")
        if st.button("Back to Movies"):
            st.session_state.booking_step = "movies"
            st.rerun()
        return

    # Fetch movie details.
    movies_ok, movies, status_code = api("GET", "/movies/")

    if not movies_ok:
        st.error(f"Unable to load movies: {movies}")
        st.caption(f"HTTP status: {status_code}")
        return

    movie = next(
        (
            item for item in movies
            if str(item.get("movie_id")) == str(movie_id)
        ),
        None,
    )

    if movie is None:
        st.error("The selected movie could not be found.")
        return

    st.markdown(f"### {movie['movie_title']}")

    selected_date = st.date_input(
        "Select Date",
        value=date.today(),
        min_value=date.today(),
        key="booking_theatre_date",
    )

    # Fetch active theatres for the selected city.
    theatres_ok, theatres, status_code = api(
        "GET",
        "/theatres/public",
        params={"city_id": city_id},
    )

    if not theatres_ok:
        st.error(f"Unable to load theatres: {theatres}")
        st.caption(f"HTTP status: {status_code}")
        return

    if not theatres:
        st.info("No active theatres were found in this city.")
        return

    # Fetch scheduled shows.
   # Fetch public shows for the selected movie and date.
    shows_ok, shows, status_code = api(
        "GET",
        "/public/shows/",
        params={
            "movie_id": movie_id,
            "show_date": selected_date.isoformat(),
        },
    )

    if not shows_ok:
        st.error(f"Unable to load show timings: {shows}")
        st.caption(f"HTTP status: {status_code}")
        return

    selected_theatres = []

    for theatre in theatres:
        theatre_id = theatre["theatre_id"]

        shows_ok, shows, status_code = api(
            "GET",
            "/public/shows/",
            params={
                "theatre_id": theatre_id,
                "movie_id": movie_id,
                "show_date": selected_date.isoformat(),
            },
        )

        if not shows_ok:
            st.error(f"Unable to load show timings: {shows}")
            st.caption(f"HTTP status: {status_code}")
            return

        upcoming_shows = []

        for show in shows:
            try:
                start_datetime = datetime.fromisoformat(show["show_start_time"])
            except (ValueError, TypeError, KeyError):
                continue

            now = (
                datetime.now(start_datetime.tzinfo)
                if start_datetime.tzinfo
                else datetime.now()
            )

            if start_datetime > now:
                upcoming_shows.append(show)

        if upcoming_shows:
            selected_theatres.append((theatre, upcoming_shows))

    # After the loop, not inside it
    if not selected_theatres:
        st.info("No upcoming shows are available for this movie on the selected date in this city.")
        return

    # Display theatres and their available show timings.
    for theatre, theatre_shows in selected_theatres:
        theatre_id = theatre["theatre_id"]

        with st.container(border=True):
            st.subheader(theatre.get("name", "Theatre"))

            if theatre.get("address"):
                st.caption(theatre["address"])

            st.write("**Available Show Timings**")

            sorted_shows = sorted(
                theatre_shows,
                key=lambda show: show["show_start_time"],
            )

            columns = st.columns(min(len(sorted_shows), 4))

            for index, show in enumerate(sorted_shows):
                with columns[index % len(columns)]:
                    try:
                        start_datetime = datetime.fromisoformat(
                            show["show_start_time"]
                        )
                        start_label = start_datetime.strftime("%I:%M %p")
                    except (ValueError, TypeError, KeyError):
                        start_label = show.get("show_start_time", "N/A")

                    language = show.get("show_language", "")
                    show_format = show.get("show_format", "")

                    # Language and format shown under the time (optional).
                    details = " · ".join(
                        part for part in (language, show_format) if part
                    )

                    # The timing itself is the button.
                    if st.button(
                        start_label,
                        key=f"select_show_{show['show_id']}",
                        use_container_width=True,
                        help=details or None,
                    ):
                        st.session_state.booking_theatre_id = theatre_id
                        st.session_state.booking_date = selected_date
                        st.session_state.booking_show_id = show["show_id"]
                        st.session_state.booking_screen_id = show["screen_id"]
                        st.session_state.booking_seat_ids = []
                        st.session_state.booking_step = "seats"
                        st.rerun()

                    if details:
                        st.caption(details)