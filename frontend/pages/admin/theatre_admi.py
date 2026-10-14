
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


def theatre_admins_page():
    ok, theatres, _ = api("GET", "/root-admin/theatres")

    if not ok:
        st.error(theatres)
        return

    ok, admins, _ = api(
        "GET",
        "/root-admin/users",
        params={"role": "ADMIN", "limit": 200},
    )

    if not ok:
        st.error(admins)
        return

    labels = {
        theatre["theatre_id"]: (
            f"{theatre['name']} ({theatre['city']})"
        )
        for theatre in theatres
    }

    # Create theatre admin
    with st.expander("Create a theatre admin"):
        if not theatres:
            st.info("Add a theatre first.")
        else:
            with st.form("add_admin_form", clear_on_submit=True):
                username = st.text_input("Username")
                email = st.text_input("Email")
                phone = st.text_input("Phone number")
                password = st.text_input(
                    "Password",
                    type="password",
                    max_chars=12,
                    help=PASSWORD_RULE,
                )
                theatre_id = st.selectbox(
                    "Theatre",
                    list(labels),
                    format_func=lambda tid: labels[tid],
                )

                submitted = st.form_submit_button(
                    "Create theatre admin"
                )

            if submitted:
                if not all(
                    [username.strip(), email.strip(),
                     phone.strip(), password]
                ):
                    st.error("Please fill in all fields.")
                else:
                    ok, data, _ = api(
                        "POST",
                        "/root-admin/theatre-admins",
                        json={
                            "username": username.strip(),
                            "user_email": email.strip(),
                            "phone_no": phone.strip(),
                            "password": password,
                            "theatre_id": theatre_id,
                        },
                    )

                    if ok:
                        flash(
                            f"Theatre admin {data['username']} created."
                        )
                        st.rerun()
                    else:
                        st.error(data)

    st.divider()
    st.subheader("Theatre admins")

    if not admins:
        st.info("No theatre admins yet.")
        return

    theatre_names = {
        theatre["theatre_id"]: theatre["name"]
        for theatre in theatres
    }

    # Admin list
    for admin in admins:
        admin_id = admin["user_id"]

        with st.container(border=True):
            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(f"**{admin['username']}**")
                st.caption(
                    f"Email: {admin['user_email']} | "
                    f"Phone: {admin['phone_no']}"
                )
                st.write(
                    "Theatre: "
                    + theatre_names.get(admin["theatre_id"], "Unknown")
                )
                st.write(
                    "Status: "
                    + user_status_text(admin["is_active"])
                )

            with col2:
                if st.button(
                    "Edit",
                    key=f"edit_admin_{admin_id}",
                ):
                    st.session_state["edit_admin_id"] = admin_id

                if st.button(
                    "Delete",
                    key=f"delete_admin_{admin_id}",
                ):
                    st.session_state["delete_admin_id"] = admin_id

    # Edit selected admin
    edit_id = st.session_state.get("edit_admin_id")
    selected = next(
        (a for a in admins if a["user_id"] == edit_id),
        None,
    )

    if selected:
        st.divider()
        st.subheader(f"Edit admin: {selected['username']}")

        with st.form(f"edit_admin_form_{edit_id}"):
            username = st.text_input(
                "Username",
                value=selected["username"],
            )
            email = st.text_input(
                "Email",
                value=selected["user_email"],
            )
            phone = st.text_input(
                "Phone number",
                value=selected["phone_no"],
            )

            theatre_ids = list(labels)
            current_theatre = selected["theatre_id"]
            default_index = (
                theatre_ids.index(current_theatre)
                if current_theatre in theatre_ids
                else 0
            )

            theatre_id = st.selectbox(
                "Theatre",
                theatre_ids,
                index=default_index,
                format_func=lambda tid: labels[tid],
            ) if theatre_ids else None

            save = st.form_submit_button("Save changes")
            cancel = st.form_submit_button("Cancel")

        if cancel:
            st.session_state.pop("edit_admin_id", None)
            st.rerun()

        if save:
            if not all([username.strip(), email.strip(), phone.strip()]):
                st.error("Please fill in all fields.")
            elif theatre_id is None:
                st.error("Please add a theatre first.")
            else:
                # Confirm the correct endpoint and payload
                # against your backend before using this request.
                ok, data, _ = api(
                    "PATCH",
                    f"/root-admin/users/{edit_id}",
                    json={
                        "username": username.strip(),
                        "user_email": email.strip(),
                        "phone_no": phone.strip(),
                        "theatre_id": theatre_id,
                    },
                )

                if ok:
                    st.session_state.pop("edit_admin_id", None)
                    flash("Theatre admin updated successfully.")
                    st.rerun()
                else:
                    st.error(data)

    # Confirm deletion
    delete_id = st.session_state.get("delete_admin_id")
    delete_admin = next(
        (a for a in admins if a["user_id"] == delete_id),
        None,
    )

    if delete_admin:
        st.warning(
            f"Are you sure you want to permanently delete "
            f"{delete_admin['username']}?"
        )

        confirm_col, cancel_col = st.columns(2)

        if confirm_col.button(
            "Confirm Delete",
            key="confirm_delete_admin",
            type="primary",
        ):
            ok, data, _ = api(
                "DELETE",
                f"/root-admin/users/{delete_id}",
            )

            if ok:
                st.session_state.pop("delete_admin_id", None)
                st.session_state.pop("edit_admin_id", None)
                flash("Theatre admin deleted successfully.")
                st.rerun()
            else:
                st.error(data)

        if cancel_col.button(
            "Cancel",
            key="cancel_delete_admin",
        ):
            st.session_state.pop("delete_admin_id", None)
            st.rerun()


