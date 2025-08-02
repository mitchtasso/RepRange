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

def log_meal(date, supabase, user_id):
    st.header("Log a New Meal")
    with st.form("workout_form"):
        food_date = st.date_input("Date", value=date)
        meal_name = st.text_input("Meal Name", placeholder="Misc", value=None)
        calories = st.number_input("Calories", min_value=0, max_value=10000)
        protein = st.number_input("Protein (g)", min_value=0, max_value=10000)
        submit = st.form_submit_button("Log Meal")

    if submit:
        if meal_name == None:
            meal_name = "Misc"
        
        data = {
            "user_id": user_id,
            "date": food_date.isoformat(),
            "meal_name": meal_name,
            "calories": calories,
            "protein": protein
        }
        try:
            supabase.table("meals").insert(data).execute()
            st.success("Meal logged successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Error logging workout: {e}")

def page(supabase, user_id):
    homeTitle, logType, space = st.columns([1.25,1,3], vertical_alignment='bottom')
    with homeTitle:
        st.title(f"📝Log")
    with logType:
        log_type = st.selectbox("Type",options=["Workout", "Meal"], label_visibility='collapsed')
    st.write("Please select a date and log your workout or meal. No slacking!")
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
    
    
    if log_type == "Workout":
        response = supabase.table("workouts").select("workout_date, exercise_type, repetitions").eq("user_id", user_id).order("workout_date", desc=True).execute()
        event_data = response.data
        calendar_events = []
        for i in range(0, len(event_data)):
            current_dict = event_data[i]
            title = current_dict['exercise_type']
            start = current_dict['workout_date']
            calendar_events.append({'title': title, 'start': start})
    if log_type == "Meal":
        response = supabase.table("meals").select("date, meal_name, calories").eq("user_id", user_id).order("date", desc=True).execute()
        event_data = response.data
        calendar_events = []
        for i in range(0, len(event_data)):
            current_dict = event_data[i]
            title = current_dict['meal_name']
            start = current_dict['date']
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
        if log_type == "Workout":
            log_workout(dateClicked["date"], supabase, user_id)
        elif log_type == "Meal":
            log_meal(dateClicked["date"], supabase, user_id)
    except Exception as e:
        pass
