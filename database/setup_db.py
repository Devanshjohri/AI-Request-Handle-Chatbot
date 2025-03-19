import sqlite3

def setup_database():
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect("database/agent_data.db")
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leaves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        leave_type TEXT,
        start_date TEXT,
        end_date TEXT,
        reason TEXT,
        status TEXT DEFAULT 'Pending'
    )
""")

    
    # 🔹 Certificates Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS certificates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        certificate_type TEXT NOT NULL,
        file_path TEXT NOT NULL
        )
    """)

    # 🔹 Academic Data Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS academic_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT,
            event_name TEXT,
            event_date TEXT
        )
    """)

    # 🔹 Backlog Exam Data Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS backlog_exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            subject TEXT,
            exam_date TEXT
        )
    """)

    # 🔹 Fee Data Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fee_data (
            student_id TEXT PRIMARY KEY,
            fee_status TEXT
        )
    """)

    # 🔹 Placement Job Openings Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_openings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT,
            role TEXT,
            salary TEXT,
            apply_deadline TEXT
        )
    """)

    # 🔹 Placement Company Visits Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT,
            visit_date TEXT
        )
    """)

    # 🔹 Compliance Table (Student Complaints, Forms)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS compliance_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            complaint_text TEXT,
            status TEXT DEFAULT 'Pending'
        )
    """)

    # Commit changes and close connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_database()