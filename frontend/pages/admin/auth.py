
import streamlit as st

from api import PASSWORD_RULE
from common import api


def auth_screen():
    """Render login, signup, and email OTP verification."""

    _, middle, _ = st.columns([1, 2, 1])

    with middle:
        login_tab, signup_tab = st.tabs(["Log in", "Sign up"])

        with login_tab:
            with st.form("login_form"):
                email = st.text_input("Email", key="login_email")
                password = st.text_input(
                    "Password",
                    type="password",
                    key="login_password",
                )
                submitted = st.form_submit_button("Log in")

            if submitted:
                ok, data, _ = api(
                    "POST",
                    "/auth/login",
                    json={
                        "user_email": email.strip(),
                        "password": password,
                    },
                )
                
                if not ok:
                    st.error(data)
                else:
                    token = data["access_token"]

                    ok, profile, _ = api(
                        "GET",
                        "/auth/me",
                        token_override=token,
                    )

                    if ok:
                        st.session_state.theatre_id = data["theatre_id"]
                        st.session_state.token  = token
                        st.session_state.user = profile
                        st.rerun()
                    else:
                        st.error(profile)

        # ---------------- SIGNUP / OTP ----------------
        with signup_tab:
            st.caption(
                "New accounts are customer accounts. "
                "Verify your email to finish registration."
            )

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
                    username = st.text_input(
                        "Username",
                        key="signup_username",
                    )
                    email = st.text_input(
                        "Email",
                        key="signup_email",
                    )
                    phone = st.text_input(
                        "Phone number",
                        key="signup_phone",
                    )
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
                    submitted = st.form_submit_button(
                        "Send verification code"
                    )

                if submitted:
                    if password != confirm_password:
                        st.error(
                            "Passwords do not match. Please try again."
                        )
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
                                data.get(
                                    "message",
                                    "Verification code sent.",
                                )
                            )
                            st.rerun()
                        else:
                            st.error(data)
                            
