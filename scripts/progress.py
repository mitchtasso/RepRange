import streamlit as st
import scripts.exercises as exercises
import pandas as pd

all_workouts = exercises.exerciseTypes
all_workouts.sort()

def page(supabase, user_id):
    st.title("📈Progress")
    progressType = st.selectbox('Tool', options=['Strength Tracker', 'Macro Tracker'])
    if progressType == 'Strength Tracker':
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
    elif progressType == 'Macro Tracker':
        response = supabase.table("meals").select("*").eq("user_id", user_id).execute()
        meals = response.data
        if meals:
            st.subheader("Progress by Calories")
            df = pd.DataFrame(meals)
            df['date'] = pd.to_datetime(df['date'])
            weekly_duration = df.groupby('date')['calories'].sum()
            st.line_chart(weekly_duration, x_label='Date', y_label='Calories')

            st.subheader("Progress by Protein")
            df = pd.DataFrame(meals)
            df['date'] = pd.to_datetime(df['date'])
            weekly_duration = df.groupby('date')['protein'].sum()
            st.line_chart(weekly_duration, x_label='Date', y_label='Protein')

