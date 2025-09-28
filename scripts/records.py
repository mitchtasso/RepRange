import streamlit as st
import scripts.exercises as exercises

all_workouts = exercises.exerciseTypes
all_workouts.sort()

def page(supabase, user_id):
    st.title("📙Records")
    recordFilter = st.selectbox("Record Type", ["Workouts", "Meals"])
    
    if recordFilter == "Workouts":
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
                
                saveButton, deleteButton, emptyCol = record.columns([1,1.1,6.8])
                with saveButton:
                    if st.button(':green[Save]', key=editButtonName, width='stretch'):
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
                    if st.button(':red[Delete]', key=workoutButtonName,width='stretch'):
                            data = workouts[i]['id']
                            supabase.table("workouts").delete().eq("id", data).execute()
                            st.rerun()
        else:
            st.write("No workouts logged yet.")
    
    elif recordFilter == "Meals":
        mealFilter = st.text_input("Filter by Meal Name", placeholder="None", value=None)
        if mealFilter == None:
            response = supabase.table("meals").select("date, meal_name, calories, protein, id").eq("user_id", user_id).order("date", desc=True).execute()
        else:
            response = supabase.table("meals").select("date, meal_name, calories, protein, id").eq("user_id", user_id).ilike("meal_name", mealFilter).order("date", desc=True).execute()
        meals = response.data
        
        labels = st.container(border=True)
        col1, col2, col3, col4 = labels.columns([1,3,0.75,0.75])
        with col1:
            st.write("Meal Date")
        with col2:
            st.write("Meal Name")
        with col3:
            st.write("Calories")
        with col4:
            st.write("Protein")
        
        if meals:
            for i in range(len(meals)):
                containerName = f"meal{i}"
                delButtonName = f"delbutton{i}"
                editButtonName = f"editbutton{i}"
                record = st.container(border=True, key=containerName)
                dateCol, mealCol, calCol, proteinCol = record.columns([1,3,0.75,0.75])
                with dateCol:
                    dateValue = st.date_input(label="", value=meals[i]['date'], key=f"dateCol{i}", label_visibility='collapsed')
                with mealCol:
                    mealValue = st.text_input(label="", placeholder=meals[i]['meal_name'], key=f"mealCol{i}", label_visibility='collapsed', value=None)
                with calCol:
                    calValue = st.number_input(label="", value=meals[i]['calories'], key=f"calCol{i}", label_visibility='collapsed', min_value=0, max_value=10000)
                with proteinCol:
                    proteinValue = st.number_input(label="", value=meals[i]['protein'], key=f"proteinCol{i}", label_visibility='collapsed', min_value=0, max_value=10000)
                
                saveButton, deleteButton, emptyCol = record.columns([1,1.1,6.8])
                with saveButton:
                    if st.button(':green[Save]', key=editButtonName, width='stretch'):
                            try:
                                data = meals[i]['id']
                                if mealValue == None:
                                    mealValue = meals[i]['meal_name']
                                    
                                supabase.table("meals").update({"date": dateValue.isoformat(), 
                                                                "meal_name": mealValue,
                                                                "calories": calValue,
                                                                "protein": proteinValue}).eq("id", data).execute()
                                record.success("Updated record")
                                st.rerun()
                            except Exception as e:
                                record.error(f"Failed to update record: {e}")
                with deleteButton:
                    if st.button(':red[Delete]', key=delButtonName,width='stretch'):
                            data = meals[i]['id']
                            supabase.table("meals").delete().eq("id", data).execute()
                            st.rerun()
        else:
            st.write("No meals logged yet.")