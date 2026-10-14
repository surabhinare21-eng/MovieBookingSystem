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


def theatres_page():
    with st.expander("Add a theatre"):
        with st.form("add_theatre_form", clear_on_submit=True):
            name = st.text_input(
                "Theatre name",
                key="new_theatre_name",
            )
            city = st.text_input(
                "City",
                key="new_theatre_city",
            )
            address = st.text_input(
                "Address",
                key="new_theatre_address",
            )

            submitted = st.form_submit_button("Add theatre")

        if submitted:
            ok, data, _ = api(
                "POST",
                "/root-admin/theatres",
                json={
                    "name": name.strip(),
                    "city": city.strip(),
                    "address": address.strip(),
                },
            )

            if ok:
                flash(
                    f"Theatre added: {data['name']}, "
                    f"{data['city']}."
                )
                st.rerun()
            else:
                st.error(data)

    ok, theatres, _ = api("GET", "/root-admin/theatres")

    if not ok:
        st.error(theatres)
        return

    if not theatres:
        st.info("No theatres yet. Add the first one above.")
        return

    query = st.text_input(
        "Search theatres",
        placeholder="Name or city",
        key="theatre_search",
    )

    shown = [
        theatre
        for theatre in theatres
        if matches(
            query,
            theatre["name"],
            theatre["city"],
            theatre["address"],
        )
    ]


    st.subheader("Theatres")

    if not shown:
        st.info("No theatres match your search.")
        return

    # Header row
    header = st.columns([1.2, 1.0, 0.6, 1.4, 1.2, 2.0, 1.0])

    headers = [
        
        "ID",
        "Theatre",
        "City",
        "Address",
        "Status",
        "Action",
        "Delete"
    ]

    for col, label in zip(header, headers):
        col.markdown(f"**{label}**")

    # Display each theatre with its own action buttons
    for theatre in shown:
        theatre_id = theatre["theatre_id"]

        cols = st.columns([1.2, 1.0, 0.6, 1.4, 1.2, 2.0, 1.0])

        with cols[-2]:
            action_label = (
                "Deactivate"
                if theatre["is_active"]
                else "Activate"
            )

            if st.button(
                action_label,
                key=f"toggle_theatre_{theatre_id}",
            ):
                ok, data, _ = api(
                    "PATCH",
                    f"/root-admin/theatres/{theatre_id}/status",
                    json={
                        "is_active": not theatre["is_active"]
                    },
                )

                if ok:
                    flash(
                        f"{theatre['name']} "
                        f"{'deactivated' if theatre['is_active'] else 'activated'}."
                    )
                    st.rerun()
                else:
                    st.error(data)

        with cols[-1]:
            if st.button(
                "Delete",
                key=f"delete_theatre_{theatre_id}",
            ):
                st.session_state["pending_delete_theatre"] = theatre_id

        cols[0].write(theatre_id)
        cols[1].write(theatre["name"])
        cols[2].write(theatre["city"])
        cols[3].write(theatre["address"])
        cols[4].write(active_text(theatre["is_active"]))

    # Ask for confirmation before deleting
    pending_id = st.session_state.get("pending_delete_theatre")

    if pending_id is not None:
        pending_theatre = next(
            (
                theatre for theatre in theatres
                if theatre["theatre_id"] == pending_id
            ),
            None,
        )

        if pending_theatre is None:
            st.session_state.pop("pending_delete_theatre", None)
        else:
            st.warning(
                f"Are you sure you want to permanently delete "
                f"{pending_theatre['name']}?"
            )

            confirm_col, cancel_col = st.columns(2)

            with confirm_col:
                if st.button(
                    "Confirm Delete",
                    key="confirm_delete_theatre",
                    type="primary",
                ):
                    ok, data, _ = api(
                        "DELETE",
                        f"/root-admin/theatres/{pending_id}",
                    )

                    if ok:
                        st.session_state.pop(
                            "pending_delete_theatre", None
                        )
                        flash(
                            f"Theatre '{pending_theatre['name']}' deleted successfully."
                        )
                        st.rerun()
                    else:
                        st.error(data)

            with cancel_col:
                if st.button(
                    "Cancel",
                    key="cancel_delete_theatre",
                ):
                    st.session_state.pop(
                        "pending_delete_theatre", None
                    )
                    st.rerun()




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