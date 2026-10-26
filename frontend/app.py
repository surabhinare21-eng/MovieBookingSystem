"""Main entry point for the Movie Ticket Booking System."""

import streamlit as st

from api import DEFAULT_API_URL
from common import ROLE_LABELS, log_out

from pages.admin.auth import auth_screen
from pages.admin.users import users_page
from pages.admin.cities import cities_page
from pages.admin.overview import overview_page
from pages.admin.profile import profile_page
from pages.admin.screens import screens_page
from pages.admin.shows import shows_page
from pages.admin.movies import movies_page
from pages.admin.theatre_admin import theatre_admins_page
from pages.admin.theatres import theatres_page, my_theatre_page
from pages.admin.superadmin_dashboard import superadmin_dashboard
from pages.admin.theatreadmin_dashboard import theatreadmin_dashboard
from pages.customer.flow import customer_flow

# --------------------------------------------------
# 1. Application configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Movie Booking System",
    layout="wide",
)

# Hide Streamlit's automatic multipage navigation
st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# 2. Initialize session state
# --------------------------------------------------

for key in ("token", "user", "flash", "notice"):
    if key not in st.session_state:
        st.session_state[key] = None

if "pending_signup_email" not in st.session_state:
    st.session_state.pending_signup_email = ""

if "signup_success" not in st.session_state:
    st.session_state.signup_success = False




# --------------------------------------------------
# 4. Sidebar user information and logout
# --------------------------------------------------

user = st.session_state.user

if user:
    st.sidebar.markdown(f"### {user['username']}")

    st.sidebar.caption(
        ROLE_LABELS.get(user["role"], user["role"])
    )

    if st.sidebar.button("Log out", key="logout_button"):
        log_out()
        st.rerun()


# --------------------------------------------------
# 5. Application title and notifications
# --------------------------------------------------

st.markdown(
    """<h1 style='text-align: center;'>Movie Ticket Booking System</h1>""",
    unsafe_allow_html=True,
)

if st.session_state.notice:
    st.warning(st.session_state.notice)
    st.session_state.notice = None

if st.session_state.flash:
    st.success(st.session_state.flash)
    st.session_state.flash = None


# --------------------------------------------------
# 6. Reusable tab renderer
# --------------------------------------------------


def render_tabs(screens: dict) -> None:
    """Render pages while preserving the selected page on rerun."""

    state_key = f"selected_page_{st.session_state.user['role']}"
    page_names = list(screens.keys())

    if (
        state_key not in st.session_state
        or st.session_state[state_key] not in page_names
    ):
        st.session_state[state_key] = page_names[0]

    selected_page = st.session_state[state_key]

    selected_page = st.radio(
        "Navigation",
        page_names,
        index=page_names.index(selected_page),
        horizontal=True,
        key=f"navigation_{st.session_state.user['role']}",
        label_visibility="collapsed",
    )

    st.session_state[state_key] = selected_page

    st.divider()
    screens[selected_page]()



# --------------------------------------------------
# 7. Role-based routing
# --------------------------------------------------

user = st.session_state.user

if not user:
    auth_screen()

elif user["role"] == "CUSTOMER":
    customer_flow()


elif user["role"] == "ADMIN":
    st.header("Theatre admin")

    if "screen_page" not in st.session_state:
        st.session_state.screen_page = "list"

    
    render_tabs({
        "My theatre": my_theatre_page,
        "Screens": screens_page,
        "Show Scheduling": shows_page,
        "My profile": profile_page,
        "Admin Dashboard": theatreadmin_dashboard
    })



elif user["role"] == "SUPER_ADMIN":
    st.header("Super admin")

    if "movie_page" not in st.session_state:
        st.session_state.movie_page = "list"

    
    render_tabs({
        "Overview": overview_page,
        "Cities": cities_page,
        "Theatres": theatres_page,
        "Theatre admins": theatre_admins_page,
        "Movies": movies_page,
        "Users": users_page,
        "My profile": profile_page,
        "Superadmin Dashboard":superadmin_dashboard
    })
    


else:
    st.error(f"Unknown role: {user['role']}")
    



#for reference:
#any pages are first imported then a common function is set that only takes the tabs to 
#render eg movies cities and other tabs then according to the role we pass it to the 
#specific functions

