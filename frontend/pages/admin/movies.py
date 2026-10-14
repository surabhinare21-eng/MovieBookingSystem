import streamlit as st

from common import api, flash


LANGUAGES = ["ENGLISH", "HINDI", "MARATHI"]
MOVIE_STATUSES = ["ACTIVE", "INACTIVE"]
DURATION_MINUTES = 59


def format_duration(hours, minutes):
    """Convert hours and minutes into HH:MM:SS."""
    return f"{int(hours):02d}:{int(minutes):02d}:00"


def parse_duration(duration):
    """Convert HH:MM:SS into hours and minutes."""
    try:
        hours, minutes, _ = str(duration).split(":")
        return int(hours), int(minutes)
    except (ValueError, AttributeError, TypeError):
        return 2, 30


@st.dialog("Edit Movie", width="large")
def edit_movie_dialog(movie):
    """Display a popup for editing an existing movie."""

    movie_id = movie["movie_id"]

    st.caption(f"Editing: {movie['movie_title']}")

    current_hours, current_minutes = parse_duration(
        movie.get("movie_duration", "02:30:00")
    )

    # Prevent invalid selectbox values if existing data is unusual.
    current_language = movie.get("movie_language", LANGUAGES[0])
    if current_language not in LANGUAGES:
        current_language = LANGUAGES[0]

    current_status = movie.get("movie_status", MOVIE_STATUSES[0])
    if current_status not in MOVIE_STATUSES:
        current_status = MOVIE_STATUSES[0]

    with st.form(f"edit_movie_form_{movie_id}"):
        title = st.text_input(
            "Title",
            value=movie["movie_title"],
        )

        description = st.text_area(
            "Description",
            value=movie["movie_description"],
        )

        language = st.selectbox(
            "Language",
            LANGUAGES,
            index=LANGUAGES.index(current_language),
        )

        movie_status = st.selectbox(
            "Status",
            MOVIE_STATUSES,
            index=MOVIE_STATUSES.index(current_status),
        )

        poster_url = st.text_input(
            "Poster URL",
            value=movie["movie_poster_url"],
        )

        rating = st.number_input(
            "Rating",
            min_value=0,
            max_value=10,
            value=int(movie["movie_rating"]),
            step=1,
        )

        duration_hours = st.number_input(
            "Duration (hours)",
            min_value=0,
            max_value=10,
            value=max(0, min(10, current_hours)),
            step=1,
        )

        duration_minutes = st.number_input(
            "Duration (minutes)",
            min_value=0,
            max_value=DURATION_MINUTES,
            value=max(0, min(DURATION_MINUTES, current_minutes)),
            step=1,
        )

        save_changes = st.form_submit_button(
            "Save Changes",
            type="primary",
            use_container_width=True,
        )

    if save_changes:
        if (
            not title.strip()
            or not description.strip()
            or not poster_url.strip()
        ):
            st.error(
                "Title, description, and poster URL are required."
            )
            return

        if int(duration_hours) == 0 and int(duration_minutes) == 0:
            st.error("Movie duration must be greater than zero.")
            return

        payload = {
            "movie_title": title.strip(),
            "movie_description": description.strip(),
            "movie_status": movie_status,
            "movie_language": language,
            "movie_poster_url": poster_url.strip(),
            "movie_rating": int(rating),
            "movie_duration": format_duration(
                duration_hours,
                duration_minutes,
            ),
        }

        ok, data, _ = api(
            "PATCH",
            f"/movies/{movie_id}",
            json=payload,
        )

        if ok:
            flash("Movie updated successfully.")
            st.rerun()
        else:
            st.error(data)


