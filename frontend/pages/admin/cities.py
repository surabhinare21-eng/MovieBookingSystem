
import streamlit as st

from api import PASSWORD_RULE

from common import (
    ROLE_LABELS,
    active_text,
    api,
    flash,
    matches,
    show_table,
    status_md,
    user_status_text,
)


def cities_page():
    st.subheader("City Management")
    st.caption("Add and manage cities available for theatres.")

    # Add a new city
    with st.expander("Add a new city", expanded=True):
        with st.form("add_city_form", clear_on_submit=True):
            city_name = st.text_input(
                "City name",
                placeholder="Enter the name of the city",
            )

            submitted = st.form_submit_button("Add city")

        if submitted:
            if not city_name.strip():
                st.error("City name cannot be empty.")
            else:
                ok, data, _ = api(
                    "POST",
                    "/root-admin/cities",
                    json={"name": city_name.strip()},
                )

                if ok:
                    flash(
                        f"City '{data['name']}' added successfully."
                    )
                    st.rerun()
                else:
                    st.error(data)

    st.divider()
    st.subheader("Registered cities")

    # Fetch registered cities
    ok, cities, _ = api("GET", "/root-admin/cities")

    if not ok:
        st.error(cities)
        return

    if not cities:
        st.info("No cities have been added yet.")
        return

    # Table header
    header = st.columns([1, 4, 2, 1.5])
    header[0].markdown("**City ID**")
    header[1].markdown("**Name**")
    header[2].markdown("**Status**")
    header[3].markdown("**Action**")

    st.divider()

    # Display each city with its own Delete button
    for city in cities:
        city_id = city["city_id"]

        col1, col2, col3, col4 = st.columns([1, 4, 2, 1.5])

        col1.write(city_id)
        col2.write(city["name"])
        col3.write(active_text(city["is_active"]))

        if col4.button(
            "Delete",
            key=f"delete_city_{city_id}",
            type="secondary",
        ):
            ok, data, _ = api(
                "DELETE",
                f"/root-admin/cities/{city_id}",
            )

            if ok:
                flash(
                    f"City '{city['name']}' deleted successfully."
                )
                st.rerun()
            else:
                st.error(data)



