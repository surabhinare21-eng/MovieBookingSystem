
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


# def screens_page():
#     st.subheader("Screen Management")
#     st.caption("Manage the screens assigned to the theatres.")

#     with st.expander("Add a screen", expanded=True):
#         with st.form("create_screen_form", clear_on_submit=True):
#             screen_is_active = st.checkbox("Active", value=True)

#             total_rows = st.number_input(
#                 "Total rows",
#                 min_value=0,
#                 step=1,
#             )

#             total_cols = st.number_input(
#                 "Total columns",
#                 min_value=0,
#                 step=1,
#             )

#             submitted = st.form_submit_button(
#                 "Add screen",
#                 type="primary",
#             )

#         if submitted:
#             ok, data, _ = api(
#                 "POST",
#                 "/screens/",
#                 json={
#                     "screen_is_active": screen_is_active,
#                     "total_rows": int(total_rows),
#                     "total_cols": int(total_cols),
#                 },
#             )

#             if ok:
#                 flash(f"Screen {data['screen_id']} added successfully.")
#                 st.rerun()
#             else:
#                 st.error(data)

#     st.divider()
#     st.subheader("Your screens")

#     ok, screens, _ = api("GET", "/screens/")

#     if not ok:
#         st.error(screens)
#         return

#     if not screens:
#         st.info("No screens have been added yet.")
#         return

#     show_table(
#         [
#             {
#                 "Screen ID": screen["screen_id"],
#                 "Status": active_text(screen["screen_is_active"]),
#                 "Rows": screen["total_rows"],
#                 "Columns": screen["total_cols"],
#             }
#             for screen in screens
#         ],
#         {
#             "Screen ID": "Screen ID",
#             "Status": "Status",
#             "Rows": "Rows",
#             "Columns": "Columns",
#         },
#     )

#     labels = {
#         screen["screen_id"]: f"Screen {screen['screen_id']}"
#         for screen in screens
#     }

#     selected_id = st.selectbox(
#         "Manage screen",
#         list(labels),
#         format_func=lambda screen_id: labels[screen_id],
#         key="manage_screen_id",
#     )

#     selected = next(
#         screen for screen in screens
#         if screen["screen_id"] == selected_id
#     )

#     with st.form("update_screen_form"):
#         is_active = st.checkbox(
#             "Active",
#             value=selected["screen_is_active"],
#         )

#         rows = st.number_input(
#             "Total rows",
#             min_value=0,
#             value=selected["total_rows"],
#             step=1,
#         )

#         columns = st.number_input(
#             "Total columns",
#             min_value=0,
#             value=selected["total_cols"],
#             step=1,
#         )

#         update_submitted = st.form_submit_button("Save screen")

#     if update_submitted:
#         ok, data, _ = api(
#             "PATCH",
#             f"/screens/{selected_id}",
#             json={
#                 "screen_is_active": is_active,
#                 "total_rows": int(rows),
#                 "total_cols": int(columns),
#             },
#         )

#         if ok:
#             flash("Screen updated successfully.")
#             st.rerun()
#         else:
#             st.error(data)

#     if st.button("Delete screen", key="delete_screen"):
#         ok, data, _ = api("DELETE", f"/screens/{selected_id}")

#         if ok:
#             flash("Screen deleted successfully.")
#             st.rerun()
#         else:
#             st.error(data)



