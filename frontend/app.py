
import streamlit as st

from api import DEFAULT_API_URL, PASSWORD_RULE, call

st.set_page_config(page_title="Movie Booking System", layout="wide")

ROLE_LABELS = {
    "SUPER_ADMIN": "Super admin",
    "ADMIN": "Theatre admin",
    "CUSTOMER": "Customer",
}


for key in ("token", "user", "flash", "notice", "pending_signup_email", "signup_success") :
    if key not in st.session_state:
        st.session_state[key] = None



with st.sidebar.expander("Connection"):
    api_url = st.text_input("Backend URL", DEFAULT_API_URL, key="backend_url")


def flash(message: str) -> None:
    """Show a success message after the next re-run."""
    st.session_state.flash = message


def log_out(notice: str | None = None) -> None:
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.notice = notice


def api(method: str, path: str, **kwargs):
    """Call the backend with the saved token. A 401 means the session is over."""
    ok, data, code = call(method, api_url, path, token=st.session_state.token, **kwargs)
    if code == 401 and st.session_state.token:
        log_out("Your session expired or your account was blocked. Log in again.")
        st.rerun()
    return ok, data, code


def status_color(value):
    """Cell colour for the Status column of a table."""
    if value == "Active":
        return "color: #1B7F3B; font-weight: 600"
    return "color: #B3261E; font-weight: 600"

def show_table(rows, columns: dict):
    """make table"""

    if not rows:
        st.info("No records available.")
        return

    headers = list(columns.values())

    st.dataframe(
        [
            {
                label: row.get(field, "-")
                for field, label in columns.items()
            }
            for row in rows
        ],
        hide_index=True,
        use_container_width=True,
    )


def matches(query: str, *values) -> bool:
    query = query.strip().lower()
    return not query or any(query in str(v).lower() for v in values)


def active_text(is_active: bool) -> str:
    return "Active" if is_active else "Inactive"


def user_status_text(is_active: bool) -> str:
    return "Active" if is_active else "Blocked"


def status_md(is_active: bool, off_word: str = "Inactive") -> str:
    """Coloured status word for normal page text (green when on, red when off)."""
    return ":green[Active]" if is_active else f":red[{off_word}]"


def field(label: str, value) -> None:
    st.caption(label)
    st.text(value if value not in (None, "") else "-")


def status_field(label: str, is_active: bool, off_word: str = "Inactive") -> None:
    st.caption(label)
    st.markdown(status_md(is_active, off_word))


user = st.session_state.user
if user:
    st.sidebar.markdown(f"### {user['username']}")
    st.sidebar.caption(ROLE_LABELS.get(user["role"], user["role"]))
    if st.sidebar.button("Log out", key="logout_button"):
        log_out()
        st.rerun()

st.title("Movie Ticket Booking System")

if st.session_state.notice:
    st.warning(st.session_state.notice)
    st.session_state.notice = None

if st.session_state.flash:
    st.success(st.session_state.flash)
    st.session_state.flash = None



def auth_screen():
    _, middle, _ = st.columns([1, 2, 1])
    with middle:
        login_tab, signup_tab = st.tabs(["Log in", "Sign up"])

        with login_tab:
            with st.form("login_form"):
                email = st.text_input("Email", key="login_email")
                password = st.text_input("Password", type="password", key="login_password")
                submitted = st.form_submit_button("Log in")

            if submitted:
                ok, data, _ = api(
                    "POST", "/auth/login", json={"user_email": email.strip(), "password": password}
                )
                if not ok:
                    st.error(data)
                else:
                    token = data["access_token"]
                    ok, profile, _ = call("GET", api_url, "/auth/me", token=token)
                    if ok:
                        st.session_state.token = token
                        st.session_state.user = profile
                        st.rerun()
                    else:
                        st.error(profile)

        with signup_tab:
            st.caption("New accounts are customer accounts. Verify your email to finish registration.")

            if st.session_state.pending_signup_email:
                pending_email = st.session_state.pending_signup_email
                st.info(
                    f"A 6-digit verification code was sent to {pending_email}. "
                    "It expires in 10 minutes."
                )

                with st.form("verify_signup_form"):
                    otp = st.text_input(
                        "Email verification code",
                        max_chars=6,
                        key="signup_otp",
                    )
                    verify_submitted = st.form_submit_button(
                        "Verify email and create account"
                    )

                if verify_submitted:
                    ok, data, _ = api(
                        "POST",
                        "/auth/signup/verify",
                        json={
                            "user_email": pending_email,
                            "otp": otp.strip(),
                        },
                    )

                    if ok:
                        st.session_state.pending_signup_email = None
                        st.session_state.signup_success = data.get(
                            "message",
                            "Email verified. You can now log in.",
                        )
                        st.rerun()
                    else:
                        st.error(data)

                if st.button("Start signup again", key="restart_signup"):
                    st.session_state.pending_signup_email = None
                    st.rerun()

            else:
                if st.session_state.signup_success:
                    st.success(st.session_state.signup_success)
                    st.session_state.signup_success = None

                with st.form("signup_form"):
                    username = st.text_input("Username", key="signup_username")
                    email = st.text_input("Email", key="signup_email")
                    phone = st.text_input("Phone number", key="signup_phone")
                    password = st.text_input(
                        "Password",
                        type="password",
                        max_chars=12,
                        help=PASSWORD_RULE,
                        key="signup_password",
                    )
                    confirm_password = st.text_input(
                        "Confirm Password",
                        type="password",
                        max_chars=12,
                        key="signup_confirm_password",
                    )
                    submitted = st.form_submit_button("Send verification code")

                if submitted:
                    if password != confirm_password:
                        st.error("Passwords do not match. Please try again.")
                    else:
                        ok, data, _ = api(
                            "POST",
                            "/auth/signup/request-verification",
                            json={
                                "username": username.strip(),
                                "user_email": email.strip(),
                                "phone_no": phone.strip(),
                                "password": password,
                            },
                        )

                        if ok:
                            st.session_state.pending_signup_email = (
                                email.strip().lower()
                            )
                            st.success(
                                data.get("message", "Verification code sent.")
                            )
                            st.rerun()
                        else:
                            st.error(data)



