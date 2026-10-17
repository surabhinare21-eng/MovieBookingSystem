
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
            use_container_width=True,
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
        use_container_width=True,
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
        use_container_width=True,
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
                    use_container_width=True,
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
                use_container_width=True,
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
    header_col, button_col = st.columns([5, 1])

    with header_col:
        st.subheader("screens")

    with button_col:
        if st.button(
            "hide" if st.session_state.get("show_screens_list", False) else "view",
            key="toggle_screens_list",
        ):
            st.session_state.show_screens_list = (
                not st.session_state.get("show_screens_list", False)
            )

    if not st.session_state.get("show_screens_list", False):
        return
    if st.button("Refresh Screens", key="refresh_screens"):
        st.rerun()

    ok, screens, _ = api("GET", "/screens/")

    if not ok:
        st.error(f"Unable to load screens: {screens}")
        return

    if not screens:
        st.info("No screens have been added yet.")
        return
    
    search_query = st.text_input(
        "Search screen",
        placeholder="Search by name",
        key="screen_catalogue_search",        
    ).strip().lower()
    filtered_screens = [
        screen
        for screen in screens
        if (
            search_query in str(screen["screen_name"]).lower()
            
        )
    ]

    if not filtered_screens:
        st.info("No screens match your search.")
        return

        # --- TABLE HEADER ---
    # Create the column layout structure for the grid table
    hdr_id, hdr_name, hdr_layout, hdr_seats, hdr_status, hdr_actions = st.columns(
        [1, 2, 1.5, 1, 1, 3.5]
    )
    
    with hdr_id: st.markdown("**Screen ID**")
    with hdr_name: st.markdown("**Screen Name**")
    with hdr_layout: st.markdown("**Seat Layout**")
    with hdr_seats: st.markdown("**Total Seats**")
    with hdr_status: st.markdown("**Status**")
    with hdr_actions: st.markdown("**Actions**")
    
    st.divider() # Sub-header underline separator

    # --- TABLE ROWS WITH INTEGRATED ACTIONS ---
    for screen in filtered_screens:
        screen_id = screen["screen_id"]
        
        # Wrapping each row entry inside a slight frame container for neatness
        with st.container():
            col_id, col_name, col_layout, col_seats, col_status, col_actions = st.columns(
                [1, 2, 1.5, 1, 1, 3.5]
            )
            
            # Populate Data cells
            col_id.write(str(screen_id))
            col_name.write(screen["screen_name"])
            col_layout.write(screen["seat_layout_name"])
            col_seats.write(str(LAYOUTS.get(screen["seat_layout_name"], {}).get("seats", "N/A")))
            col_status.write(active_text(screen["screen_is_active"]))
            
            # Populate Action Cells Side-by-Side inside the same row structure
            with col_actions:
                btn_edit, btn_view, btn_del = st.columns(3, gap="small")
                
                with btn_edit:
                    if st.button("Edit", key=f"tbl_edit_{screen_id}", use_container_width=True):
                        edit_screen_dialog(screen)
                        
                with btn_view:
                    if st.button("Layout", key=f"tbl_view_{screen_id}", use_container_width=True):
                        seat_layout_dialog(screen)
                        
                with btn_del:
                    if st.button("Delete", key=f"tbl_del_{screen_id}", type="secondary", use_container_width=True):
                        delete_screen_dialog(screen)
        st.divider()
