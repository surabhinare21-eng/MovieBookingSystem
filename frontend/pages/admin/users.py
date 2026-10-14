import streamlit as st
from common import( 
api, ROLE_LABELS,matches,
user_status_text,show_table, status_md,flash
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

