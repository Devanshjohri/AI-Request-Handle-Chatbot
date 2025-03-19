import sqlite3
import os

DB_PATH = "database/agent_data.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class CertificateAgent:
    def __init__(self):
        self.name = "certificate_agent"

    def fetch_certificate(self, student_id, certificate_type):
        """Retrieve a certificate from the database"""
        conn = get_db_connection()
        cursor = conn.cursor()
    
        # ✅ Check if the certificate exists
        cursor.execute(
        "SELECT file_path FROM certificates WHERE student_id = ? AND certificate_type = ?",
        (student_id, certificate_type),
        )

        result = cursor.fetchone()
    
        conn.close()

        if result  is None:
            return {"message": "No certificate found for the given details. ❌"}
        
        certificate_filename = os.path.basename(result[0]) #✅ Get only the filename
        download_url = f"http://127.0.0.1:8000/download_certificate/{certificate_filename}"  # ✅ Use FastAPI URL

        return {"certificate_url": download_url}

    def upload_certificate(self, student_id, certificate_type, file_path):
        """Store a certificate in the database"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO certificates (student_id, certificate_type, file_path) VALUES (?, ?, ?)", 
                       (student_id, certificate_type, file_path))
        conn.commit()
        conn.close()
        return {"message": f"Certificate '{certificate_type}' uploaded successfully! ✅"}

# Initialize Certificate Agent
certificate_agent = CertificateAgent()
