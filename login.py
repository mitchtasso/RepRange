import streamlit as st
from supabase import create_client, Client
import main

supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]
supabase = Client = create_client(supabase_url, supabase_key)

def sign_up(email,password):
    try:
        user = supabase.auth.sign_up({"email": email, "password": password})
        return user
    except Exception as e:
        st.error(f"Registration failed: {e}")

def sign_in(email,password):
    try:
        user = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state['token'] = supabase.auth.get_session().access_token
        return user
    except Exception as e:
        st.error(f"Login failed: {e}")

def sign_out():
    try:
        supabase.auth.sign_out()
        st.session_state.user_email = None
        st.rerun()
    except Exception as e:
        st.error(f"Logout failed: {e}")

def main_app(user_email, user_id, token):
    main.main_page(user_email, user_id, token)
    if st.sidebar.button("Logout"):
        sign_out()

def auth_screen():
    st.set_page_config(page_title="RepRange", page_icon="images/RepRange-logo.png")
    logo, title = st.columns([1,5])
    with logo:
        st.image("images/RepRange-logo.png", width=100)
    with title:
        st.title("RepRange")
    
    login, signup = st.tabs(["Login", "Sign Up"])
    
    with login:
        email = st.text_input("Email", key='login_user')
        password = st.text_input("Password", type='password', key='login_pass')
        if st.button("Login"):
            user = sign_in(email, password)
            if user and user.user:
                st.session_state.user_email = user.user.email
                st.session_state.user_id = user.user.id
                st.session_state['authenticated'] = True
                st.success(f"Welcome back, {email}!")
                st.rerun()
    
    with signup:
        email_signup = st.text_input("Email")
        password_signup = st.text_input("Password", type='password')
        confirm_password = st.text_input("Confirm Password", type='password')
        if st.button("Register"):
            if confirm_password == password_signup:
                user = sign_up(email_signup, password_signup)
                if user and user.user:
                    st.success("Registration successful. Please accept the confirmation email then login.")
            else:
                st.error("Password do not match")

if "user_email" not in st.session_state:
    st.session_state.user_email = None
    st.session_state.user_id = None
    st.session_state['authenticated'] = False

if st.session_state.user_email:
    main_app(st.session_state.user_email, st.session_state.user_id, st.session_state.token)
else:
    auth_screen()