def profile_page():
    me = st.session_state.user

    with st.container(border=True):
        st.subheader(me["username"])
        st.caption(ROLE_LABELS.get(me["role"], me["role"]))

        left, right = st.columns(2)
        with left:
            field("Email", me["user_email"])
            field("Phone number", me["phone_no"])
        with right:
            field("Account number", me["id"])
            status_field("Account status", me["is_active"], "Blocked")

    if st.button("Refresh profile", key="refresh_profile"):
        ok, data, _ = api("GET", "/auth/me")
        if ok:
            st.session_state.user = data
            st.rerun()
        else:
            st.error(data)


def customer_home():
    st.header(f"Welcome, {st.session_state.user['username']}")
    profile_page()
    st.info("Browsing movies and booking tickets will appear here once those features are built.")


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
            name = st.text_input("Theatre name", value=theatre["name"], key="edit_theatre_name")
            address = st.text_input("Address", value=theatre["address"], key="edit_theatre_address")
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
                ok, data, _ = api("PATCH", "/theatre-admin/my-theatre", json=changes)
                if ok:
                    flash("Theatre details saved.")
                    st.rerun()
                else:
                    st.error(data)


def overview_page():
    ok_t, theatres, _ = api("GET", "/root-admin/theatres")
    ok_u, users, _ = api("GET", "/root-admin/users", params={"limit": 200})
    if not ok_t:
        st.error(theatres)
        return
    if not ok_u:
        st.error(users)
        return

    row1 = st.columns(3)
    row1[0].metric("Theatres", len(theatres))
    row1[1].metric("Active theatres", sum(t["is_active"] for t in theatres))
    row1[2].metric("Inactive theatres", sum(not t["is_active"] for t in theatres))

    row2 = st.columns(3)
    row2[0].metric("Customers", sum(u["role"] == "CUSTOMER" for u in users))
    row2[1].metric("Theatre admins", sum(u["role"] == "ADMIN" for u in users))
    row2[2].metric("Blocked users", sum(not u["is_active"] for u in users))

    if len(users) == 200:
        st.caption("User counts cover the first 200 users.")

    if not theatres:
        st.info("No theatres yet. Open the Theatres tab to add the first one.")
    else:
        unassigned = [
            t for t in theatres
            if t["is_active"] and not any(u["role"] == "ADMIN" and u["theatre_id"] == t["theatre_id"] for u in users)
        ]
        if unassigned:
            st.warning(
                "Active theatres without a theatre admin: "
                + ", ".join(t["name"] for t in unassigned)
                + ". Create one in the Theatre admins tab."
            )


def theatres_page():
    with st.expander("Add a theatre"):
        with st.form("add_theatre_form", clear_on_submit=True):
            name = st.text_input("Theatre name", key="new_theatre_name")
            city = st.text_input("City", key="new_theatre_city")
            address = st.text_input("Address", key="new_theatre_address")
            submitted = st.form_submit_button("Add theatre")

        if submitted:
            ok, data, _ = api(
                "POST",
                "/root-admin/theatres",
                json={"name": name.strip(), "city": city.strip(), "address": address.strip()},
            )
            if ok:
                flash(f"Theatre added: {data['name']}, {data['city']}.")
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

    query = st.text_input("Search theatres", placeholder="Name or city", key="theatre_search")
    shown = [t for t in theatres if matches(query, t["name"], t["city"], t["address"])]
    rows = [{**t, "status": active_text(t["is_active"])} for t in shown]
    if rows:
        show_table(
            rows,
            {"theatre_id": "ID", "name": "Theatre", "city": "City", "address": "Address", "status": "Status"},
        )
    else:
        st.info("No theatres match your search.")

    st.subheader("Manage a theatre")
    labels = {t["theatre_id"]: f"{t['name']} ({t['city']})" for t in theatres}
    chosen_id = st.selectbox("Theatre", list(labels), format_func=lambda i: labels[i], key="manage_theatre")
    chosen = next(t for t in theatres if t["theatre_id"] == chosen_id)

    st.markdown(f"Status: {status_md(chosen['is_active'])}")
    if chosen["is_active"]:
        st.caption("Deactivating a theatre stops its theatre admin from managing it.")
        button_label = "Deactivate theatre"
    else:
        button_label = "Activate theatre"

    if st.button(button_label, key="toggle_theatre"):
        ok, data, _ = api(
            "PATCH",
            f"/root-admin/theatres/{chosen_id}/status",
            json={"is_active": not chosen["is_active"]},
        )
        if ok:
            flash(f"{chosen['name']} is now {'inactive' if chosen['is_active'] else 'active'}.")
            st.rerun()
        else:
            st.error(data)


