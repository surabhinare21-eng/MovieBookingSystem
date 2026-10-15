import streamlit as st

from common import api, matches


def cities_page():
    st.subheader("Select your city")

    search = st.text_input(
        "Search city",
        placeholder="Search for your city...",
        key="customer_city_search",
        label_visibility="collapsed",
    )

    ok, cities, _ = api("GET", "/cities/public")
    if not ok:
        st.error(cities)
        return
    if not cities:
        st.info("No cities are available yet. Please check back soon.")
        return

    # matches() casefolds both sides, so the search is case-insensitive
    filtered = [c for c in cities if matches(search, c["name"])]
    if not filtered:
        st.warning(f'No city found for "{search.strip()}".')
        return

    per_row = 4
    for start in range(0, len(filtered), per_row):
        columns = st.columns(per_row)
        for column, city in zip(columns, filtered[start:start + per_row]):
            with column:
                with st.container(border=True):
                    st.markdown(f"{city['name']}")
                    if st.button("Select", key=f"pick_city_{city['city_id']}", width="stretch"):
                        st.session_state["booking_city_id"] = city["city_id"]
                        st.session_state["booking_city_name"] = city["name"]
                        st.session_state.pop("booking_movie_id", None)
                        st.session_state["booking_step"] = "movies"
                        st.rerun()