import streamlit as st
import pandas as pd
import database as db

def update_marks(enrollment_id, quiz, midterm, final):
    # Logic moved to DB Trigger (before_enrollment_update)
    # We only update the raw marks, the DB calculates Total and Grade.

    query = """
    UPDATE Enrollments 
    SET quiz_marks=%s, midterm_marks=%s, final_marks=%s
    WHERE enrollment_id=%s
    """
    params = (quiz, midterm, final, enrollment_id)
    try:
        db.execute_query(query, params)
        st.success(f"Marks submitted! Grade will be calculated by Database Trigger.")
    except Exception as e:
        st.error(f"Error updating marks: {e}")

def read_marks():
    query = """
    SELECT e.enrollment_id, s.name as student_name, c.name as course_name, e.semester, 
           e.quiz_marks, e.midterm_marks, e.final_marks, e.total_marks, e.grade
    FROM Enrollments e
    JOIN Students s ON e.student_id = s.student_id
    JOIN Courses c ON e.course_id = c.course_id
    ORDER BY c.name, s.name
    """
    result = db.execute_read_query(query)
    return pd.DataFrame(result)

def app():
    st.title("Examination & Results")

    menu = ["View Results", "Enter Marks"]
    choice = st.sidebar.selectbox("Sub-Menu", menu)

    if choice == "Enter Marks":
        st.subheader("Enter Marks for Enrolled Students")
        df = read_marks()
        
        if not df.empty:
            # Dropdown to select student/course combo
            df['label'] = df['student_name'] + " - " + df['course_name'] + " (" + df['semester'] + ")"
            enrollment_label = st.selectbox("Select Student", df['label'].tolist())
            
            # Get current data for default values
            current_row = df[df['label'] == enrollment_label].iloc[0]
            enrollment_id = int(current_row['enrollment_id']) # Ensure python int
            
            with st.form("marks_form"):
                st.write(f"Entering marks for: **{enrollment_label}**")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    quiz = st.number_input("Quiz Marks (0-20)", min_value=0.0, max_value=20.0, value=float(current_row['quiz_marks']))
                with col2:
                    midterm = st.number_input("Midterm Marks (0-30)", min_value=0.0, max_value=30.0, value=float(current_row['midterm_marks']))
                with col3:
                    final = st.number_input("Final Marks (0-50)", min_value=0.0, max_value=50.0, value=float(current_row['final_marks']))
                
                submitted = st.form_submit_button("Update Marks & Calculate Grade")
                if submitted:
                    update_marks(enrollment_id, quiz, midterm, final)

        else:
            st.info("No enrollments found to enter marks.")

    elif choice == "View Results":
        st.subheader("Class Results")
        df = read_marks()
        if not df.empty:
            st.dataframe(df)
        else:
            st.info("No results found.")
