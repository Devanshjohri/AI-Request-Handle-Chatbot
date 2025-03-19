import sqlite3
import streamlit as st
import requests
from leave_AI.nlp_leave_extraction import extract_leave_details
from leave_AI.leave_approval_model import predict_leave_approval

DB_PATH = "database/agent_data.db"
BASE_URL = "http://127.0.0.1:8000"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class LeaveAgent:
    def __init__(self):
        self.name = "leave_agent"

    def process_leave(self, data: dict):
        student_id = data.get("student_id")
        leave_type = data.get("leave_type")
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        reason = data.get("reason")
        
        if not all([student_id, leave_type, start_date, end_date, reason]):
            return {"error": "Missing required fields"}
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO leaves (student_id, leave_type, start_date, end_date, reason, status) VALUES (?, ?, ?, ?, ?, ?)",
            (student_id, leave_type, start_date, end_date, reason, "Pending")
        )
        conn.commit()
        conn.close()
        
        return {"message": "Leave request processed successfully"}
    
    def get_leave_requests(self, student_id=None):
        """Retrieve all leave requests"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leaves WHERE student_id = ?", (student_id,))
        leaves = cursor.fetchall()
        conn.close()
        return [dict(row) for row in leaves]
    
    def reset_leave_status(self, leave_id):
        """Reset leave request status to 'Completed'"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE leaves SET status = 'Completed' WHERE id = ?", (leave_id,))
        conn.commit()
        conn.close()
        return {"message": f"Leave request {leave_id} has been marked as Completed"}

# Initialize agent instance
leave_agent = LeaveAgent()

# ✅ Function to display leave details in Streamlit
def show_leave_details():
    st.subheader("📜 Your Leave Requests")

    if "user_roll" not in st.session_state:
        st.warning("Please enter your Roll Number first.")
        return

    # Fetch leave requests for the logged-in student
    leave_requests = leave_agent.get_leave_requests(st.session_state.user_roll)

    if not leave_requests:
        st.warning("No leave requests found.")
    else:
        # Display leave details in a table
        st.table(leave_requests)

    