import sqlite3

DB_PATH = "database/agent_data.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class ComplianceAgent:
    def __init__(self):
        self.name = "compliance_agent"

    def submit_complaint(self, data):
        student_id = data.get("student_id")
        complaint_text = data.get("complaint")
        
        if not student_id or not complaint_text:
            return {"error": "Missing required fields"}
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO complaints (student_id, complaint_text) VALUES (?, ?)",
            (student_id, complaint_text)
        )
        conn.commit()
        conn.close()
        
        return {"message": "Complaint submitted successfully"}

# Initialize agent instance
compliance_agent = ComplianceAgent()
