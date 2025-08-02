import streamlit as st
from supabase import create_client, Client

import scripts.logworkout as logworkout
import scripts.chadai as chadai
import scripts.workouts_record as workouts_record
import scripts.progress as progress
import scripts.about as about

supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]
openai_key = st.secrets["OPENAI_KEY"]
supabase = Client = create_client(supabase_url, supabase_key)

def main_page(user_email, user_id, token):
    st.set_page_config(page_icon="images/RepRange-logo.png", page_title="RepRange", initial_sidebar_state='expanded')
    
    supabase.postgrest.auth(token)

    # Sidebar navigation for authenticated users
    st.sidebar.image("images/default-user.png", width=75)
    st.sidebar.write(f"Welcome, {user_email}!")
    st.sidebar.title("Menu")
    page = st.sidebar.selectbox("Select a page", ["📝Log Workout", "🦾ChadAI", "📙Workout Entries", "📈Progress", "🔗About"])
    
    if page == "📝Log Workout":
        logworkout.page(supabase, user_id)
    elif page == "🦾ChadAI":
        chadai.page(supabase, user_id, openai_key)
    elif page == "📙Workout Entries":
        workouts_record.page(supabase, user_id)
    elif page == "📈Progress":
        progress.page(supabase, user_id)
    elif page == "🔗About":
        about.page()