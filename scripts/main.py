import streamlit as st
from supabase import create_client, Client

import scripts.dashboard as dashboard
import scripts.log as log
import scripts.chadai as chadai
import scripts.records as records
import scripts.progress as progress
import scripts.profile as profile
import scripts.about as about

supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]
openai_key = st.secrets["OPENAI_KEY"]
supabase = Client = create_client(supabase_url, supabase_key)

def main_page(user_email, user_id, token):
    st.set_page_config(page_icon="images/RepRange-icon.png", page_title="RepRange", initial_sidebar_state='expanded')
    
    supabase.postgrest.auth(token)

    # Sidebar navigation for authenticated users
    st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
    )
    email = user_email.split('@')[0]
    st.sidebar.write(f'**{email.upper()}**')
    st.sidebar.text(f"{user_email}")
    st.sidebar.title("Menu")
    page = st.sidebar.selectbox("Page", ["📊Dashboard","📝Log", "🦾ChadAI", "📙Records", "📈Progress", "👤Profile", "🔗About"])
    
    if page == "📊Dashboard":
        dashboard.page(supabase, user_id)
    elif page == "📝Log":
        log.page(supabase, user_id)
    elif page == "🦾ChadAI":
        chadai.page(supabase, user_id, openai_key)
    elif page == "📙Records":
        records.page(supabase, user_id)
    elif page == "📈Progress":
        progress.page(supabase, user_id)
    elif page == "👤Profile":
        profile.page(user_id, user_email)
    elif page == "🔗About":
        about.page()