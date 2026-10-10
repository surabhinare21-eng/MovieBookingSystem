import streamlit as st

from api import DEFAULT_API_URL, get_profile, post_json


st.set_page_config(page_title="Movie Booking System", page_icon="🎬")
st.title("Movie Ticket Booking System")

api_url = st.sidebar.text_input("Backend URL", DEFAULT_API_URL)

if "token" not in st.session_state:
    st.session_state.token = None

signup_tab, login_tab, profile_tab = st.tabs(["Sign up", "Log in", "My profile"])

with signup_tab:
    st.subheader("Create an account")
    with st.form("signup_form"):
        username = st.text_input("Username")
        user_email = st.text_input("Email")
        phone_no = st.text_input("Phone number")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign up")

    if submitted:
        ok, result = post_json(
            api_url,
            "/auth/signup",
            {
                "username": username,
                "user_email": user_email,
                "phone_no": phone_no,
                "password": password,
            },
        )
        if ok:
            st.success(result["message"])
        else:
            st.error(result)

with login_tab:
    st.subheader("Log in")
    with st.form("login_form"):
        user_email = st.text_input("Login email")
        password = st.text_input("Login password", type="password")
        submitted = st.form_submit_button("Log in")

    if submitted:
        ok, result = post_json(
            api_url,
            "/auth/login",
            {"user_email": user_email, "password": password},
        )
        if ok:
            st.session_state.token = result["access_token"]
            st.success("Logged in successfully.")
        else:
            st.error(result)

with profile_tab:
    if not st.session_state.token:
        st.info("Log in first to view your profile.")
    elif st.button("Load profile"):
        ok, result = get_profile(api_url, st.session_state.token)
        if ok:
            st.json(result)
        else:
            st.error(result)

if st.sidebar.button("Log out"):
    st.session_state.token = None
    st.rerun()
