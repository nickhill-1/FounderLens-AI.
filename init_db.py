import sqlite3

def setup_database():
    print("INITIALIZING DATABASE PROTOCOL...")
    
    # 1. This creates a file called 'founderlens.db' in your folder.
    # If the file already exists, it just connects to it.
    conn = sqlite3.connect("founderlens.db")
    
    # 2. The cursor is the tool we use to send SQL commands to the database.
    cursor = conn.cursor()
    
    # 3. Write the SQL to create your table. 
    # AUTOINCREMENT means idea #1 gets ID 1, idea #2 gets ID 2, etc.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS telemetry_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pitch_text TEXT NOT NULL,
        problem_score REAL,
        solution_score REAL,
        fit_score REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 4. Save (commit) the changes and close the connection.
    conn.commit()
    conn.close()
    
    print("SUCCESS: founderlens.db compiled and telemetry_logs table secured.")

if __name__ == "__main__":
    setup_database()