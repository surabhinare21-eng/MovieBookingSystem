
import streamlit as st

from pages.customer.theatres import theatres_page


def demo_theatre_page():
    st.title("Theatre Page — Demo Testing")
    st.caption(
        "Temporary testing page. Enter IDs that already exist "
        "in your backend database."
    )

    city_id = st.number_input(
        "City ID",
        min_value=1,
        step=1,
        key="demo_city_id",
    )

    movie_id = st.number_input(
        "Movie ID",
        min_value=1,
        step=1,
        key="demo_movie_id",
    )

    if st.button("Load Theatres", type="primary"):
        st.session_state["booking_city_id"] = int(city_id)
        st.session_state["booking_movie_id"] = int(movie_id)
        st.session_state["booking_step"] = "theatres"
        st.session_state["demo_show_theatres"] = True

    if st.session_state.get("demo_show_theatres", False):
        if st.button("Back to Demo Inputs"):
            st.session_state["demo_show_theatres"] = False
            st.rerun()

        theatres_page()

