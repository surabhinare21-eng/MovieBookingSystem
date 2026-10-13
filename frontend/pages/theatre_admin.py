
from datetime import datetime

import streamlit as st

from common import (
    api,
    active_text,
    flash,
    field,
    show_table,
    status_field,
)


def my_theatre_page():
    ok, theatre, _ = api("GET", "/theatre-admin/my-theatre")

    if not ok:
        st.error(theatre)
        st.caption("A super admin can assign or reactivate your theatre.")
        return

    with st.container(border=True):
        st.subheader(theatre["name"])

        left, middle, right = st.columns(3)

        with left:
            field("City", theatre["city"])

        with middle:
            field("Address", theatre["address"])

        with right:
            status_field("Status", theatre["is_active"])

    with st.expander("Edit theatre details"):
        st.caption("The city can only be changed by a super admin.")

        with st.form("edit_theatre_form"):
            name = st.text_input(
                "Theatre name",
                value=theatre["name"],
                key="edit_theatre_name",
            )

            address = st.text_input(
                "Address",
                value=theatre["address"],
                key="edit_theatre_address",
            )

            submitted = st.form_submit_button("Save changes")

        if submitted:
            changes = {}

            if name.strip() != theatre["name"]:
                changes["name"] = name.strip()

            if address.strip() != theatre["address"]:
                changes["address"] = address.strip()

            if not changes:
                st.info("Nothing changed.")
            else:
                ok, data, _ = api(
                    "PATCH",
                    "/theatre-admin/my-theatre",
                    json=changes,
                )

                if ok:
                    flash("Theatre details saved.")
                    st.rerun()
                else:
                    st.error(data)


def screens_page():
    st.subheader("Screen Management")
    st.caption("Manage the screens assigned to the theatres.")

    with st.expander("Add a screen", expanded=True):
        with st.form("create_screen_form", clear_on_submit=True):
            screen_is_active = st.checkbox("Active", value=True)

            total_rows = st.number_input(
                "Total rows",
                min_value=0,
                step=1,
            )

            total_cols = st.number_input(
                "Total columns",
                min_value=0,
                step=1,
            )

            submitted = st.form_submit_button(
                "Add screen",
                type="primary",
            )

        if submitted:
            ok, data, _ = api(
                "POST",
                "/screens/",
                json={
                    "screen_is_active": screen_is_active,
                    "total_rows": int(total_rows),
                    "total_cols": int(total_cols),
                },
            )

            if ok:
                flash(f"Screen {data['screen_id']} added successfully.")
                st.rerun()
            else:
                st.error(data)

    st.divider()
    st.subheader("Your screens")

    ok, screens, _ = api("GET", "/screens/")

    if not ok:
        st.error(screens)
        return

    if not screens:
        st.info("No screens have been added yet.")
        return

    show_table(
        [
            {
                "Screen ID": screen["screen_id"],
                "Status": active_text(screen["screen_is_active"]),
                "Rows": screen["total_rows"],
                "Columns": screen["total_cols"],
            }
            for screen in screens
        ],
        {
            "Screen ID": "Screen ID",
            "Status": "Status",
            "Rows": "Rows",
            "Columns": "Columns",
        },
    )

    labels = {
        screen["screen_id"]: f"Screen {screen['screen_id']}"
        for screen in screens
    }

    selected_id = st.selectbox(
        "Manage screen",
        list(labels),
        format_func=lambda screen_id: labels[screen_id],
        key="manage_screen_id",
    )

    selected = next(
        screen for screen in screens
        if screen["screen_id"] == selected_id
    )

    with st.form("update_screen_form"):
        is_active = st.checkbox(
            "Active",
            value=selected["screen_is_active"],
        )

        rows = st.number_input(
            "Total rows",
            min_value=0,
            value=selected["total_rows"],
            step=1,
        )

        columns = st.number_input(
            "Total columns",
            min_value=0,
            value=selected["total_cols"],
            step=1,
        )

        update_submitted = st.form_submit_button("Save screen")

    if update_submitted:
        ok, data, _ = api(
            "PATCH",
            f"/screens/{selected_id}",
            json={
                "screen_is_active": is_active,
                "total_rows": int(rows),
                "total_cols": int(columns),
            },
        )

        if ok:
            flash("Screen updated successfully.")
            st.rerun()
        else:
            st.error(data)

    if st.button("Delete screen", key="delete_screen"):
        ok, data, _ = api("DELETE", f"/screens/{selected_id}")

        if ok:
            flash("Screen deleted successfully.")
            st.rerun()
        else:
            st.error(data)


