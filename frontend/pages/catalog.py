
import streamlit as st

from common import api, flash, show_table


# def movies_page():
#     st.subheader("Movie Catalogue")
#     st.caption("Create and manage movies available for show scheduling.")

#     # Add a movie
#     with st.expander("Add a movie", expanded=True):
#         with st.form("create_movie_form", clear_on_submit=True):
#             title = st.text_input("Title")
#             description = st.text_area("Description")

#             language = st.selectbox(
#                 "Language",
#                 ["ENGLISH", "HINDI", "MARATHI"],
#             )

#             movie_status = st.selectbox(
#                 "Status",
#                 ["ACTIVE", "INACTIVE"],
#             )

#             poster_url = st.text_input("Poster URL")

#             rating = st.number_input(
#                 "Rating",
#                 min_value=0,
#                 max_value=10,
#                 step=1,
#             )

#             submitted = st.form_submit_button(
#                 "Add movie",
#                 type="primary",
#             )

#         if submitted:
#             if (
#                 not title.strip()
#                 or not description.strip()
#                 or not poster_url.strip()
#             ):
#                 st.error(
#                     "Title, description, and poster URL are required."
#                 )
#             else:
#                 ok, data, _ = api(
#                     "POST",
#                     "/movies/",
#                     json={
#                         "movie_title": title.strip(),
#                         "movie_description": description.strip(),
#                         "movie_status": movie_status,
#                         "movie_language": language,
#                         "movie_poster_url": poster_url.strip(),
#                         "movie_rating": int(rating),
#                     },
#                 )

#                 if ok:
#                     flash(
#                         f"Movie '{data['movie_title']}' added successfully."
#                     )
#                     st.rerun()
#                 else:
#                     st.error(data)

#     # Display movies
#     st.divider()
#     st.subheader("Movies")

#     ok, movies, _ = api("GET", "/movies/")

#     if not ok:
#         st.error(movies)
#         return

#     if not movies:
#         st.info("No movies have been added yet.")
#         return

#     show_table(
#         [
#             {
#                 "Movie ID": movie["movie_id"],
#                 "Title": movie["movie_title"],
#                 "Language": movie["movie_language"],
#                 "Status": movie["movie_status"],
#                 "Rating": movie["movie_rating"],
#             }
#             for movie in movies
#         ],
#         {
#             "Movie ID": "Movie ID",
#             "Title": "Title",
#             "Language": "Language",
#             "Status": "Status",
#             "Rating": "Rating",
#         },
#     )

#     # Select a movie to manage
#     labels = {
#         movie["movie_id"]: movie["movie_title"]
#         for movie in movies
#     }

#     selected_id = st.selectbox(
#         "Manage movie",
#         list(labels),
#         format_func=lambda movie_id: (
#             f"{labels[movie_id]} (ID {movie_id})"
#         ),
#         key="manage_movie_id",
#     )

#     selected = next(
#         movie for movie in movies
#         if movie["movie_id"] == selected_id
#     )

#     # Update movie
#     with st.form("update_movie_form"):
#         title = st.text_input(
#             "Title",
#             value=selected["movie_title"],
#         )

#         description = st.text_area(
#             "Description",
#             value=selected["movie_description"],
#         )

#         languages = ["ENGLISH", "HINDI", "MARATHI"]

#         language = st.selectbox(
#             "Language",
#             languages,
#             index=languages.index(selected["movie_language"]),
#         )

#         statuses = ["ACTIVE", "INACTIVE"]

#         movie_status = st.selectbox(
#             "Status",
#             statuses,
#             index=statuses.index(selected["movie_status"]),
#         )

#         poster_url = st.text_input(
#             "Poster URL",
#             value=selected["movie_poster_url"],
#         )

#         rating = st.number_input(
#             "Rating",
#             min_value=0,
#             max_value=10,
#             value=selected["movie_rating"],
#             step=1,
#         )

#         update_submitted = st.form_submit_button("Save movie")

#     if update_submitted:
#         ok, data, _ = api(
#             "PATCH",
#             f"/movies/{selected_id}",
#             json={
#                 "movie_title": title.strip(),
#                 "movie_description": description.strip(),
#                 "movie_status": movie_status,
#                 "movie_language": language,
#                 "movie_poster_url": poster_url.strip(),
#                 "movie_rating": int(rating),
#             },
#         )

#         if ok:
#             flash("Movie updated successfully.")
#             st.rerun()
#         else:
#             st.error(data)

#     # Delete movie
#     if st.button("Delete movie", key="delete_movie"):
#         ok, data, _ = api(
#             "DELETE",
#             f"/movies/{selected_id}",
#         )

#         if ok:
#             flash("Movie deleted successfully.")
#             st.rerun()
#         else:
#             st.error(data)


