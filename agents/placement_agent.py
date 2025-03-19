import sqlite3

DB_PATH = "database/agent_data.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class PlacementAgent:
    def __init__(self):
        self.name = "placement_agent"

    def get_job_openings(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM job_openings")
        jobs = cursor.fetchall()
        conn.close()
        
        return {"message": "Job openings retrieved", "data": [dict(row) for row in jobs]}

    def get_company_visits(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM company_visits")
        visits = cursor.fetchall()
        conn.close()
        
        return {"message": "Company visit schedule retrieved", "data": [dict(row) for row in visits]}

# Initialize agent instance
placement_agent = PlacementAgent()
