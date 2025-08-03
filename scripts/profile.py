import streamlit as st
from supabase import create_client, Client
import login

supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_SERVICE_KEY"]
supabase = Client = create_client(supabase_url, supabase_key)

def page(user_id, user_email):
    logo, title = st.columns([1,5])
    with logo:
        st.image("images/default-user.png", width=100)
    with title:
        st.title("Profile")
    
    profile = st.container(border=True)
    profile.write(f"Email: {user_email}")
    
    profile.error("Selecting this option immediately deletes your account and all records. Proceed with caution.")
    if profile.button("Delete Account"):
        try:
            supabase.table("workouts").delete().eq("user_id", user_id).execute()
            supabase.table("meals").delete().eq("user_id", user_id).execute()
            supabase.auth.admin.delete_user(user_id)
            profile.success("Account deleted successfully")
            login.sign_out()
        except Exception as e:
            profile.error(f"Error deleting all records: {e}")
    