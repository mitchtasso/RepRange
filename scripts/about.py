import streamlit as st

def page():
    logo, title = st.columns([1,5])

    with logo:
        st.image("images/logo.png", width=100)
    with title:
        st.title("About")
        github, linkedin, streamlit, space = st.columns([1,1,1,1.5])
        with github:
            st.link_button("GitHub", url='https://github.com/mitchtasso', icon='💻', use_container_width=True)
        with linkedin:
            st.link_button("LinkedIn", url='https://www.linkedin.com/in/mitchell-tasso-91504a283', icon='💼', use_container_width=True)
        with streamlit:
            st.link_button("Streamlit", url='https://share.streamlit.io/user/mitchtasso', icon='🐍', use_container_width=True)
        with space:
            st.write("")

    description = st.container(border=True)
    description.write("""Hello! My name is Mitchell Tasso of Mitchware. Thank you for using my application RepRange. This application was developed with Streamlit, Python, and Supabase.
                This application has built in authentication, stores all data per user, and utilizes RLS to keep your data secure. I have included my LinkedIn, GitHub, and Streamlit if 
                you are interested in the application or want to connect. Keep grinding and don't forget to log it!""")