def movies_page():
    """Display the movie creation form and catalogue."""

    st.subheader("Movie Catalogue")
    st.caption(
        "Create and manage movies available for show scheduling."
    )

    # --------------------------------------------------
    # ADD MOVIE
    # --------------------------------------------------
    with st.expander("Add a movie", expanded=True):
        with st.form("create_movie_form", clear_on_submit=True):
            title = st.text_input("Title")
            description = st.text_area("Description")

            language = st.selectbox(
                "Language",
                LANGUAGES,
            )

            movie_status = st.selectbox(
                "Status",
                MOVIE_STATUSES,
            )

            poster_url = st.text_input("Poster URL")

            rating = st.number_input(
                "Rating",
                min_value=0,
                max_value=10,
                value=0,
                step=1,
            )

            duration_hours = st.number_input(
                "Duration (hours)",
                min_value=0,
                max_value=10,
                value=2,
                step=1,
            )

            duration_minutes = st.number_input(
                "Duration (minutes)",
                min_value=0,
                max_value=DURATION_MINUTES,
                value=30,
                step=1,
            )

            submitted = st.form_submit_button(
                "Add Movie",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            if (
                not title.strip()
                or not description.strip()
                or not poster_url.strip()
            ):
                st.error(
                    "Title, description, and poster URL are required."
                )

            elif int(duration_hours) == 0 and int(duration_minutes) == 0:
                st.error("Movie duration must be greater than zero.")

            else:
                payload = {
                    "movie_title": title.strip(),
                    "movie_description": description.strip(),
                    "movie_status": movie_status,
                    "movie_language": language,
                    "movie_poster_url": poster_url.strip(),
                    "movie_rating": int(rating),
                    "movie_duration": format_duration(
                        duration_hours,
                        duration_minutes,
                    ),
                }

                ok, data, _ = api(
                    "POST",
                    "/movies/",
                    json=payload,
                )

                if ok:
                    flash(
                        f"Movie '{data['movie_title']}' "
                        "added successfully."
                    )
                    st.rerun()
                else:
                    st.error(data)

    st.divider()

    # --------------------------------------------------
    # ALL MOVIES
    # --------------------------------------------------
    st.subheader("All Movies")

    ok, movies, _ = api("GET", "/movies/")

    if not ok:
        st.error(movies)
        return

    if not movies:
        st.info(
            "No movies available. Add a movie using the form above."
        )
        return

    search_query = st.text_input(
        "Search movies",
        placeholder="Search by title, ID, language, or status...",
        key="movie_catalogue_search",
    ).strip().lower()

    filtered_movies = [
        movie
        for movie in movies
        if (
            search_query in str(movie["movie_id"]).lower()
            or search_query in movie["movie_title"].lower()
            or search_query in movie["movie_language"].lower()
            or search_query in movie["movie_status"].lower()
        )
    ]

    if not filtered_movies:
        st.info("No movies match your search.")
        return

    # Table header.
    column_widths = [0.6, 2.2, 1.1, 1.1, 0.7, 1.2, 1.0, 1.0]

    headers = st.columns(column_widths)

    for column, heading in zip(
        headers,
        [
            "ID",
            "Title",
            "Language",
            "Status",
            "Rating",
            "Duration",
            "Actions",
        ],
    ):
        column.markdown(f"**{heading}**")

    st.divider()

    # Movie rows.
    for movie in filtered_movies:
        movie_id = movie["movie_id"]

        columns = st.columns(column_widths)

        columns[0].write(movie_id)
        columns[1].write(movie["movie_title"])
        columns[2].write(movie["movie_language"])
        columns[3].write(movie["movie_status"])
        columns[4].write(movie["movie_rating"])
        columns[5].write(movie.get("movie_duration", "N/A"))

        with columns[6]:
            if st.button(
                "Edit",
                key=f"edit_movie_{movie_id}",
                use_container_width=True,
            ):
                edit_movie_dialog(movie)
        with columns[7]:
            if st.button(
                "Delete",
                key=f"delete_movie_{movie_id}",
                use_container_width=True,
            ):
                ok, data, _ = api(
                    "DELETE",
                    f"/movies/{movie_id}",
                )

                if ok:
                    flash(
                        f"Movie '{movie['movie_title']}' "
                        "deleted successfully."
                    )
                    st.rerun()
                else:
                    st.error(data)

        st.divider()