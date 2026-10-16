import streamlit as st

from pages.customer.cities import cities_page
from pages.customer.movies import movies_page
from pages.customer.theatres import theatres_page
from pages.customer.seats import seats_page


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
        theatres_page()
    elif step == "seats":
        # This is a dedicated booking step/page; no timing-page controls are rendered here.
        seats_page()
    elif step == "payment":
        st.subheader("Payment")
        st.info("Your seats are held for five minutes. Connect the payment workflow here.")
        if st.button("Back to seat selection"):
            st.session_state["booking_step"] = "seats"
            st.rerun()
