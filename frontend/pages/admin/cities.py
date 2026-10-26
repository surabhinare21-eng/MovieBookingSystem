
import streamlit as st

from api import PASSWORD_RULE

from common import (
    ROLE_LABELS,
    active_text,
    api,
    flash,
    # matches,
    # show_table,
    # status_md,
    # user_status_text,
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

    search_query = st.text_input(
        "Search cities",
        placeholder="Search by city name or ID",
        key="city_search",
    ).strip().lower()

    filtered_cities = [
        city
        for city in cities
        if (
            search_query in str(city["city_id"]).lower()
            or search_query in str(city["name"]).lower()
        )
    ]

    if not filtered_cities:
        st.info("No cities match your search.")
        return

    # Table header
    header = st.columns([1, 4, 2, 2])
    header[0].markdown("**City ID**")
    header[1].markdown("**Name**")
    header[2].markdown("**Status**")
    header[3].markdown("**Actions**")

    st.divider()

    # Display filtered cities
    for city in filtered_cities:
        city_id = city["city_id"]

        col1, col2, col3, col4, col5 = st.columns(
            [1, 4, 2, 1, 1]
        )

        col1.write(city_id)
        col2.write(city["name"])
        col3.write(active_text(city["is_active"]))

        if col4.button(
            "Edit",
            key=f"edit_city_{city_id}",
            use_container_width=True,
        ):
            edit_city(city)

        if col5.button(
            "Delete",
            key=f"delete_city_{city_id}",
            type="secondary",
            use_container_width=True,
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



@st.dialog("Edit City", width="small")
def edit_city(city):
    """Display a popup for editing an existing city name"""
    
    city_id = city["city_id"]
    city_name = city["name"]
    st.caption(f"Editing : {city['name']}")
    
    current_city = city.get("name")
    
    with st.form(f"edit_city_form_{city_id}"):
        city_name = st.text_input(
            "Name",
            value=current_city,
        )
    
        save_changes = st.form_submit_button(
            "Save Changes",
            type="primary",
            use_container_width=True
        )
    if save_changes:
        if(
            not city_name.strip()
        ):
            st.error("City is not empty")
            return
        
        ok,data,_ = api(
            "PUT",
            f"/root-admin/cities/{city_id}",
            json={"name":city_name.strip()},
        )
            
        if ok:
            flash("city updated successfully")
            st.rerun()
        else:
            st.error(data)