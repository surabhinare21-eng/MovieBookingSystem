
import streamlit as st

from common import api, field, status_field, ROLE_LABELS


def profile_page():
    """Display the current user's profile and account information."""

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
            status_field(
                "Account status",
                me["is_active"],
                "Blocked",
            )

    if st.button("Refresh profile", key="refresh_profile"):
        ok, data, _ = api("GET", "/auth/me")

        if ok:
            st.session_state.user = data
            st.rerun()
        else:
            st.error(data)


def customer_home():
    """Display the customer home page."""

    st.header(f"Welcome, {st.session_state.user['username']}")

    profile_page()

    st.info(
        "Browsing movies and booking tickets will appear here "
        "once those features are built."
    )

