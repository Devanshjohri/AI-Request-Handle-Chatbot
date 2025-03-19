import sqlite3

DB_PATH = "database/agent_data.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class FeeAgent:
    def __init__(self):
        self.name = "fee_agent"

    def get_fee_details(self, student_id):
        if not student_id:
            return {"error": "Missing student ID"}
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fees WHERE student_id = ?", (student_id,))
        fee_data = cursor.fetchone()
        conn.close()
        
        if fee_data:
            return {"message": "Fee details retrieved", "data": dict(fee_data)}
        return {"error": "No fee records found"}

# Initialize agent instance
fee_agent = FeeAgent()
