import sqlite3

DB_PATH = "database/agent_data.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class ExamAgent:
    def __init__(self):
        self.name = "exam_agent"

    def get_academic_calendar(self):
        return {"message": "Fetching academic calendar details..."}

    def get_backlog_exam_info(self, student_id):
        if not student_id:
            return {"error": "Missing student ID"}
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM backlog_exams WHERE student_id = ?", (student_id,))
        backlog_data = cursor.fetchall()
        conn.close()
        
        return {"message": "Backlog exam details", "data": [dict(row) for row in backlog_data]}

# Initialize agent instance
exam_agent = ExamAgent()
