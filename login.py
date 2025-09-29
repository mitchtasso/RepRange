import streamlit as st
from supabase import create_client, Client
import scripts.main as main
from streamlit_cookies_controller import CookieController

supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]
supabase = Client = create_client(supabase_url, supabase_key)

controller = CookieController()

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
        controller.set('token', supabase.auth.get_session().refresh_token)
        return user
    except Exception as e:
        st.error(f"Login failed: {e}")

def sign_out():
    try:
        controller.remove('token')
        supabase.auth.sign_out()
        st.session_state.user_email = None
        st.rerun()
    except Exception as e:
        st.error(f"Logout failed: {e}")

def one_time_pass_send(email):
    supabase.auth.reset_password_email(email)

def one_time_pass_confirm(email, otp):
    user = supabase.auth.verify_otp({"email": f"{email}",
                                "token": f"{otp}",
                                "type": "email",})
    st.session_state['otp_token'] = supabase.auth.get_session().access_token
    st.session_state['otp_refresh'] = supabase.auth.get_session().refresh_token

def reset_new_password(new_password):
    supabase.auth.set_session(st.session_state['otp_token'], st.session_state['otp_refresh'])
    supabase.auth.update_user({"password": new_password})

def auth_screen():
    st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
    )
    
    st.set_page_config(page_title="RepRange", page_icon="images/RepRange-icon.png")
    space, mid, space2 = st.columns(3)
    with mid:
        st.image("images/RepRange-logo.png", width=200)
    authBox = st.container(border=True)
    login, signup, reset = authBox.tabs([r"$\textsf{\large Login}$", r"$\textsf{\large Sign Up}$", r"$\textsf{\large Reset Password}$"])
    
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
                st.error("Passwords do not match")
    with reset:
        if "pass_reset" not in st.session_state:
            st.session_state['pass_reset'] = 'start'
            st.session_state['temp_email'] = ''
        if st.session_state.pass_reset == 'start':
            st.write('Send a One Time Password (OTP) to your email address to verify your identity')
            email_reset = st.text_input("Email", key='reset_email')
            if st.button('Send Code', key='pass_reset_button'):
                try:
                    st.session_state.temp_email = email_reset
                    one_time_pass_send(email_reset)
                    st.success("One time password sent to your email")
                    st.session_state.pass_reset = 'otp'
                    st.rerun()
                except Exception:
                    st.error("Issue sending one time password, please wait and try again")
                    st.session_state.pass_reset = 'start'
        elif st.session_state.pass_reset == 'otp':
            st.success(f'One time password sent to: {st.session_state.temp_email}')
            otp_input = st.number_input('OTP', min_value=0, max_value=999999, format="%06d")
            otp_submit, otp_cancel, buttonSpace = st.columns([1,1,6])
            with otp_submit:
                if st.button('Login', key='otp_confirm', width='stretch'):
                    try:
                        st.session_state.pass_reset = 'reset'
                        one_time_pass_confirm(st.session_state.temp_email, otp_input)
                        st.success("One time password confirmed!")
                    except Exception as e:
                        st.session_state.pass_reset = 'otp'
                        st.error(f"Issue confirming one time password: {e}")
                    st.rerun()
            with otp_cancel:
                if st.button(':red[Cancel]', key='cancel_otp_send', width='stretch'):
                    st.session_state.pass_reset = 'start'
                    st.rerun()
        elif st.session_state.pass_reset == 'reset':
            st.success("One time password confirmed!")
            st.text(st.session_state.temp_email)
            password_reset = st.text_input("New Password:", type='password', key='password_reset')
            confirm_password_reset = st.text_input("Confirm New Password:", type='password', key='password_confirm_reset')
            if st.button("Reset Password"):
                if confirm_password_reset == password_reset:
                    try:
                        reset_new_password(password_reset)
                        st.success("Password reset successful")
                        st.session_state.pass_reset = 'start'
                        st.rerun()
                    except Exception as e:
                        st.error(f"Issure resetting password: {e}")
                else:
                    st.error("Passwords do not match")

def main_app(token):
    session = supabase.auth.get_user(token)
    user_email = session.user.email
    user_id = session.user.id
    try:
        main.main_page(user_email, user_id, token)
    except Exception as e:
        st.error(f"Session failed, please refresh the page: {e}")
    if st.sidebar.button("Logout"):
        sign_out()
    powered = st.sidebar.container(vertical_alignment='bottom')
    powered.write('')
    powered.divider()
    st.logo("images/RepRange-banner.png", size='large')
    powered.write("Powered by OpenAI's GPT-5")
    powered.write('© 2025 Mitchware')

if "user_email" not in st.session_state:
    st.session_state.user_email = None
    st.session_state.user_id = None
    st.session_state['authenticated'] = False

if controller.get('token') == None:
    if st.session_state.user_email:
        main_app(st.session_state.token)
    else:
        auth_screen()
else:
    try:
        supabase.auth.refresh_session(controller.get('token'))
        #supabase.auth.set_session(access_token=controller.get('atoken'),refresh_token=controller.get('token'))
        sessionRefresh = supabase.auth.get_session().access_token
        controller.set('token', supabase.auth.get_session().refresh_token)
        #controller.set('atoken', supabase.auth.get_session().access_token)
        main_app(sessionRefresh)
    except Exception as e:
        controller.remove('token')
        st.rerun()
