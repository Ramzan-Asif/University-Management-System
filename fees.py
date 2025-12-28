import streamlit as st
import pandas as pd
import database as db
import datetime

def generate_fee(student_id, semester, amount, due_date):
    query = """
    INSERT INTO Fees (student_id, semester, amount, due_date, status)
    VALUES (%s, %s, %s, %s, 'Pending')
    """
    params = (student_id, semester, amount, due_date)
    try:
        db.execute_query(query, params)
        st.success("Fee request generated successfully!")
    except Exception as e:
        st.error(f"Error generating fee: {e}")

def pay_fee(fee_id, payment_date, amount_paid, fine_amount):
    # Update status to Paid and set payment details
    query = """
    UPDATE Fees 
    SET payment_date=%s, fine_amount=%s, status='Paid'
    WHERE fee_id=%s
    """
    params = (payment_date, fine_amount, fee_id)
    try:
        db.execute_query(query, params)
        st.success(f"Fee paid successfully! (Fine: ${fine_amount})")
    except Exception as e:
        st.error(f"Error processing payment: {e}")

def read_fees():
    query = """
    SELECT f.fee_id, s.name as student_name, f.semester, f.amount, f.due_date, 
           f.payment_date, f.fine_amount, f.status
    FROM Fees f
    JOIN Students s ON f.student_id = s.student_id
    ORDER BY f.due_date DESC
    """
    result = db.execute_read_query(query)
    return pd.DataFrame(result)

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

def app():
    st.title("Fee & Payment Management")

    menu = ["View Fees", "Generate Fee Challan", "Process Payment"]
    choice = st.sidebar.selectbox("Sub-Menu", menu)
    
    student_map = get_students_map()

    if choice == "Generate Fee Challan":
        st.subheader("Generate New Fee")
        with st.form("fee_gen_form"):
            student_name = st.selectbox("Select Student", list(student_map.keys()) if student_map else ["No Students Found"])
            semester = st.selectbox("Semester", ["Fall 2024", "Spring 2025", "Summer 2025", "Fall 2025"])
            amount = st.number_input("Amount ($)", min_value=0.0, step=50.0)
            due_date = st.date_input("Due Date", datetime.date.today() + datetime.timedelta(days=30))
            
            submitted = st.form_submit_button("Generate Challan")
            if submitted and student_map:
                generate_fee(student_map[student_name], semester, amount, due_date)

    elif choice == "View Fees":
        st.subheader("All Fee Records")
        df = read_fees()
        if not df.empty:
            st.dataframe(df)
        else:
            st.info("No fee records found.")

    elif choice == "Process Payment":
        st.subheader("Process Fee Payment")
        # Get Pending Fees only
        query = """
        SELECT f.fee_id, s.name, f.semester, f.amount, f.due_date 
        FROM Fees f
        JOIN Students s ON f.student_id = s.student_id
        WHERE f.status = 'Pending' OR f.status = 'Overdue'
        """
        pending_result = db.execute_read_query(query)
        pending_df = pd.DataFrame(pending_result)
        
        if not pending_df.empty:
            pending_df['label'] = pending_df['name'] + " - " + pending_df['semester'] + " ($" + pending_df['amount'].astype(str) + ")"
            selected_challan = st.selectbox("Select Challan to Pay", pending_df['label'].tolist())
            
            # Get fee info
            fee_info = pending_df[pending_df['label'] == selected_challan].iloc[0]
            fee_id = int(fee_info['fee_id']) # Ensure python int
            due_date = pd.to_datetime(fee_info['due_date']).date()
            base_amount = float(fee_info['amount'])
            
            st.write(f"**Amount Due:** ${base_amount}")
            st.write(f"**Due Date:** {due_date}")
            
            payment_date = st.date_input("Payment Date", datetime.date.today())
            
            # Simple Fine Logic: $10 per day late
            fine = 0.0
            if payment_date > due_date:
                days_late = (payment_date - due_date).days
                fine = float(days_late * 10)
                st.warning(f"Payment is late by {days_late} days. Fine Calculated: ${fine}")
            
            total_payable = base_amount + fine
            st.write(f"**Total Payable:** ${total_payable}")
            
            if st.button("Confirm Payment"):
                pay_fee(fee_id, payment_date, total_payable, fine)
        else:
            st.info("No pending payments found.")
