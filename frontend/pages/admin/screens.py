
import streamlit as st

from common import api, active_text, flash, show_table


LAYOUTS = {
    "Compact": {"rows": 5, "cols": 10, "seats": 50},
    "Small": {"rows": 10, "cols": 10, "seats": 100},
    "Medium": {"rows": 15, "cols": 10, "seats": 150},
    "Large": {"rows": 25, "cols": 10, "seats": 250},
}


@st.dialog("Edit Screen", width="large")
def edit_screen_dialog(screen):
    screen_id = screen["screen_id"]

    st.caption(f"Editing {screen['screen_name']}")

    layout_names = list(LAYOUTS.keys())
    current_layout = screen["seat_layout_name"]

    with st.form(f"edit_screen_form_{screen_id}"):
        updated_name = st.text_input(
            "Screen Name",
            value=screen["screen_name"],
            max_chars=100,
        )

        updated_layout = st.selectbox(
            "Seat Layout",
            options=layout_names,
            index=(
                layout_names.index(current_layout)
                if current_layout in layout_names
                else 0
            ),
            format_func=lambda name: (
                f"{name} — {LAYOUTS[name]['seats']} seats "
                f"({LAYOUTS[name]['rows']} × {LAYOUTS[name]['cols']})"
            ),
        )

        updated_active = st.checkbox(
            "Active",
            value=screen["screen_is_active"],
        )

        submitted = st.form_submit_button(
            "Save Changes",
            type="primary",
            width=True,
        )

    if submitted:
        if not updated_name.strip():
            st.error("Screen name cannot be empty.")
            return

        ok, data, _ = api(
            "PATCH",
            f"/screens/{screen_id}",
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


@st.dialog("Delete Screen", width="small")
def delete_screen_dialog(screen):
    screen_id = screen["screen_id"]

    st.warning(
        f"Are you sure you want to delete "
        f"**{screen['screen_name']}**?"
    )
    st.caption(
        "A screen with scheduled shows may not be deletable."
    )

    confirm_col, cancel_col = st.columns(2)

    if confirm_col.button(
        "Confirm Delete",
        key=f"confirm_delete_screen_{screen_id}",
        type="primary",
        width=True,
    ):
        ok, data, _ = api(
            "DELETE",
            f"/screens/{screen_id}",
        )

        if ok:
            flash("Screen deleted successfully.")
            st.rerun()
        else:
            st.error(data)

    if cancel_col.button(
        "Cancel",
        key=f"cancel_delete_screen_{screen_id}",
        width=True,
    ):
        st.rerun()


@st.dialog("Seat Layout Preview", width="large")
def seat_layout_dialog(screen):
    layout = LAYOUTS.get(screen["seat_layout_name"])

    if not layout:
        st.error("Unknown seat layout.")
        return

    st.subheader(screen["screen_name"])
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
                        f"seat_preview_{screen['screen_id']}_"
                        f"{row_index}_{col_index}"
                    ),
                    disabled=True,
                    width=True,
                )

    st.info("SCREEN")


def screens_page():
    """Add, view, edit, delete, and preview screens on one page."""

    st.subheader("Screen Management")
    st.caption("Manage your theatre screens from one place.")

    # ---------------- ADD SCREEN ----------------
    with st.expander("Add a Screen", expanded=True):
        with st.form("create_screen_form", clear_on_submit=True):
            screen_name = st.text_input(
                "Screen Name",
                placeholder="e.g. Screen A1",
                max_chars=100,
            )

            seat_layout_name = st.selectbox(
                "Seat Layout",
                options=list(LAYOUTS),
                format_func=lambda name: (
                    f"{name} — {LAYOUTS[name]['seats']} seats "
                    f"({LAYOUTS[name]['rows']} × "
                    f"{LAYOUTS[name]['cols']})"
                ),
            )

            screen_is_active = st.checkbox(
                "Active",
                value=True,
            )

            submitted = st.form_submit_button(
                "Add Screen",
                type="primary",
                width=True,
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

    st.divider()

    # ---------------- ALL SCREENS ----------------
    st.subheader("All Screens")

    if st.button("Refresh Screens", key="refresh_screens"):
        st.rerun()

    ok, screens, _ = api("GET", "/screens/")

    if not ok:
        st.error(f"Unable to load screens: {screens}")
        return

    if not screens:
        st.info("No screens have been added yet.")
        return

    show_table(
        [
            {
                "Screen ID": screen["screen_id"],
                "Screen Name": screen["screen_name"],
                "Seat Layout": screen["seat_layout_name"],
                "Total Seats": LAYOUTS.get(
                    screen["seat_layout_name"], {}
                ).get("seats", "N/A"),
                "Status": active_text(screen["screen_is_active"]),
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

    st.caption("Manage individual screens below.")

    # ---------------- PER-ROW ACTIONS ----------------
    for screen in screens:
        screen_id = screen["screen_id"]

        with st.container(border=True):
            details_col, edit_col, preview_col, delete_col = st.columns(
                [4, 1, 1.4, 1]
            )

            with details_col:
                st.markdown(f"**{screen['screen_name']}**")
                st.caption(
                    f"ID: {screen_id} · "
                    f"{screen['seat_layout_name']} · "
                    f"{LAYOUTS.get(screen['seat_layout_name'], {}).get('seats', 'N/A')} seats"
                )

            with edit_col:
                if st.button(
                    "Edit",
                    key=f"edit_screen_{screen_id}",
                    width=True,
                ):
                    edit_screen_dialog(screen)

            with preview_col:
                if st.button(
                    "View Layout",
                    key=f"preview_screen_{screen_id}",
                    width=True,
                ):
                    seat_layout_dialog(screen)

            with delete_col:
                if st.button(
                    "Delete",
                    key=f"delete_screen_{screen_id}",
                    width=True,
                ):
                    delete_screen_dialog(screen)