def screens_page():
    """Create, view, update, preview, and delete theatre screens."""

    layouts = {
        "Compact": {"rows": 5, "cols": 10, "seats": 50},
        "Small": {"rows": 10, "cols": 10, "seats": 100},
        "Medium": {"rows": 15, "cols": 10, "seats": 150},
        "Large": {"rows": 25, "cols": 10, "seats": 250},
    }

    st.subheader("Screen Management")
    st.caption("Managing the screens.")

    add_tab, manage_tab = st.tabs(["Add Screen", "Manage Screens"])

    # ---------------- ADD SCREEN ----------------
    with add_tab:
        with st.form("create_screen_form", clear_on_submit=True):
            screen_name = st.text_input(
                "Screen Name",
                placeholder="e.g. Screen A1",
                max_chars=100,
            )

            seat_layout_name = st.selectbox(
                "Seat Layout",
                options=list(layouts),
                format_func=lambda name: (
                    f"{name} — {layouts[name]['seats']} seats "
                    f"({layouts[name]['rows']} × {layouts[name]['cols']})"
                ),
            )

            screen_is_active = st.checkbox(
                "Active",
                value=False,
            )

            submitted = st.form_submit_button(
                "Add Screen",
                type="primary",
            )

        if submitted:
            if not screen_name.strip():
                st.error("Please enter a screen name.")
            else:
                ok, data, _ = api(
                    "POST",
                    "/screens/",
                    json={
                        "screen_name": screen_name.strip(),
                        "seat_layout_name": seat_layout_name,
                        "screen_is_active": screen_is_active,
                    },
                )

                if ok:
                    flash(
                        f"{data['screen_name']} added successfully."
                    )
                    st.rerun()
                else:
                    st.error(data)

    # ---------------- MANAGE SCREENS ----------------
    with manage_tab:
        st.subheader("Your Screens")

        ok, screens, _ = api("GET", "/screens/")

        if not ok:
            st.error(screens)
            return

        if not screens:
            st.info("No screens have been added yet.")
            return

        # Display all screens.
        show_table(
            [
                {
                    "Screen ID": screen["screen_id"],
                    "Screen Name": screen["screen_name"],
                    "Seat Layout": screen["seat_layout_name"],
                    "Total Seats": layouts.get(
                        screen["seat_layout_name"], {}
                    ).get("seats", "N/A"),
                    "Status": active_text(
                        screen["screen_is_active"]
                    ),
                }
                for screen in screens
            ],
            {
                "Screen ID": "Screen ID",
                "Screen Name": "Screen Name",
                "Seat Layout": "Seat Layout",
                "Total Seats": "Total Seats",
                "Status": "Status",
            },
        )

        st.divider()
        st.subheader("Update or Delete a Screen")

        screen_labels = {
            screen["screen_id"]: (
                f"{screen['screen_name']} "
                f"(ID: {screen['screen_id']})"
            )
            for screen in screens
        }

        selected_id = st.selectbox(
            "Select Screen",
            options=list(screen_labels),
            format_func=lambda screen_id: screen_labels[screen_id],
            key="manage_screen_id",
        )

        selected = next(
            screen
            for screen in screens
            if screen["screen_id"] == selected_id
        )

        # Edit screen details.
        with st.form("update_screen_form"):
            updated_name = st.text_input(
                "Screen Name",
                value=selected["screen_name"],
                max_chars=100,
            )

            updated_layout = st.selectbox(
                "Seat Layout",
                options=list(layouts),
                index=(
                    list(layouts).index(selected["seat_layout_name"])
                    if selected["seat_layout_name"] in layouts
                    else 0
                ),
                format_func=lambda name: (
                    f"{name} — {layouts[name]['seats']} seats "
                    f"({layouts[name]['rows']} × {layouts[name]['cols']})"
                ),
            )

            updated_active = st.checkbox(
                "Active",
                value=selected["screen_is_active"],
            )

            update_submitted = st.form_submit_button(
                "Save Changes",
                type="primary",
            )

        if update_submitted:
            if not updated_name.strip():
                st.error("Screen name cannot be empty.")
            else:
                ok, data, _ = api(
                    "PATCH",
                    f"/screens/{selected_id}",
                    json={
                        "screen_name": updated_name.strip(),
                        "seat_layout_name": updated_layout,
                        "screen_is_active": updated_active,
                    },
                )

                if ok:
                    flash("Screen updated successfully.")
                    st.rerun()
                else:
                    st.error(data)

        # Preview the selected screen's seat layout.
        if st.button(
            "View Seat Layout",
            key=f"view_layout_{selected_id}",
        ):
            st.session_state.screen_layout_preview_id = selected_id
            st.rerun()

        # Delete the selected screen.
        st.divider()
        st.warning(
            "A screen cannot be deleted if shows are scheduled on it."
        )

        if st.button(
            "Delete Selected Screen",
            key=f"delete_screen_{selected_id}",
            type="secondary",
        ):
            st.session_state.screen_to_delete_id = selected_id

        if st.session_state.get("screen_to_delete_id") == selected_id:
            st.error(
                f"Are you sure you want to delete "
                f"{selected['screen_name']}?"
            )

            confirm_col, cancel_col = st.columns(2)

            if confirm_col.button(
                "Confirm Delete",
                key=f"confirm_delete_{selected_id}",
                type="primary",
            ):
                ok, data, _ = api(
                    "DELETE",
                    f"/screens/{selected_id}",
                )

                if ok:
                    st.session_state.pop("screen_to_delete_id", None)
                    st.session_state.pop("manage_screen_id", None)
                    flash("Screen deleted successfully.")
                    st.rerun()
                else:
                    st.error(data)

            if cancel_col.button(
                "Cancel",
                key=f"cancel_delete_{selected_id}",
            ):
                st.session_state.pop("screen_to_delete_id", None)
                st.rerun()

    # ---------------- SEAT LAYOUT PREVIEW ----------------
    preview_id = st.session_state.get("screen_layout_preview_id")

    if preview_id is not None:
        ok, screen, _ = api("GET", f"/screens/{preview_id}")

        if not ok:
            st.error(screen)
            if st.button("Close Preview"):
                st.session_state.pop("screen_layout_preview_id", None)
                st.rerun()
            return

        layout = layouts.get(screen["seat_layout_name"])

        if layout is None:
            st.error("Unknown seat layout.")
            return

        st.divider()
        st.subheader(
            f"{screen['screen_name']} — Seat Layout Preview"
        )

        st.caption("Back of the auditorium")

        for row_index in reversed(range(layout["rows"])):
            row_label = chr(ord("A") + row_index)
            st.caption(f"Row {row_label}")

            seat_columns = st.columns(layout["cols"], gap="small")

            for col_index in range(layout["cols"]):
                seat_label = f"{row_label}{col_index + 1:02d}"

                with seat_columns[col_index]:
                    st.button(
                        f"🟢 {seat_label}",
                        key=(
                            f"seat_preview_{preview_id}_"
                            f"{row_index}_{col_index}"
                        ),
                        disabled=True,
                        use_container_width=True,
                    )

        st.info("SCREEN")

        if st.button("Close Seat Layout Preview"):
            st.session_state.pop("screen_layout_preview_id", None)
            st.rerun()



