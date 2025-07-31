import streamlit as st
from streamlit_calendar import calendar
from supabase import create_client, Client
import pandas as pd
import exercises

supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]
supabase = Client = create_client(supabase_url, supabase_key)

def main_page(user_email, user_id, token):
    st.set_page_config(page_icon="images\RepRange-logo.png", page_title="RepRange", initial_sidebar_state='expanded')
    
    supabase.postgrest.auth(token)

    # Sidebar navigation for authenticated users
    st.sidebar.image("images\default-user.png", width=75)
    st.sidebar.write(f"Welcome, {user_email}!")
    st.sidebar.title("Menu")
    page = st.sidebar.selectbox("Select a page", ["Log Workout", "Workout Entries", "Progress", "About"])
    
    all_workouts = exercises.exerciseTypes
    all_workouts.sort()
    
    def log_workout(date):
        st.header("Log a New Workout")
        with st.form("workout_form"):
            workout_date = st.date_input("Date", value=date)
            exercise_type = st.selectbox("Exercise Type", all_workouts)
            repetitions = st.number_input("Repetitions", min_value=1, max_value=10000)
            weight = st.number_input("Weight (Bodyweight for Calisthenics)", min_value=1, max_value=10000)
            sets = st.number_input("Sets", min_value=1, max_value=10000)
            volume = weight * repetitions * sets
            submit = st.form_submit_button("Log Workout")

        if submit:
            data = {
                "user_id": user_id,
                "workout_date": workout_date.isoformat(),
                "exercise_type": exercise_type,
                "repetitions": repetitions,
                "weight": weight,
                "sets": sets,
                "volume": volume
            }
            try:
                supabase.table("workouts").insert(data).execute()
                st.success("Workout logged successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error logging workout: {e}")
    
    if page == "Log Workout":
        homeLogo, homeTitle = st.columns([1,5])
        with homeLogo:
            st.image("images\RepRange-logo.png", width=100)
        with homeTitle:
            st.title(f" Welcome to RepRange!")
        st.write("Please select a date and log your workout for the day or for any days you missed. No slacking!")
        calendar_options = {
            "editable": True,
            "selectable": True,
            "headerToolbar": {
                "left": "today prev,next",
                "center": "title",
                "right": "dayGridMonth",
            },
            "initialView": "dayGridMonth"
        }
        
        response = supabase.table("workouts").select("workout_date, exercise_type, repetitions").eq("user_id", user_id).order("workout_date", desc=True).execute()
        event_data = response.data
        calendar_events = []
        for i in range(0, len(event_data)):
            current_dict = event_data[i]
            title = current_dict['exercise_type']
            start = current_dict['workout_date']
            calendar_events.append({'title': title, 'start': start})

        custom_css="""
            .fc-event-past {
                opacity: 0.8;
            }
            .fc-event-time {
                font-style: italic;
            }
            .fc-event-title {
                font-weight: 700;
            }
            .fc-toolbar-title {
                font-size: 2rem;
            }
        """

        cal = calendar(
            events=calendar_events,
            options=calendar_options,
            custom_css=custom_css,
            key='calendar',
            callbacks=['dateClick', 'eventChange', 'eventsSet', 'select']
            )
        try:
            dateClicked = cal["dateClick"]
            log_workout(dateClicked["date"])
        except Exception as e:
            pass

    elif page == "Workout Entries":
        st.title("🏋Workout Entries")
        workoutfilter = st.selectbox("Filter by Exercise Type", all_workouts, placeholder="All", index=None)
        if workoutfilter == None:
            response = supabase.table("workouts").select("workout_date, exercise_type, repetitions, weight, sets, id").eq("user_id", user_id).order("workout_date", desc=True).execute()
        else:
            response = supabase.table("workouts").select("workout_date, exercise_type, repetitions, weight, sets, id").eq("user_id", user_id).eq("exercise_type", workoutfilter).order("workout_date", desc=True).execute()
        workouts = response.data
        
        labels = st.container(border=True)
        col1, col2, col3, col4, col5 = labels.columns([1,3,0.5,0.5,0.5])
        with col1:
            st.write("Workout Date")
        with col2:
            st.write("Exercise")
        with col3:
            st.write("Reps")
        with col4:
            st.write("Weight")
        with col5:
            st.write("Sets")
        
        if workouts:
            for i in range(len(workouts)):
                containerName = f"workout{i}"
                workoutButtonName = f"button{i}"
                editButtonName = f"editbutton{i}"
                record = st.container(border=True, key=containerName)
                workoutCol, exerciseCol, repCol, weightCol, setCol = record.columns([1,3,0.5,0.5,0.5])
                with workoutCol:
                    workoutValue = st.date_input(label="", value=workouts[i]['workout_date'], key=f"workoutCol{i}", label_visibility='collapsed')
                with exerciseCol:
                    exerciseValue = st.selectbox(label="", options=all_workouts, index=None, placeholder=workouts[i]['exercise_type'], key=f"exerciseCol{i}", label_visibility='collapsed')
                with repCol:
                    repValue = st.number_input(label="", value=workouts[i]['repetitions'], key=f"repCol{i}", label_visibility='collapsed', min_value=1, max_value=10000)
                with weightCol:
                    weightValue = st.number_input(label="", value=workouts[i]['weight'], key=f"weightCol{i}", label_visibility='collapsed', min_value=1, max_value=10000)
                with setCol:
                    setValue = st.number_input(label="", value=workouts[i]['sets'], key=f"setCol{i}", label_visibility='collapsed', min_value=1, max_value=10000)
                
                deleteButton, saveButton, emptyCol = st.columns([1,1,6.8])
                with saveButton:
                    if st.button('Save', key=editButtonName, use_container_width=True):
                            try:
                                data = workouts[i]['id']
                                if exerciseValue == None:
                                    exerciseValue = workouts[i]['exercise_type']
                                    
                                volume = weightValue * repValue * setValue
                                    
                                supabase.table("workouts").update({"workout_date": workoutValue.isoformat(), 
                                                                "exercise_type": exerciseValue,
                                                                "repetitions": repValue,
                                                                "weight": weightValue,
                                                                "sets": setValue,
                                                                "volume": volume}).eq("id", data).execute()
                                record.success("Updated record")
                                st.rerun()
                            except Exception as e:
                                record.error(f"Failed to update record: {e}")
                with deleteButton:
                    if st.button('Delete', key=workoutButtonName,use_container_width=True):
                            data = workouts[i]['id']
                            supabase.table("workouts").delete().eq("id", data).execute()
                            st.rerun()
        else:
            st.write("No workouts logged yet.")

    elif page == "Progress":
        st.title("💪Workout Progress")
        exerciseType = st.selectbox(label="Exercise Type", options=all_workouts, index=0)
        response = supabase.table("workouts").select("*").eq("user_id", user_id).eq("exercise_type", exerciseType).execute()
        workouts = response.data
        if workouts:
            st.subheader("Progress by Volume")
            df = pd.DataFrame(workouts)
            df['workout_date'] = pd.to_datetime(df['workout_date'])
            weekly_duration = df.groupby('workout_date')['volume'].sum()
            st.line_chart(weekly_duration, x_label='Date', y_label='Volume')
            
            st.subheader("Projected Strength")
            response2 = supabase.table("workouts").select("*").eq("user_id", user_id).eq("exercise_type", exerciseType).order("workout_date", desc=True).limit(1).execute()
            exerciseData = response2.data
            workoutDate = exerciseData[0]['workout_date']
            repsCurrent = int(exerciseData[0]['repetitions'])
            weightCurrent = int(exerciseData[0]['weight'])
            oneRep = weightCurrent * (1.0 + (repsCurrent / 30.0))
            
            projections = st.container(border=True)
            projections.write("Most Recent Workout")
            recentWD, recentReps, recentWeight, recentMax = projections.columns(4)
            with recentWD:
                st.write("Date")
                st.write(workoutDate)
            with recentReps:
                st.write("Reps")
                st.write(str(repsCurrent))
            with recentWeight:
                st.write("Weight")
                st.write(str(weightCurrent), "lbs")
            with recentMax:
                st.write("One Rep Max")
                st.write(str(round(oneRep)), 'lbs')
            
            generations = projections.container(border=True)
            genPercent, genWeight, genReps = generations.columns(3)
            with genPercent:
                st.write("Percent of Max:")
                for i in range(1,11):
                    st.write(f"{100 - (5*i)}%")
            with genWeight:
                st.write("Weight:")
                for i in range(1,11):
                    newWeight = oneRep - (weightCurrent*0.08*i)
                    st.write(f"{round(newWeight)}lbs")
            with genReps:
                st.write("Reps:")
                for i in range(1,11):
                    newWeight = oneRep - (weightCurrent*0.08*i)
                    repsMax = 30.0 * ((oneRep / newWeight) - 1.0)
                    st.write(f"{round(repsMax)}")
        else:
            st.write("No data available for analytics.")
    elif page == "About":
        logo, title = st.columns([1,5])

        with logo:
            st.image("images\logo.png", width=100)
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