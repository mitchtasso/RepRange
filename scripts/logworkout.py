import streamlit as st
from streamlit_calendar import calendar
import scripts.exercises as exercises

all_workouts = exercises.exerciseTypes
all_workouts.sort()

def log_workout(date, supabase, user_id):
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

def page(supabase, user_id):
    homeLogo, homeTitle = st.columns([1,5])
    with homeLogo:
        st.image("images/RepRange-logo.png", width=100)
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
        log_workout(dateClicked["date"], supabase, user_id)
    except Exception as e:
        pass
