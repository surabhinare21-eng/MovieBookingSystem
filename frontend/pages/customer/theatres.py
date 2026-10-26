
import streamlit as st
from datetime import date, datetime, timedelta

from common import api


def theatres_page():
    """Display available dates, theatres, and show timings."""

    st.subheader("Choose Your Theatre")
    st.caption("Select a date and show timing to continue to seat selection.")

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

    # Fetch active theatres in the selected city.
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

    # Find dates with upcoming shows over the next 14 days.
    today = date.today()
    available_shows_by_date = {}

    for day_offset in range(14):
        show_date = today + timedelta(days=day_offset)
        shows_for_date = []

        for theatre in theatres:
            theatre_id = theatre["theatre_id"]

            shows_ok, shows, status_code = api(
                "GET",
                "/public/shows/",
                params={
                    "theatre_id": theatre_id,
                    "movie_id": movie_id,
                    "show_date": show_date.isoformat(),
                },
            )

            if not shows_ok:
                st.error(f"Unable to load show timings: {shows}")
                st.caption(f"HTTP status: {status_code}")
                return

            upcoming_shows = []

            for show in shows:
                try:
                    start_datetime = datetime.fromisoformat(
                        show["show_start_time"]
                    )
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
                shows_for_date.append((theatre, upcoming_shows))

        if shows_for_date:
            available_shows_by_date[show_date] = shows_for_date

    # Only dates with upcoming shows are selectable.
    available_dates = list(available_shows_by_date.keys())

    if not available_dates:
        st.info(
            "No upcoming shows are available for this movie "
            "in this city over the next 14 days."
        )
        return

    st.write("**Select a date**")

    # Use one consistent session-state key.
    selected_date = st.session_state.get("selected_booking_date")

    if selected_date not in available_dates:
        selected_date = available_dates[0]
        st.session_state.selected_booking_date = selected_date

    # Display the available dates as buttons.
    date_columns = st.columns(min(len(available_dates), 7))

    for index, show_date in enumerate(available_dates):
        with date_columns[index % len(date_columns)]:
            if show_date == today:
                day_label = "TODAY"
            elif show_date == today + timedelta(days=1):
                day_label = "TOMORROW"
            else:
                day_label = show_date.strftime("%a").upper()

            date_label = (
                f"{day_label}\n"
                f"{show_date.strftime('%d %b')}"
            )

            if st.button(
                date_label,
                key=f"booking_date_{show_date.isoformat()}",
                type=(
                    "primary"
                    if show_date == selected_date
                    else "secondary"
                ),
                use_container_width=True,
            ):
                st.session_state.selected_booking_date = show_date
                st.rerun()

    # Retrieve theatres and shows for the selected date.
    selected_theatres = available_shows_by_date[selected_date]

    if not selected_theatres:
        st.info("No upcoming shows are available on this date.")
        return

    # Display each theatre once, with its upcoming show timings.
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
                        start_label = show.get(
                            "show_start_time", "N/A"
                        )

                    language = show.get("show_language", "")
                    show_format = show.get("show_format", "")

                    details = " · ".join(
                        part
                        for part in (language, show_format)
                        if part
                    )

                    if st.button(
                        start_label,
                        key=f"select_show_{show['show_id']}",
                        width=True,
                        help=details or None,
                    ):
                        # Save the selected booking context.
                        st.session_state.booking_theatre_id = theatre_id
                        st.session_state.booking_theatre_name = (
                            theatre.get("name", "Selected Theatre")
                        )
                        st.session_state.booking_movie_title = (
                            movie.get("movie_title", "Selected Movie")
                        )
                        st.session_state.booking_date = selected_date
                        st.session_state.booking_show_id = show["show_id"]
                        st.session_state.booking_screen_id = show["screen_id"]
                        st.session_state.booking_seat_ids = []

                        st.session_state.pop(
                            "booking_requested_count", None
                        )
                        st.session_state.booking_show_price_dialog = False
                        st.session_state.booking_step = "seats"
                        st.rerun()

                    if details:
                        st.caption(details)
