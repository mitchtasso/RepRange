import streamlit as st

def page(supabase, user_id, user_email):
    logo, title = st.columns([1,5])
    with logo:
        st.image("images/default-user.png", width=100)
    with title:
        st.title("Profile")
    
    profile = st.container(border=True)
    profile.write(f"Email: {user_email}")
    
    profile.error("Selecting this option immediately deletes all records. Proceed with caution.")
    if profile.button("Delete Records"):
        try:
            supabase.table("workouts").delete().eq("user_id", user_id).execute()
            supabase.table("meals").delete().eq("user_id", user_id).execute()
            profile.success("All records deleted successfully")
            st.rerun()
        except Exception as e:
            profile.error(f"Error deleting all records: {e}")
    