def shows_page():
    st.subheader("Show Scheduling")
    st.caption("Schedule and manage movie shows for your theatre.")

    with st.expander("Schedule a new show", expanded=True):

        # Fetch screens assigned to the logged-in theatre.
        screens_ok, screens, _ = api("GET", "/screens/")

        if not screens_ok:
            st.error(f"Unable to load screens: {screens}")
            return

        if not screens:
            st.warning(
                "No screens are available. Please create a screen "
                "before scheduling a show."
            )
            return

        # Display screen names while retaining their IDs.
        screen_options = {
            f"{screen['screen_name']} "
            f"({screen['seat_layout_name']})":
            screen["screen_id"]
            for screen in screens
        }

        with st.form("create_show_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            movie_id = col1.number_input(
                "Movie ID",
                min_value=1,
                step=1,
            )

            selected_screen = col2.selectbox(
                "Select Screen",
                options=list(screen_options.keys()),
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
                selected_screen_id = screen_options[selected_screen]

                payload = {
                    "show_start_time": start_datetime.isoformat(),
                    "show_end_time": end_datetime.isoformat(),
                    "show_status": True,
                    "show_language": show_language,
                    "show_format": show_format,
                    "screen_id": selected_screen_id,
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

    # Map screen IDs to names for display.
    # Fetch again so the table uses current screen information.
    screens_ok, screens, _ = api("GET", "/screens/")

    if not screens_ok:
        st.error(f"Unable to load screens: {screens}")
        return

    screen_names = {
        screen["screen_id"]: screen["screen_name"]
        for screen in screens
    }

    rows = []

    for show in shows:
        rows.append({
            "Show ID": show["show_id"],
            "Movie ID": show["movie_id"],
            "Screen": screen_names.get(
                show["screen_id"],
                f"Screen ID {show['screen_id']}",
            ),
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
            "Screen": "Screen",
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
