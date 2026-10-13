
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


def overview_page():
    ok_t, theatres, _ = api("GET", "/root-admin/theatres")
    ok_u, users, _ = api(
        "GET",
        "/root-admin/users",
        params={"limit": 200},
    )

    if not ok_t:
        st.error(theatres)
        return

    if not ok_u:
        st.error(users)
        return

    row1 = st.columns(3)
    row1[0].metric("Theatres", len(theatres))
    row1[1].metric(
        "Active theatres",
        sum(t["is_active"] for t in theatres),
    )
    row1[2].metric(
        "Inactive theatres",
        sum(not t["is_active"] for t in theatres),
    )

    row2 = st.columns(3)
    row2[0].metric(
        "Customers",
        sum(u["role"] == "CUSTOMER" for u in users),
    )
    row2[1].metric(
        "Theatre admins",
        sum(u["role"] == "ADMIN" for u in users),
    )
    row2[2].metric(
        "Blocked users",
        sum(not u["is_active"] for u in users),
    )

    if len(users) == 200:
        st.caption("User counts cover the first 200 users.")

    if not theatres:
        st.info(
            "No theatres yet. Open the Theatres tab "
            "to add the first one."
        )
    else:
        unassigned = [
            theatre
            for theatre in theatres
            if theatre["is_active"]
            and not any(
                user["role"] == "ADMIN"
                and user["theatre_id"] == theatre["theatre_id"]
                for user in users
            )
        ]

        if unassigned:
            st.warning(
                "Active theatres without a theatre admin: "
                + ", ".join(t["name"] for t in unassigned)
                + ". Create one in the Theatre admins tab."
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
        "Action",
        "Delete",
        "ID",
        "Theatre",
        "City",
        "Address",
        "Status",
    ]

    for col, label in zip(header, headers):
        col.markdown(f"**{label}**")

    # Display each theatre with its own action buttons
    for theatre in shown:
        theatre_id = theatre["theatre_id"]

        cols = st.columns([1.2, 1.0, 0.6, 1.4, 1.2, 2.0, 1.0])

        with cols[0]:
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

        with cols[1]:
            if st.button(
                "Delete",
                key=f"delete_theatre_{theatre_id}",
            ):
                st.session_state["pending_delete_theatre"] = theatre_id

        cols[2].write(theatre_id)
        cols[3].write(theatre["name"])
        cols[4].write(theatre["city"])
        cols[5].write(theatre["address"])
        cols[6].write(active_text(theatre["is_active"]))

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


def theatre_admins_page():
    ok, theatres, _ = api("GET", "/root-admin/theatres")

    if not ok:
        st.error(theatres)
        return

    with st.container(border=True):
        st.subheader("Create a theatre admin")

        if not theatres:
            st.info(
                "Add a theatre first. Every theatre admin "
                "belongs to one theatre."
            )
        else:
            labels = {
                theatre["theatre_id"]: (
                    f"{theatre['name']} ({theatre['city']})"
                )
                for theatre in theatres
            }

            with st.form("add_admin_form", clear_on_submit=True):
                col1, col2 = st.columns(2)

                username = col1.text_input(
                    "Username",
                    key="admin_username",
                )
                email = col2.text_input(
                    "Email",
                    key="admin_email",
                )
                phone = col1.text_input(
                    "Phone number",
                    key="admin_phone",
                )
                password = col2.text_input(
                    "Password",
                    type="password",
                    max_chars=12,
                    help=PASSWORD_RULE,
                    key="admin_password",
                )

                theatre_id = st.selectbox(
                    "Theatre",
                    list(labels),
                    format_func=lambda theatre_id: labels[theatre_id],
                    key="admin_theatre",
                )

                submitted = st.form_submit_button(
                    "Create theatre admin"
                )

            if submitted:
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
                        f"Theatre admin {data['username']} "
                        f"created for {labels[theatre_id]}."
                    )
                    st.rerun()
                else:
                    st.error(data)

    st.subheader("Theatre admins")

    ok, admins, _ = api(
        "GET",
        "/root-admin/users",
        params={"role": "ADMIN", "limit": 200},
    )

    if not ok:
        st.error(admins)
        return

    if not admins:
        st.info("No theatre admins yet.")
        return

    theatre_names = {
        theatre["theatre_id"]: theatre["name"]
        for theatre in theatres
    }

    rows = [
        {
            **admin,
            "theatre": theatre_names.get(
                admin["theatre_id"], "-"
            ),
            "status": user_status_text(admin["is_active"]),
        }
        for admin in admins
    ]

    show_table(
        rows,
        {
            "user_id": "ID",
            "username": "Username",
            "user_email": "Email",
            "phone_no": "Phone",
            "theatre": "Theatre",
            "status": "Status",
        },
    )


def users_page():
    left, right = st.columns([1, 2])

    role_filter = left.selectbox(
        "Role",
        ["All", "CUSTOMER", "ADMIN", "SUPER_ADMIN"],
        key="users_role",
    )

    query = right.text_input(
        "Search users",
        placeholder="Name, email or phone",
        key="user_search",
    )

    params = {"limit": 200}

    if role_filter != "All":
        params["role"] = role_filter

    ok, users, _ = api(
        "GET",
        "/root-admin/users",
        params=params,
    )

    if not ok:
        st.error(users)
        return

    shown = [
        user for user in users
        if matches(
            query,
            user["username"],
            user["user_email"],
            user["phone_no"],
        )
    ]

    if not shown:
        st.info("No users match these filters.")
        return

    rows = [
        {
            **user,
            "role_label": ROLE_LABELS.get(
                user["role"], user["role"]
            ),
            "status": user_status_text(user["is_active"]),
        }
        for user in shown
    ]

    show_table(
        rows,
        {
            "user_id": "ID",
            "username": "Username",
            "user_email": "Email",
            "phone_no": "Phone",
            "role_label": "Role",
            "status": "Status",
        },
    )

    if len(users) == 200:
        st.caption(
            "Showing the first 200 users. "
            "Use the filters to narrow the list."
        )

    st.subheader("Block or unblock a user")

    labels = {
        user["user_id"]: (
            f"{user['username']} ({user['user_email']})"
        )
        for user in shown
    }

    chosen_id = st.selectbox(
        "User",
        list(labels),
        format_func=lambda user_id: labels[user_id],
        key="manage_user",
    )

    chosen = next(
        user for user in shown
        if user["user_id"] == chosen_id
    )

    st.markdown(
        f"Role: {ROLE_LABELS.get(chosen['role'], chosen['role'])}. "
        f"Status: {status_md(chosen['is_active'], 'Blocked')}"
    )

    is_self = chosen["user_id"] == st.session_state.user["id"]
    is_super = chosen["role"] == "SUPER_ADMIN"

    # if is_self:
        # st.caption("You cannot block your own account.")
    if is_super:
        st.caption("Super admin accounts cannot be blocked.")
    elif chosen["is_active"]:
        st.caption(
            "A blocked user cannot log in, and their current "
            "session ends on the next click."
        )

    button_label = (
        "Block user"
        if chosen["is_active"]
        else "Unblock user"
    )

    if st.button(
        button_label,
        key="toggle_user",
        disabled=is_self or is_super,
    ):
        ok, data, _ = api(
            "PATCH",
            f"/root-admin/users/{chosen_id}/status",
            json={"is_active": not chosen["is_active"]},
        )

        if ok:
            flash(
                f"{chosen['username']} is now "
                f"{'blocked' if chosen['is_active'] else 'active'}."
            )
            st.rerun()
        else:
            st.error(data)