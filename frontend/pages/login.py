import streamlit as st

st.title("Movie Ticket Booking")
st.subheader("Login")

with st.form("Login Form"):
    # Inputs
    user_email = st.text_input("Username")
    user_password = st.text_input("Password", type="password") # Password mask karna mat bhoolna!
    
    # Sending data for verification
    login_submit_button = st.form_submit_button("Login")

if login_submit_button:
    if not user_email or not user_password:
        st.error(" Please fill all the fields ")
    
    
    


# Sign Up page par jaane ke liye button
if st.button("Don't have an account? Sign Up"):
    st.switch_page("pages/signup.py")