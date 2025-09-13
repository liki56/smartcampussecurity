# scripts/face_train.py
import os
import pickle
import face_recognition
from scripts.database_utils import add_or_update_student

# Path to dataset and output pickle file
DATASET_DIR = "dataset"
ENCODINGS_PATH = os.path.join("models", "face_encodings.pkl")

# Dictionary to store encodings in memory
face_data = {}

# Iterate through each person folder in dataset
for person_folder in sorted(os.listdir(DATASET_DIR)):
    person_path = os.path.join(DATASET_DIR, person_folder)
    if not os.path.isdir(person_path):
        continue

    usn_name = person_folder  # Expected format: USN_Name
    encodings_list = []

    # Iterate through all images for this person
    for image_file in os.listdir(person_path):
        image_path = os.path.join(person_path, image_file)
        try:
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)

            if encodings:
                encodings_list.append(encodings[0])
        except Exception as e:
            print(f"⚠️ Skipping {image_path}: {e}")

    # If encodings found, save to dictionary and update database
    if encodings_list:
        face_data[usn_name] = encodings_list

        # Split USN and Name
        parts = usn_name.split("_")
        usn = parts[0]
        name = "_".join(parts[1:]) if len(parts) > 1 else usn_name

        # Add or update student in database
        add_or_update_student(usn, name, encodings_list, id_text='', id_photo_path='')
        print(f"✅ Added {usn_name} with {len(encodings_list)} encodings")

# Save all encodings to pickle
os.makedirs(os.path.dirname(ENCODINGS_PATH), exist_ok=True)
with open(ENCODINGS_PATH, "wb") as f:
    pickle.dump(face_data, f)

print(f"💾 Saved all face encodings to {ENCODINGS_PATH}")
