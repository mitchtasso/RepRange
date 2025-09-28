import streamlit as st
import random
from openai import OpenAI
import clipboard
from pydantic import BaseModel, ConfigDict

greetings = ['Hello, what can we get into today?', 'Hi, have anything specific in mind?',
             "What's on your mind today?"]

def page(supabase, user_id, openai_key):
    
    def get_workout_records():
        response = supabase.table("workouts").select("workout_date, exercise_type, repetitions, weight, sets").eq("user_id", user_id).order("workout_date", desc=True).execute()
        return str(response.data)
    
    def get_meal_records():
        response = supabase.table("meals").select("date, meal_name, calories, protein").eq("user_id", user_id).order("date", desc=True).execute()
        return str(response.data)
    
    def reset_chat():
        st.session_state['vert_messages'] = []
        st.session_state.responseID = None
        st.rerun()

    if 'model' not in st.session_state:
        st.session_state['model'] = OpenAI(api_key=openai_key)

    if 'responseID' not in st.session_state:
        st.session_state['responseID'] = None

    if 'vert_messages' not in st.session_state:
        reset_chat()

    for message in st.session_state['vert_messages']:
        avatarImage = ''
        if message['role'] == 'user':
            avatarImage = 'images/default-user.png'
        else:
            avatarImage = 'images/chadAI.png'
        
        with st.chat_message(message['role'], avatar=avatarImage):
            st.markdown(message['content'])
    
    if prompt := st.chat_input("Ask a question about fitness.."):
        st.session_state['vert_messages'].append({"role": "user", "content": prompt})
        with st.chat_message('user', avatar='images/default-user.png'):
            st.write(prompt)

        with st.chat_message("ai", avatar='images/chadAI.png'):
            st.write('Thinking...')
        
        with st.chat_message('assistant', avatar='images/chadAI.png'):
            client = st.session_state['model']
            response = client.responses.create(
                instructions=f'Act like a fitness expert that has access to these workout records: {get_workout_records()} and these meal records: {get_meal_records()}. Keep your responses short. Your name is Chad.',
                input=prompt,
                model='gpt-5-nano',
                previous_response_id=st.session_state.responseID,
                stream=True
            )
            
            def stream_output():
                for event in response:
                    if event.type == 'response.output_text.delta':
                        yield event.delta
                    elif event.type == 'function_call':
                        if event.name == 'pull_workout_records':
                            result = get_workout_records()
                            # Handle the result, e.g., yield it or send it back to the API
                            yield result
            stream_text = st.write_stream(stream_output())
            #stream_text = st.write_stream(response)
        st.session_state['vert_messages'].append({"role": "assistant", "content":  stream_text})

    if len(st.session_state.vert_messages) == 0:
        st.title('')
        st.title(greetings[random.randint(0,len(greetings)-1)])

    if len(st.session_state.vert_messages) > 0:
        output = ''
        for i in range (0, len(st.session_state.vert_messages)):
            output += ('\n' + (st.session_state.vert_messages[i]['role']).upper() + ": \n\n" + st.session_state.vert_messages[i]['content'] + "\n")
        
        actions = st.container()
        col1, col2, col3, col4 = actions.columns([1,1,1,13])
        with col1:
            if st.button(" 📋 ", key='vert_copy', width='stretch'):
                clipboard.copy(st.session_state.vert_messages[len(st.session_state.vert_messages)-1]['content'])
                actions.success('Contents copied')
        with col2:
            st.download_button(' ↓ ', data=output, file_name='vert-output.txt', width='stretch')
        with col3:
            if st.button(" 🗘 ", key='vert_clear', width='stretch'):
                reset_chat()