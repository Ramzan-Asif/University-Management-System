import streamlit as st
import pandas as pd
import database as db
import datetime

def register_student(student_id, course_id, semester, enrollment_date):
    query = """
    INSERT INTO Enrollments (student_id, course_id, semester, enrollment_date)
    VALUES (%s, %s, %s, %s)
    """
    params = (student_id, course_id, semester, enrollment_date)
    try:
        db.execute_query(query, params)
        st.success("Student enrolled successfully!")
    except Exception as e:
        if "Duplicate entry" in str(e):
            st.error("Student is already enrolled in this course for this semester.")
        else:
            st.error(f"Error enrolling student: {e}")

def read_enrollments():
    query = """
    SELECT e.enrollment_id, s.name as student_name, c.name as course_name, e.semester, e.enrollment_date, e.grade
    FROM Enrollments e
    JOIN Students s ON e.student_id = s.student_id
    JOIN Courses c ON e.course_id = c.course_id
    """
    result = db.execute_read_query(query)
    return pd.DataFrame(result)

def drop_enrollment(enrollment_id):
    query = "DELETE FROM Enrollments WHERE enrollment_id = %s"
    params = (enrollment_id,)
    try:
        db.execute_query(query, params)
        st.success("Enrollment dropped successfully!")
    except Exception as e:
        st.error(f"Error dropping enrollment: {e}")

def get_students_map():
    query = "SELECT student_id, name FROM Students"
    result = db.execute_read_query(query)
    student_map = {}
    if result:
        for row in result:
             if isinstance(row, dict):
                 student_map[f"{row['name']} (ID: {row['student_id']})"] = row['student_id']
             else:
                 student_map[f"{row[1]} (ID: {row[0]})"] = row[0]
    return student_map

def get_courses_map():
    query = "SELECT course_id, name FROM Courses"
    result = db.execute_read_query(query)
    course_map = {}
    if result:
        for row in result:
             if isinstance(row, dict):
                 course_map[f"{row['name']} (ID: {row['course_id']})"] = row['course_id']
             else:
                 course_map[f"{row[1]} (ID: {row[0]})"] = row[0]
    return course_map

def app():
    st.title("Manage Enrollments")

    menu = ["View Enrollments", "Register Student to Course", "Drop Course"]
    choice = st.sidebar.selectbox("Sub-Menu", menu)

    student_map = get_students_map()
    course_map = get_courses_map()

    if choice == "Register Student to Course":
        st.subheader("Register Student")
        with st.form("register_form"):
            student_name = st.selectbox("Select Student", list(student_map.keys()) if student_map else ["No Students Found"])
            course_name = st.selectbox("Select Course", list(course_map.keys()) if course_map else ["No Courses Found"])
            semester = st.selectbox("Semester", ["Fall 2024", "Spring 2025", "Summer 2025", "Fall 2025"])
            enrollment_date = st.date_input("Enrollment Date", datetime.date.today())
            
            submitted = st.form_submit_button("Enroll")
            if submitted:
                if student_map and course_map:
                    register_student(student_map[student_name], course_map[course_name], semester, enrollment_date)
                else:
                    st.error("Students and Courses must exist to enroll.")

    elif choice == "View Enrollments":
        st.subheader("Current Enrollments")
        df = read_enrollments()
        if not df.empty:
            st.dataframe(df)
        else:
            st.info("No enrollments found.")

    elif choice == "Drop Course":
        st.subheader("Drop Student from Course")
        df = read_enrollments()
        if not df.empty:
            # Create a readable string for selection
            df['label'] = df['student_name'] + " - " + df['course_name'] + " (" + df['semester'] + ")"
            enrollment_label = st.selectbox("Select Enrollment to Drop", df['label'].tolist())
            
            # Get ID
            enrollment_id = df[df['label'] == enrollment_label]['enrollment_id'].values[0]
            
            if st.button("Drop Course"):
                drop_enrollment(enrollment_id)
        else:
            st.info("No enrollments to drop.")
