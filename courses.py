import streamlit as st
import pandas as pd
import database as db

def create_course(name, credit_hours, dept_id):
    query = """
    INSERT INTO Courses (name, credit_hours, dept_id)
    VALUES (%s, %s, %s)
    """
    params = (name, credit_hours, dept_id)
    try:
        db.execute_query(query, params)
        st.success(f"Course '{name}' added successfully!")
    except Exception as e:
        st.error(f"Error adding course: {e}")

def read_courses():
    query = """
    SELECT c.course_id, c.name, c.credit_hours, d.name as department
    FROM Courses c
    LEFT JOIN Departments d ON c.dept_id = d.dept_id
    """
    result = db.execute_read_query(query)
    return pd.DataFrame(result)

def update_course(course_id, name, credit_hours, dept_id):
    query = """
    UPDATE Courses
    SET name=%s, credit_hours=%s, dept_id=%s
    WHERE course_id=%s
    """
    params = (name, credit_hours, dept_id, course_id)
    try:
        db.execute_query(query, params)
        st.success("Course updated successfully!")
    except Exception as e:
        st.error(f"Error updating course: {e}")

def delete_course(course_id):
    query = "DELETE FROM Courses WHERE course_id = %s"
    params = (course_id,)
    try:
        db.execute_query(query, params)
        st.success("Course deleted successfully!")
    except Exception as e:
        st.error(f"Error deleting course: {e}")

def get_departments_map():
    query = "SELECT dept_id, name FROM Departments"
    result = db.execute_read_query(query)
    dept_map = {}
    if result:
        for row in result:
            if isinstance(row, dict):
                 dept_map[row['name']] = row['dept_id']
            else:
                 dept_map[row[1]] = row[0]
    return dept_map

def app():
    st.title("Manage Courses")

    menu = ["View Courses", "Add Course", "Update Course", "Delete Course"]
    choice = st.sidebar.selectbox("Sub-Menu", menu)

    dept_map = get_departments_map()

    if choice == "Add Course":
        st.subheader("Add New Course")
        with st.form("add_course_form"):
            name = st.text_input("Course Name")
            credit_hours = st.number_input("Credit Hours", min_value=1, max_value=6, step=1)
            
            dept_name = st.selectbox("Department", list(dept_map.keys()) if dept_map else ["No Departments Found"])
            
            submitted = st.form_submit_button("Add Course")
            if submitted:
                if dept_map:
                    create_course(name, credit_hours, dept_map[dept_name])
                else:
                    st.error("Cannot add course without a department.")

    elif choice == "View Courses":
        st.subheader("View All Courses")
        df = read_courses()
        if not df.empty:
            st.dataframe(df)
        else:
            st.info("No courses found.")

    elif choice == "Update Course":
        st.subheader("Update Course Details")
        df = read_courses()
        if not df.empty:
            course_id = st.selectbox("Select Course ID", df['course_id'].tolist())
            
            query = "SELECT * FROM Courses WHERE course_id = %s"
            current_course = db.execute_read_query(query, (course_id,))
            if current_course:
                current_course = current_course[0]
                
                with st.form("update_course_form"):
                    name = st.text_input("Course Name", value=current_course['name'])
                    credit_hours = st.number_input("Credit Hours", min_value=1, max_value=6, value=current_course['credit_hours'])
                    
                    current_dept_id = current_course['dept_id']
                    current_dept_name = next((name for name, id in dept_map.items() if id == current_dept_id), None)
                    
                    if current_dept_name and current_dept_name in dept_map:
                        dept_name = st.selectbox("Department", list(dept_map.keys()), index=list(dept_map.keys()).index(current_dept_name))
                    else:
                        dept_name = st.selectbox("Department", list(dept_map.keys()))
                    
                    submitted = st.form_submit_button("Update")
                    if submitted:
                        update_course(course_id, name, credit_hours, dept_map[dept_name])
        else:
             st.info("No courses to update.")

    elif choice == "Delete Course":
        st.subheader("Delete Course")
        df = read_courses()
        if not df.empty:
            course_id = st.selectbox("Select Course to Delete", df['course_id'].tolist())
            if st.button("Delete"):
                delete_course(course_id)
        else:
            st.info("No courses to delete.")