def movies_page():
    st.subheader("Movie Catalogue")
    st.caption("Create and manage movies available for show scheduling.")


    with st.expander("Add a movie", expanded=True):
        with st.form("create_movie_form", clear_on_submit=True):
            title = st.text_input("Title")
            description = st.text_area("Description")

            language = st.selectbox(
                "Language",
                ["ENGLISH", "HINDI", "MARATHI"],
            )

            movie_status = st.selectbox(
                "Status",
                ["ACTIVE", "INACTIVE"],
            )

            poster_url = st.text_input("Poster URL")

            rating = st.number_input(
                "Rating",
                min_value=0,
                max_value=10,
                step=1,
            )

            submitted = st.form_submit_button(
                "Add movie",
                type="primary",
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
            else:
                ok, data, _ = api(
                    "POST",
                    "/movies/",
                    json={
                        "movie_title": title.strip(),
                        "movie_description": description.strip(),
                        "movie_status": movie_status,
                        "movie_language": language,
                        "movie_poster_url": poster_url.strip(),
                        "movie_rating": int(rating),
                    },
                )

                if ok:
                    flash(
                        f"Movie '{data['movie_title']}' added successfully."
                    )
                    st.rerun()
                else:
                    st.error(data)

    st.divider()

    if st.button("Manage Movies", type="primary"):
        st.session_state.movie_page = "manage"
        st.rerun()

    
    st.divider()
    st.subheader("Movies")

    ok, movies, _ = api("GET", "/movies/")


    search_query = st.text_input(
        "Search movies",
        placeholder="Search by title, ID, language, or status...",
        key="movie_catalogue_search",
    ).strip().lower()

    filtered_movies = [
        movie for movie in movies
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

    show_table(
        [
            {
                "Movie ID": movie["movie_id"],
                "Title": movie["movie_title"],
                "Language": movie["movie_language"],
                "Status": movie["movie_status"],
                "Rating": movie["movie_rating"],
            }
            for movie in filtered_movies
        ],
        {
            "Movie ID": "Movie ID",
            "Title": "Title",
            "Language": "Language",
            "Status": "Status",
            "Rating": "Rating",
        },
    )


   

def manage_movies_page():
    st.subheader("Manage Movies")
    st.caption("Select a movie to edit its details or delete it.")

    ok, movies, _ = api("GET", "/movies/")

    if not ok:
        st.error(movies)
        return

    if not movies:
        st.info("No movies available to manage.")

        if st.button("Back to Movies"):
            st.session_state.movie_page = "list"
            st.rerun()

        return

    labels = {
        movie["movie_id"]: movie["movie_title"]
        for movie in movies
    }

    selected_id = st.selectbox(
        "Select a movie",
        list(labels),
        format_func=lambda movie_id: (
            f"{labels[movie_id]} (ID {movie_id})"
        ),
        key="manage_movie_id",
    )

    selected = next(
        movie for movie in movies
        if movie["movie_id"] == selected_id
    )

    st.divider()
    st.caption(f"Editing: {selected['movie_title']}")

    with st.form("update_movie_form"):
        title = st.text_input(
            "Title",
            value=selected["movie_title"],
            key=f"movie_title_{selected_id}",
        )

        description = st.text_area(
            "Description",
            value=selected["movie_description"],
            key=f"movie_description_{selected_id}",
        )

        languages = ["ENGLISH", "HINDI", "MARATHI"]

        language = st.selectbox(
            "Language",
            languages,
            index=languages.index(selected["movie_language"]),
            key=f"movie_language_{selected_id}",
        )

        statuses = ["ACTIVE", "INACTIVE"]

        movie_status = st.selectbox(
            "Status",
            statuses,
            index=statuses.index(selected["movie_status"]),
            key=f"movie_status_{selected_id}",
        )

        poster_url = st.text_input(
            "Poster URL",
            value=selected["movie_poster_url"],
            key=f"movie_poster_{selected_id}",
        )

        rating = st.number_input(
            "Rating",
            min_value=0,
            max_value=10,
            value=selected["movie_rating"],
            step=1,
            key=f"movie_rating_{selected_id}",
        )

        update_submitted = st.form_submit_button(
            "Save Changes",
            type="primary",
        )

    if update_submitted:
        if (
            not title.strip()
            or not description.strip()
            or not poster_url.strip()
        ):
            st.error(
                "Title, description, and poster URL are required."
            )
        else:
            ok, data, _ = api(
                "PATCH",
                f"/movies/{selected_id}",
                json={
                    "movie_title": title.strip(),
                    "movie_description": description.strip(),
                    "movie_status": movie_status,
                    "movie_language": language,
                    "movie_poster_url": poster_url.strip(),
                    "movie_rating": int(rating),
                },
            )

            if ok:
                flash("Movie updated successfully.")
                st.session_state.movie_page = "list"
                st.rerun()
            else:
                st.error(data)

    st.divider()

    if st.button("Delete Movie", key="delete_movie"):
        ok, data, _ = api(
            "DELETE",
            f"/movies/{selected_id}",
        )

        if ok:
            flash("Movie deleted successfully.")
            st.session_state.movie_page = "list"
            st.rerun()
        else:
            st.error(data)

    if st.button("Back to Movies"):
        st.session_state.movie_page = "list"
        st.rerun()
