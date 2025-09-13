# scripts/database_utils.py
import sqlite3
import pickle
import os
from datetime import datetime

# Database file path
DB_DIR = "database"
DB_PATH = os.path.join(DB_DIR, "students.db")
os.makedirs(DB_DIR, exist_ok=True)

def init_db():
    """Initialize the database with students and logs tables."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create students table
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            usn TEXT PRIMARY KEY,
            name TEXT,
            encodings BLOB,
            id_text TEXT,
            id_photo_path TEXT
        )
    ''')
    
    # Create access logs table
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usn TEXT,
            name TEXT,
            time TEXT,
            result TEXT,
            face_img_path TEXT,
            id_img_path TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def add_or_update_student(usn, name, encodings, id_text='', id_photo_path=''):
    """
    Add a new student or update existing student record.
    encodings: list of face_recognition encodings (numpy arrays)
    """
    enc_blob = pickle.dumps(encodings)  # Convert list of numpy arrays to blob
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO students (usn, name, encodings, id_text, id_photo_path)
        VALUES (?, ?, ?, ?, ?)
    ''', (usn, name, enc_blob, id_text, id_photo_path))
    conn.commit()
    conn.close()

def fetch_student_by_usn(usn):
    """Fetch a single student by USN."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT usn, name, encodings, id_text, id_photo_path FROM students WHERE usn=?', (usn,))
    row = c.fetchone()
    conn.close()
    if row:
        encodings = pickle.loads(row[2])
        return {
            'usn': row[0],
            'name': row[1],
            'encodings': encodings,
            'id_text': row[3],
            'id_photo_path': row[4]
        }
    return None

def load_all_students():
    """Return all students as a list of dictionaries."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT usn, name, encodings, id_text, id_photo_path FROM students')
    rows = c.fetchall()
    conn.close()

    students = []
    for usn, name, enc_blob, id_text, id_photo_path in rows:
        encodings = pickle.loads(enc_blob)
        students.append({
            'usn': usn,
            'name': name,
            'encodings': encodings,
            'id_text': id_text,
            'id_photo_path': id_photo_path
        })
    return students

def log_access(usn, name, result, face_img_path='', id_img_path=''):
    """Log an access attempt."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT INTO logs (usn, name, time, result, face_img_path, id_img_path)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (usn, name, timestamp, result, face_img_path, id_img_path))
    conn.commit()
    conn.close()
