import streamlit as st
from datetime import datetime, timedelta, timezone

now_utc = datetime.now(timezone.utc)
seven_days_ago_utc = now_utc - timedelta(days=7)

def page(supabase, user_id):
    st.title(f" Welcome to RepRange!")
    
    st.write("A platform for logging workouts, meals, and tracking your progress along the way")
    
    widget1, widget2 = st.columns([1,2])
    with widget1:
        weekWorkouts = supabase.table("workouts").select("*").gte("workout_date", seven_days_ago_utc.isoformat()).lte("workout_date", now_utc.isoformat()).execute()
        w1 = st.container(border=True)
        w1.write("Total Workouts (Past Week)")
        w1.title(len(weekWorkouts.data))
        
        weekMeals = supabase.table("meals").select("*").gte("date", seven_days_ago_utc.isoformat()).lte("date", now_utc.isoformat()).execute()
        w2 = st.container(border=True)
        w2.write("Total Meals (Past Week)")
        w2.title(len(weekMeals.data))
        
    with widget2:
        recentWorkout = supabase.table("workouts").select("*").eq("user_id", user_id).order("workout_date", desc=True).limit(1).execute()
        w3 = st.container(border=True)
        w3.write("Workout Logged (Most Recent)")
        try:
            check = recentWorkout.data[0]['workout_date']
            workDate, exercise, weight, rep, sets = w3.columns([0.75,1,0.75,0.5,0.5])
            with workDate:
                st.write("Date")
                st.write(f"{recentWorkout.data[0]['workout_date']}")
            with exercise:
                st.write("Exercise")
                st.write(f"{recentWorkout.data[0]['exercise_type']}")
            with weight:
                st.write("Weight")
                st.write(f"{recentWorkout.data[0]['weight']} lb(s)")
            with rep:
                st.write("Reps")
                st.write(f"{recentWorkout.data[0]['repetitions']}")
            with sets:
                st.write("Sets")
                st.write(f"{recentWorkout.data[0]['sets']}")
        except Exception as e:
            w3.write("No workouts logged.")
        
        recentMeal = supabase.table("meals").select("*").eq("user_id", user_id).order("date", desc=True).limit(1).execute()
        w4 = st.container(border=True)
        w4.write("Meal Logged (Most Recent)")
        try:
            check2 = recentMeal.data[0]['date']
            mealDate, mealName, cal, protein = w4.columns(4)
            with mealDate:
                st.write("Date")
                st.write(f"{recentMeal.data[0]['date']}")
            with mealName:
                st.write("Meal Name")
                st.write(f"{recentMeal.data[0]['meal_name']}")
            with cal:
                st.write("Calories")
                st.write(f"{recentMeal.data[0]['calories']} cal")
            with protein:
                st.write("Protein")
                st.write(f"{recentMeal.data[0]['protein']} (g)")
        except:
            w4.write("No meals logged.")