
import streamlit as st

from common import api


def shows_page():
    st.subheader("Select a Show")
    st.caption("Choose a show timing to continue to seat selection.")

    movie_id = st.session_state.get("booking_movie_id")

    if movie_id is None:
        st.warning("Please select a movie first.")
        return

    # Fetch shows for the selected movie.
    # This assumes your API supports GET /shows?movie_id=<id>.
    ok, result, status_code = api(
        "GET",
        "/shows",
        params={"movie_id": movie_id},
    )

    if not ok:
        st.error(f"Unable to load shows: {result}")
        st.caption(f"HTTP status: {status_code}")
        return

    if not result:
        st.info("No shows are available for this movie.")
        return

    for show in result:
        show_id = show["show_id"]

        with st.container(border=True):
            st.write(f"**Show ID:** {show_id}")
            st.write(f"Start: {show.get('show_start_time', 'N/A')}")
            st.write(f"End: {show.get('show_end_time', 'N/A')}")
            st.write(f"Language: {show.get('show_language', 'N/A')}")
            st.write(f"Format: {show.get('show_format', 'N/A')}")

            if st.button(
                "Select this show",
                key=f"select_show_{show_id}",
                width=True,
            ):
                st.session_state["booking_show_id"] = show_id
                st.session_state["booking_seat_ids"] = []
                st.session_state["booking_step"] = "seats"
                st.rerun()
