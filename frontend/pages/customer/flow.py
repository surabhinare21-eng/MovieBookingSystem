import streamlit as st

from pages.customer.cities import cities_page
from pages.customer.movies import movies_page
from pages.customer.theatres import theatres_page


def customer_flow():
    step = st.session_state.get("booking_step") or "cities"

    if step in ("movies", "theatres", "seats") and not st.session_state.get("booking_city_id"):
        step = "cities"
    if step in ("theatres", "seats") and not st.session_state.get("booking_movie_id"):
        step = "movies"
    st.session_state["booking_step"] = step

    if step == "cities":
        cities_page()
    elif step == "movies":
        movies_page()
    elif step == "theatres":
        if st.button("← Back to movies", key="back_to_movies"):
            st.session_state["booking_step"] = "movies"
            st.rerun()
        theatres_page()
    elif step == "seats":
        if st.button("← Back to show timings", key="back_to_theatres"):
            st.session_state["booking_step"] = "theatres"
            st.rerun()
        st.info("Seat selection is the next screen to build.")