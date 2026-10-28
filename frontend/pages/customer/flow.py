import streamlit as st

from pages.customer.cities import cities_page
from pages.customer.movies import movies_page
from pages.customer.theatres import theatres_page
from pages.customer.seats import seats_page
from pages.customer.payment import payments_page
from pages.customer.my_bookings import my_bookings_page


def customer_flow():
    if st.session_state.get("customer_view") == "my_bookings":
        my_bookings_page()
        return

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
        seats_page()
    elif step == "payment":
        payments_page()