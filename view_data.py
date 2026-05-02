import sqlite3

# Connect to the database
conn = sqlite3.connect("founderlens.db")
cursor = conn.cursor()

# Grab all the data from your table
cursor.execute("SELECT id, pitch_text, fit_score, timestamp FROM telemetry_logs")
rows = cursor.fetchall()

print("\n" + "="*50)
print(" 🚀 FOUNDERLENS TELEMETRY DATABASE SECURE")
print("="*50)

if not rows:
    print("Database is currently empty. Run a diagnostic in the browser first!")
else:
    for row in rows:
        print(f"IDEA ID   : {row[0]}")
        print(f"PITCH     : {row[1][:60]}...") # Shows the first 60 characters
        print(f"FIT SCORE : {row[2]}")
        print(f"TIMESTAMP : {row[3]}")
        print("-" * 50)

conn.close()