def shows_page():
    st.subheader("Show Scheduling")
    st.caption("Schedule and manage movie shows for your theatre.")

    with st.expander("Schedule a new show", expanded=True):
        with st.form("create_show_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            movie_id = col1.number_input(
                "Movie ID",
                min_value=1,
            )

            screen_id = col2.number_input(
                "Screen ID",
                min_value=1,
            )

            col3, col4 = st.columns(2)

            show_language = col3.selectbox(
                "Language",
                ["English", "Hindi", "Marathi", "Other"],
            )

            show_format = col4.selectbox(
                "Format",
                ["2D", "3D", "IMAX", "4DX"],
            )

            col5, col6 = st.columns(2)

            start_date = col5.date_input(
                "Show date",
                key="show_start_date",
            )

            start_time = col6.time_input(
                "Start time",
                key="show_start_time",
            )

            col7, col8 = st.columns(2)

            end_date = col7.date_input(
                "End date",
                value=start_date,
                key="show_end_date",
            )

            end_time = col8.time_input(
                "End time",
                value=start_time,
                key="show_end_time",
            )

            submitted = st.form_submit_button(
                "Schedule show",
                type="primary",
            )

        if submitted:
            start_datetime = datetime.combine(
                start_date,
                start_time,
            )

            end_datetime = datetime.combine(
                end_date,
                end_time,
            )

            if end_datetime <= start_datetime:
                st.error("End time must be after start time.")
            else:
                payload = {
                    "show_start_time": start_datetime.isoformat(),
                    "show_end_time": end_datetime.isoformat(),
                    "show_status": True,
                    "show_language": show_language,
                    "show_format": show_format,
                    "screen_id": int(screen_id),
                    "movie_id": int(movie_id),
                }

                ok, data, _ = api(
                    "POST",
                    "/shows/",
                    json=payload,
                )

                if ok:
                    flash("Show scheduled successfully.")
                    st.rerun()
                else:
                    st.error(data)

    st.divider()
    st.subheader("Scheduled shows")

    if st.button("Refresh shows", key="refresh_shows"):
        st.rerun()

    ok, shows, _ = api("GET", "/shows/")

    if not ok:
        st.error(shows)
        return

    if not shows:
        st.info("No shows have been scheduled yet.")
        return

    rows = []

    for show in shows:
        rows.append({
            "Show ID": show["show_id"],
            "Movie ID": show["movie_id"],
            "Screen ID": show["screen_id"],
            "Start Time": show["show_start_time"],
            "End Time": show["show_end_time"],
            "Language": show["show_language"],
            "Format": show["show_format"],
            "Status": active_text(show["show_status"]),
        })

    show_table(
        rows,
        {
            "Show ID": "Show ID",
            "Movie ID": "Movie ID",
            "Screen ID": "Screen ID",
            "Start Time": "Start Time",
            "End Time": "End Time",
            "Language": "Language",
            "Format": "Format",
            "Status": "Status",
        },
    )

    st.subheader("Manage show status")

    show_ids = [show["show_id"] for show in shows]

    selected_id = st.selectbox(
        "Select show",
        show_ids,
        key="manage_show_id",
    )

    selected_show = next(
        show for show in shows
        if show["show_id"] == selected_id
    )

    currently_active = selected_show["show_status"]

    st.write(
        f"Current status: {active_text(currently_active)}"
    )

    button_label = (
        "Deactivate show"
        if currently_active
        else "Activate show"
    )

    if st.button(button_label, key="toggle_show_status"):
        ok, data, _ = api(
            "PATCH",
            f"/shows/{selected_id}/status",
            json={"show_status": not currently_active},
        )

        if ok:
            flash("Show status updated successfully.")
            st.rerun()
        else:
            st.error(data)