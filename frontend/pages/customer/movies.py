import streamlit as st

from common import api, matches

CARDS_PER_ROW = 4
NO_GENRE = "Uncategorised"


def format_duration(value) -> str:
    try:
        hours, minutes, _ = str(value).split(":")
        return f"{int(hours)}h {int(minutes):02d}m"
    except (ValueError, TypeError):
        return "-"


def show_poster(url):
    if not url:
        st.caption("No poster")
        return
    try:
        st.image(url, width="stretch")
    except Exception:
        st.caption("Poster unavailable")


@st.dialog("Movie details", width="large")
def movie_details_dialog(movie):
    poster_col, info_col = st.columns([1, 2])
    with poster_col:
        show_poster(movie.get("movie_poster_url"))
    with info_col:
        st.markdown(f"## {movie['movie_title']}")
        st.caption(" · ".join(p for p in (
            movie.get("movie_genre"),
            str(movie["movie_language"]).title(),
            format_duration(movie.get("movie_duration")),
            f" {movie['movie_rating']}/10",
        ) if p))
        st.write(movie["movie_description"])

        if st.button("Book show", type="primary",
                     key=f"book_show_{movie['movie_id']}", use_container_width=True):
            st.session_state["booking_movie_id"] = movie["movie_id"]
            st.session_state["booking_step"] = "theatres"
            st.rerun()


def movie_card(movie, key_prefix):
    with st.container(border=True):
        show_poster(movie.get("movie_poster_url"))
        st.markdown(f"**{movie['movie_title']}**")
        st.caption(f"{movie.get('movie_genre') or NO_GENRE} · {str(movie['movie_language']).title()}")
        st.caption(f"{movie['movie_rating']}/10 · {format_duration(movie.get('movie_duration'))}")
        if st.button("View details", key=f"{key_prefix}_view_{movie['movie_id']}", use_container_width=True):
            movie_details_dialog(movie)


def card_grid(movies, key_prefix):
    for start in range(0, len(movies), CARDS_PER_ROW):
        columns = st.columns(CARDS_PER_ROW)
        for column, movie in zip(columns, movies[start:start + CARDS_PER_ROW]):
            with column:
                movie_card(movie, key_prefix)


def movies_page():
    city_id = st.session_state.get("booking_city_id")
    city_name = st.session_state.get("booking_city_name", "your city")

    title_col, change_col = st.columns([4, 1])
    title_col.subheader(f"Movies in {city_name}")
    if change_col.button("Change city", use_container_width=True):
        st.session_state["booking_step"] = "cities"
        st.rerun()

    ok, movies, _ = api("GET", "/public/movies/", params={"city_id": city_id})
    if not ok:
        st.error(movies)
        return
    if not movies:
        st.info(f"No movies with upcoming shows in {city_name} right now.")
        return

    genres = sorted({m.get("movie_genre") for m in movies if m.get("movie_genre")})
    languages = sorted({str(m["movie_language"]) for m in movies})

    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    search = c1.text_input("Search", placeholder="Search by title...", key="customer_movie_search")
    genre = c2.selectbox("Genre", ["All genres"] + genres, key="customer_movie_genre")
    language = c3.selectbox("Language", ["All languages"] + languages, key="customer_movie_language")
    group_by = c4.selectbox("Group by", ["None", "Genre", "Language"], key="customer_movie_group")

    filtered = [
        m for m in movies
        if matches(search, m["movie_title"])
        and (genre == "All genres" or m.get("movie_genre") == genre)
        and (language == "All languages" or str(m["movie_language"]) == language)
    ]
    if not filtered:
        st.info("No movies match your filters.")
        return

    if group_by == "None":
        card_grid(filtered, "all")
        return

    groups = {}
    for m in filtered:
        key = (m.get("movie_genre") or NO_GENRE) if group_by == "Genre" else str(m["movie_language"]).title()
        groups.setdefault(key, []).append(m)

    for name in sorted(groups):
        st.markdown(f"### {name}")
        card_grid(groups[name], f"grp_{name}")