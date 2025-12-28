import streamlit as st
import pandas as pd
import database as db

def create_department(name):
    query = "INSERT INTO Departments (name) VALUES (%s)"
    params = (name,)
    try:
        db.execute_query(query, params)
        st.success(f"Department '{name}' added successfully!")
    except Exception as e:
        st.error(f"Error adding department: {e}")

def read_departments():
    query = "SELECT * FROM Departments"
    result = db.execute_read_query(query)
    # Convert list of dicts (if using dictionary cursor) or tuples to DataFrame
    return pd.DataFrame(result)

def update_department(dept_id, new_name):
    query = "UPDATE Departments SET name = %s WHERE dept_id = %s"
    params = (new_name, dept_id)
    try:
        db.execute_query(query, params)
        st.success(f"Department updated successfully!")
    except Exception as e:
        st.error(f"Error updating department: {e}")

def delete_department(dept_id):
    query = "DELETE FROM Departments WHERE dept_id = %s"
    params = (dept_id,)
    try:
        db.execute_query(query, params)
        st.success("Department deleted successfully!")
    except Exception as e:
        st.error(f"Error deleting department: {e}")

def app():
    st.title("Manage Departments")

    menu = ["View Departments", "Add Department", "Update Department", "Delete Department"]
    choice = st.sidebar.selectbox("Sub-Menu", menu)

    if choice == "Add Department":
        st.subheader("Add New Department")
        with st.form("add_dept_form"):
            name = st.text_input("Department Name")
            submitted = st.form_submit_button("Add Department")
            if submitted:
                if name:
                    create_department(name)
                else:
                    st.warning("Please enter a department name.")

    elif choice == "View Departments":
        st.subheader("View All Departments")
        df = read_departments()
        if not df.empty:
            st.dataframe(df)
        else:
            st.info("No departments found.")

    elif choice == "Update Department":
        st.subheader("Update Department Details")
        df = read_departments()
        if not df.empty:
            dept_id = st.selectbox("Select Department ID", df['dept_id'].tolist())
            current_name = df[df['dept_id'] == dept_id]['name'].values[0]
            
            with st.form("update_dept_form"):
                new_name = st.text_input("New Department Name", value=current_name)
                submitted = st.form_submit_button("Update")
                if submitted:
                    update_department(dept_id, new_name)
        else:
            st.info("No departments to update.")

    elif choice == "Delete Department":
        st.subheader("Delete Department")
        df = read_departments()
        if not df.empty:
            dept_id = st.selectbox("Select Department to Delete", df['dept_id'].tolist())
            st.warning("Warning: Deleting a department might be restricted if it has associated students/courses.")
            if st.button("Delete"):
                delete_department(dept_id)
        else:
            st.info("No departments to delete.")
