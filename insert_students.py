import sqlite3
import os

# Connect to the database
conn = sqlite3.connect("database/students.db")
cursor = conn.cursor()

# Function to insert a student
def insert_student(sr_no, name):
    # Path to student's face image (dataset folder)
    photo_path = f"dataset/{sr_no}/0.jpg"  # Use the first image in folder
    # Path to student's ID card
    id_card_path = f"id_cards/{sr_no}.png"

    cursor.execute("""
        INSERT OR REPLACE INTO students (sr_no, name, photo_path, id_card_path)
        VALUES (?, ?, ?, ?)
    """, (sr_no, name, photo_path, id_card_path))
    conn.commit()
    print(f"✅ Inserted: {sr_no} - {name}")

# Add your students here
insert_student("241358", "Prakruthi")
insert_student("241354", "Lakshmi ")
insert_student("241355", "V Likitha ")
insert_student("241352", "Nithya Shree ")
insert_student("23-0668", "Namitha CS ")

conn.close()
print("✅ All students inserted successfully.")
