import streamlit as st
import pandas as pd
import database as db

def create_student(name, email, phone, dept_id, admission_date):
    query = """
    INSERT INTO Students (name, email, phone, dept_id, admission_date)
    VALUES (%s, %s, %s, %s, %s)
    """
    params = (name, email, phone, dept_id, admission_date)
    try:
        db.execute_query(query, params)
        st.success(f"Student '{name}' added successfully!")
    except Exception as e:
        st.error(f"Error adding student: {e}")

def read_students():
    # Join with Departments to show Department Name instead of ID
    query = """
    SELECT s.student_id, s.name, s.email, s.phone, d.name as department, s.admission_date
    FROM Students s
    LEFT JOIN Departments d ON s.dept_id = d.dept_id
    """
    result = db.execute_read_query(query)
    return pd.DataFrame(result)

def update_student(student_id, name, email, phone, dept_id, admission_date):
    query = """
    UPDATE Students
    SET name=%s, email=%s, phone=%s, dept_id=%s, admission_date=%s
    WHERE student_id=%s
    """
    params = (name, email, phone, dept_id, admission_date, student_id)
    try:
        db.execute_query(query, params)
        st.success("Student updated successfully!")
    except Exception as e:
        st.error(f"Error updating student: {e}")

def delete_student(student_id):
    query = "DELETE FROM Students WHERE student_id = %s"
    params = (student_id,)
    try:
        db.execute_query(query, params)
        st.success("Student deleted successfully!")
    except Exception as e:
        st.error(f"Error deleting student: {e}")

def get_departments_map():
    # Helper to get a dictionary of {dept_name: dept_id} for dropdowns
    query = "SELECT dept_id, name FROM Departments"
    result = db.execute_read_query(query)
    dept_map = {}
    if result:
        for row in result:
             # Handle both dictionary cursor and tuple cursor just in case
            if isinstance(row, dict):
                 dept_map[row['name']] = row['dept_id']
            else:
                 dept_map[row[1]] = row[0]
    return dept_map

def app():
    st.title("Manage Students")

    menu = ["View Students", "Add Student", "Update Student", "Delete Student"]
    choice = st.sidebar.selectbox("Sub-Menu", menu)

    dept_map = get_departments_map()

    if choice == "Add Student":
        st.subheader("Add New Student")
        with st.form("add_student_form"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            
            # Department Dropdown
            dept_name = st.selectbox("Department", list(dept_map.keys()) if dept_map else ["No Departments Found"])
            admission_date = st.date_input("Admission Date")
            
            submitted = st.form_submit_button("Add Student")
            if submitted:
                if dept_map:
                    create_student(name, email, phone, dept_map[dept_name], admission_date)
                else:
                    st.error("Cannot add student without a department. Please create a department first.")

    elif choice == "View Students":
        st.subheader("View All Students")
        df = read_students()
        if not df.empty:
            st.dataframe(df)
        else:
            st.info("No students found.")

    elif choice == "Update Student":
        st.subheader("Update Student Details")
        df = read_students()
        if not df.empty:
            student_id = st.selectbox("Select Student ID", df['student_id'].tolist())
            
            # Fetch current student data
            query = "SELECT * FROM Students WHERE student_id = %s"
            current_student = db.execute_read_query(query, (student_id,))
            if current_student:
                current_student = current_student[0] # First record
                
                with st.form("update_student_form"):
                    name = st.text_input("Name", value=current_student['name'])
                    email = st.text_input("Email", value=current_student['email'])
                    phone = st.text_input("Phone", value=current_student['phone'])
                    
                    # Find current department name for default value
                    current_dept_id = current_student['dept_id']
                    current_dept_name = next((name for name, id in dept_map.items() if id == current_dept_id), None)
                    
                    if current_dept_name and current_dept_name in dept_map:
                        dept_name = st.selectbox("Department", list(dept_map.keys()), index=list(dept_map.keys()).index(current_dept_name))
                    else:
                        dept_name = st.selectbox("Department", list(dept_map.keys()))

                    admission_date = st.date_input("Admission Date", value=pd.to_datetime(current_student['admission_date']))
                    
                    submitted = st.form_submit_button("Update")
                    if submitted:
                        update_student(student_id, name, email, phone, dept_map[dept_name], admission_date)
        else:
            st.info("No students to update.")

    elif choice == "Delete Student":
        st.subheader("Delete Student")
        df = read_students()
        if not df.empty:
            student_id = st.selectbox("Select Student to Delete", df['student_id'].tolist())
            if st.button("Delete"):
                delete_student(student_id)
        else:
            st.info("No students to delete.")
