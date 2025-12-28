import streamlit as st
import database as db
import departments
import students
import teachers
import courses
import enrollments
import grades
import attendance
import fees

def main():
    st.set_page_config(page_title="University Management System", layout="wide")
    st.title("University Management System")

    menu = ["Dashboard", "Students", "Teachers", "Courses", "Departments", "Enrollments", "Results", "Attendance", "Fees"]
    choice = st.sidebar.selectbox("Navigation", menu)

    if choice == "Dashboard":
        st.subheader("Dashboard")
        st.write("Welcome to the University Management System.")
        
        # Quick Stats
        try:
            student_count = len(db.execute_read_query("SELECT * FROM Students") or [])
            teacher_count = len(db.execute_read_query("SELECT * FROM Teachers") or [])
            course_count = len(db.execute_read_query("SELECT * FROM Courses") or [])
            dept_count = len(db.execute_read_query("SELECT * FROM Departments") or [])
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Students", student_count)
            col2.metric("Teachers", teacher_count)
            col3.metric("Courses", course_count)
            col4.metric("Departments", dept_count)
            
            st.success("Database Connection Successful!")
            
        except Exception as e:
            st.error(f"Error connecting to database: {e}")

    elif choice == "Students":
        students.app()

    elif choice == "Teachers":
        teachers.app()

    elif choice == "Courses":
        courses.app()
        
    elif choice == "Departments":
        departments.app()

    elif choice == "Enrollments":
        enrollments.app()

    elif choice == "Results":
        grades.app()

    elif choice == "Attendance":
        attendance.app()

    elif choice == "Fees":
        fees.app()

if __name__ == '__main__':
    main()