def theatre_admins_page():
    ok, theatres, _ = api("GET", "/root-admin/theatres")
    if not ok:
        st.error(theatres)
        return

    with st.container(border=True):
        st.subheader("Create a theatre admin")
        if not theatres:
            st.info("Add a theatre first. Every theatre admin belongs to one theatre.")
        else:
            labels = {t["theatre_id"]: f"{t['name']} ({t['city']})" for t in theatres}
            with st.form("add_admin_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                username = col1.text_input("Username", key="admin_username")
                email = col2.text_input("Email", key="admin_email")
                phone = col1.text_input("Phone number", key="admin_phone")
                password = col2.text_input(
                    "Password", type="password", max_chars=12, help=PASSWORD_RULE, key="admin_password"
                )
                theatre_id = st.selectbox(
                    "Theatre", list(labels), format_func=lambda i: labels[i], key="admin_theatre"
                )
                submitted = st.form_submit_button("Create theatre admin")

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
                    flash(f"Theatre admin {data['username']} created for {labels[theatre_id]}.")
                    st.rerun()
                else:
                    st.error(data)

    st.subheader("Theatre admins")
    ok, admins, _ = api("GET", "/root-admin/users", params={"role": "ADMIN", "limit": 200})
    if not ok:
        st.error(admins)
        return
    if not admins:
        st.info("No theatre admins yet.")
        return

    theatre_names = {t["theatre_id"]: t["name"] for t in theatres}
    rows = [
        {**a, "theatre": theatre_names.get(a["theatre_id"], "-"), "status": user_status_text(a["is_active"])}
        for a in admins
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
    role_filter = left.selectbox("Role", ["All", "CUSTOMER", "ADMIN", "SUPER_ADMIN"], key="users_role")
    query = right.text_input("Search users", placeholder="Name, email or phone", key="user_search")

    params = {"limit": 200}
    if role_filter != "All":
        params["role"] = role_filter

    ok, users, _ = api("GET", "/root-admin/users", params=params)
    if not ok:
        st.error(users)
        return

    shown = [u for u in users if matches(query, u["username"], u["user_email"], u["phone_no"])]
    if not shown:
        st.info("No users match these filters.")
        return

    rows = [
        {**u, "role_label": ROLE_LABELS.get(u["role"], u["role"]), "status": user_status_text(u["is_active"])}
        for u in shown
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
        st.caption("Showing the first 200 users. Use the filters to narrow the list.")

    st.subheader("Block or unblock a user")
    labels = {u["user_id"]: f"{u['username']} ({u['user_email']})" for u in shown}
    chosen_id = st.selectbox("User", list(labels), format_func=lambda i: labels[i], key="manage_user")
    chosen = next(u for u in shown if u["user_id"] == chosen_id)

    st.markdown(
        f"Role: {ROLE_LABELS.get(chosen['role'], chosen['role'])}. "
        f"Status: {status_md(chosen['is_active'], 'Blocked')}"
    )

    is_self = chosen["user_id"] == st.session_state.user["id"]
    is_super = chosen["role"] == "SUPER_ADMIN"
    if is_self:
        st.caption("You cannot block your own account.")
    elif is_super:
        st.caption("Super admin accounts cannot be blocked.")
    elif chosen["is_active"]:
        st.caption("A blocked user cannot log in, and their current session ends on the next click.")

    button_label = "Block user" if chosen["is_active"] else "Unblock user"
    if st.button(button_label, key="toggle_user", disabled=is_self or is_super):
        ok, data, _ = api(
            "PATCH",
            f"/root-admin/users/{chosen_id}/status",
            json={"is_active": not chosen["is_active"]},
        )
        if ok:
            flash(f"{chosen['username']} is now {'blocked' if chosen['is_active'] else 'active'}.")
            st.rerun()
        else:
            st.error(data)


def render_tabs(screens: dict) -> None:
    for tab, render in zip(st.tabs(list(screens)), screens.values()):
        with tab:
            render()


if not user:
    auth_screen()
elif user["role"] == "CUSTOMER":
    customer_home()
elif user["role"] == "ADMIN":
    st.header("Theatre admin")
    render_tabs({"My theatre": my_theatre_page, "My profile": profile_page})
elif user["role"] == "SUPER_ADMIN":
    st.header("Super admin")
    render_tabs(
        {
            "Overview": overview_page,
            "Theatres": theatres_page,
            "Theatre admins": theatre_admins_page,
            "Users": users_page,
            "My profile": profile_page,
        }
    )
else:
    st.error(f"Unknown role: {user['role']}")
