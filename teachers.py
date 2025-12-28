import streamlit as st
import pandas as pd
import database as db

def create_teacher(name, email, phone, dept_id, hire_date):
    query = """
    INSERT INTO Teachers (name, email, phone, dept_id, hire_date)
    VALUES (%s, %s, %s, %s, %s)
    """
    params = (name, email, phone, dept_id, hire_date)
    try:
        db.execute_query(query, params)
        st.success(f"Teacher '{name}' added successfully!")
    except Exception as e:
        st.error(f"Error adding teacher: {e}")

def read_teachers():
    # Join with Departments to show Department Name instead of ID
    query = """
    SELECT t.teacher_id, t.name, t.email, t.phone, d.name as department, t.hire_date
    FROM Teachers t
    LEFT JOIN Departments d ON t.dept_id = d.dept_id
    """
    result = db.execute_read_query(query)
    return pd.DataFrame(result)

def update_teacher(teacher_id, name, email, phone, dept_id, hire_date):
    query = """
    UPDATE Teachers
    SET name=%s, email=%s, phone=%s, dept_id=%s, hire_date=%s
    WHERE teacher_id=%s
    """
    params = (name, email, phone, dept_id, hire_date, teacher_id)
    try:
        db.execute_query(query, params)
        st.success("Teacher updated successfully!")
    except Exception as e:
        st.error(f"Error updating teacher: {e}")

def delete_teacher(teacher_id):
    query = "DELETE FROM Teachers WHERE teacher_id = %s"
    params = (teacher_id,)
    try:
        db.execute_query(query, params)
        st.success("Teacher deleted successfully!")
    except Exception as e:
        st.error(f"Error deleting teacher: {e}")

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
    st.title("Manage Teachers")

    menu = ["View Teachers", "Add Teacher", "Update Teacher", "Delete Teacher"]
    choice = st.sidebar.selectbox("Sub-Menu", menu)

    dept_map = get_departments_map()

    if choice == "Add Teacher":
        st.subheader("Add New Teacher")
        with st.form("add_teacher_form"):
            name = st.text_input("Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            
            # Department Dropdown
            dept_name = st.selectbox("Department", list(dept_map.keys()) if dept_map else ["No Departments Found"])
            hire_date = st.date_input("Hire Date")
            
            submitted = st.form_submit_button("Add Teacher")
            if submitted:
                if dept_map:
                    create_teacher(name, email, phone, dept_map[dept_name], hire_date)
                else:
                    st.error("Cannot add teacher without a department. Please create a department first.")

    elif choice == "View Teachers":
        st.subheader("View All Teachers")
        df = read_teachers()
        if not df.empty:
            st.dataframe(df)
        else:
            st.info("No teachers found.")

    elif choice == "Update Teacher":
        st.subheader("Update Teacher Details")
        df = read_teachers()
        if not df.empty:
            teacher_id = st.selectbox("Select Teacher ID", df['teacher_id'].tolist())
            
            # Fetch current teacher data
            query = "SELECT * FROM Teachers WHERE teacher_id = %s"
            current_teacher = db.execute_read_query(query, (teacher_id,))
            if current_teacher:
                current_teacher = current_teacher[0]
                
                with st.form("update_teacher_form"):
                    name = st.text_input("Name", value=current_teacher['name'])
                    email = st.text_input("Email", value=current_teacher['email'])
                    phone = st.text_input("Phone", value=current_teacher['phone'])
                    
                    # Find current department name for default value
                    current_dept_id = current_teacher['dept_id']
                    current_dept_name = next((name for name, id in dept_map.items() if id == current_dept_id), None)
                    
                    if current_dept_name and current_dept_name in dept_map:
                        dept_name = st.selectbox("Department", list(dept_map.keys()), index=list(dept_map.keys()).index(current_dept_name))
                    else:
                        dept_name = st.selectbox("Department", list(dept_map.keys()))

                    hire_date = st.date_input("Hire Date", value=pd.to_datetime(current_teacher['hire_date']))
                    
                    submitted = st.form_submit_button("Update")
                    if submitted:
                        update_teacher(teacher_id, name, email, phone, dept_map[dept_name], hire_date)
        else:
             st.info("No teachers to update.")

    elif choice == "Delete Teacher":
        st.subheader("Delete Teacher")
        df = read_teachers()
        if not df.empty:
            teacher_id = st.selectbox("Select Teacher to Delete", df['teacher_id'].tolist())
            if st.button("Delete"):
                delete_teacher(teacher_id)
        else:
            st.info("No teachers to delete.")
