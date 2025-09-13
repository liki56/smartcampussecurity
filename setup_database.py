import sqlite3
import os

# --- Step 1: Create Database and Table ---
db_path = "database/students.db"
os.makedirs("database", exist_ok=True)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    sr_no TEXT PRIMARY KEY,
    name TEXT,
    photo_path TEXT,
    id_card_path TEXT
)
""")

conn.commit()
print("✅ Database and table created successfully.")
