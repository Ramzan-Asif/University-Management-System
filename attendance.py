import streamlit as st
import pandas as pd
import database as db
import datetime

def mark_attendance(enrollment_id, attendance_date, status):
    # Check if record exists
    check_query = "SELECT * FROM Attendance WHERE enrollment_id=%s AND attendance_date=%s"
    existing = db.execute_read_query(check_query, (enrollment_id, attendance_date))
    
    if existing:
        query = "UPDATE Attendance SET status=%s WHERE enrollment_id=%s AND attendance_date=%s"
        params = (status, enrollment_id, attendance_date)
    else:
        query = "INSERT INTO Attendance (enrollment_id, attendance_date, status) VALUES (%s, %s, %s)"
        params = (enrollment_id, attendance_date, status)
    
    try:
        db.execute_query(query, params)
    except Exception as e:
        st.error(f"Error marking attendance: {e}")

def get_enrolled_students(course_id, semester):
    query = """
    SELECT e.enrollment_id, s.name, s.student_id
    FROM Enrollments e
    JOIN Students s ON e.student_id = s.student_id
    WHERE e.course_id = %s AND e.semester = %s
    """
    return db.execute_read_query(query, (course_id, semester))

def get_course_attendance(course_id, semester):
    query = """
    SELECT s.name, a.attendance_date, a.status 
    FROM Attendance a
    JOIN Enrollments e ON a.enrollment_id = e.enrollment_id
    JOIN Students s ON e.student_id = s.student_id
    WHERE e.course_id = %s AND e.semester = %s
    ORDER BY a.attendance_date DESC, s.name
    """
    result = db.execute_read_query(query, (course_id, semester))
    return pd.DataFrame(result)

def app():
    st.title("Attendance Management")

    menu = ["Mark Attendance", "View Attendance"]
    choice = st.sidebar.selectbox("Sub-Menu", menu)

    # Common Filters
    courses_map = db.execute_read_query("SELECT course_id, name FROM Courses")
    course_options = {row['name']: row['course_id'] for row in courses_map} if courses_map else {}
    
    if not course_options:
        st.warning("No courses found. Please add courses first.")
        return

    course_name = st.selectbox("Select Course", list(course_options.keys()))
    course_id = course_options[course_name]
    
    semester = st.selectbox("Select Semester", ["Fall 2024", "Spring 2025", "Summer 2025", "Fall 2025"])

    if choice == "Mark Attendance":
        st.subheader(f"Mark Attendance for {course_name} - {semester}")
        attendance_date = st.date_input("Date", datetime.date.today())
        
        students = get_enrolled_students(course_id, semester)
        
        if students:
            with st.form("attendance_form"):
                st.write("Mark Status for each student:")
                status_updates = {}
                
                for student in students:
                    # Default to Present
                    st.write(f"**{student['name']}** (ID: {student['student_id']})")
                    status = st.radio(f"Status for {student['name']}", 
                                      ['Present', 'Absent', 'Late', 'Excused'], 
                                      key=student['enrollment_id'], horizontal=True)
                    status_updates[student['enrollment_id']] = status
                    st.divider()
                
                submitted = st.form_submit_button("Submit Attendance")
                if submitted:
                    count = 0
                    for eid, stat in status_updates.items():
                        mark_attendance(eid, attendance_date, stat)
                        count += 1
                    st.success(f"Attendance marked for {count} students!")
        else:
            st.info("No students enrolled in this course for this semester.")

    elif choice == "View Attendance":
        st.subheader(f"Attendance Log: {course_name}")
        df = get_course_attendance(course_id, semester)
        
        if not df.empty:
            # Pivot table for better view: Rows=Students, Cols=Dates
            pivot_df = df.pivot_table(index='name', columns='attendance_date', values='status', aggfunc='first')
            st.dataframe(pivot_df)
        else:
            st.info("No attendance records found.")
