import streamlit as st 

st.title("Movie Ticket Booking ")
st.subheader("Signup page ")

with st.form("Registration form"):
    user_name = st.text_input("Username")
    user_email = st.text_input("Email")
    user_password = st.text_input("Password", type="password")
    user_confirm_password = st.text_input("Confirm Password", type="password")
    user_phone_number = st.text_input("Phone Number")
    
    signup_submit_button = st.form_submit_button("SignUp")


if signup_submit_button:
    
    if not user_name or not user_email or not user_password or not user_confirm_password or not user_phone_number:
        st.error(" Please Check all fields are required to be filled  ")
    
    
    elif user_password != user_confirm_password:
        st.error("Your confirm password is not matching ")
        
    else:
        
        st.success(f"Congratulation {user_name}! your account have  successfully  created ")
        
if st.button("If you  have already  a account ? Login "):
    st.switch_page("pages/login.py")        