import streamlit as st
from openai import OpenAI

def page(supabase, user_id , openai_key):
    logo, title = st.columns([1,5])
    
    def reset_chat():
        st.session_state['messages'] = []
        response = supabase.table("workouts").select("workout_date, exercise_type, repetitions, weight, sets").eq("user_id", user_id).order("workout_date", desc=True).execute()
        st.session_state['messages'].append({"role": "user", "content": f'Act like a fitness guru named ChadAI and use these workout records for reference: {str(response.data)}'})

    with logo:
        st.image("images/chadAI.png", width=100)
    with title:
        st.title("ChadAI")
        clear = st.button("Clear")
        if clear:
            reset_chat()
    
    if 'model' not in st.session_state:
        st.session_state['model'] = OpenAI(api_key=openai_key)

    if 'messages' not in st.session_state:
        reset_chat()

    for message in st.session_state['messages']:
        if 'Act like a fitness guru named ChadAI' not in message['content']:
            with st.chat_message(message['role']):
                st.markdown(message['content'])

    if prompt := st.chat_input("Ask a question about fitness.."):
        st.session_state['messages'].append({"role": "user", "content": prompt})
        with st.chat_message('user'):
            st.markdown(prompt)

        with st.chat_message('assistant'):
            client = st.session_state['model']
            stream = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {"role": message["role"], "content": message["content"]} for message in st.session_state['messages']
                ],
                temperature=0.7,
                max_tokens=512,
                stream=True
            )

            response = st.write_stream(stream)
        st.session_state['messages'].append({"role": "assistant", "content": response})