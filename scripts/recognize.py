import cv2
import face_recognition
import pickle
import numpy as np
from scripts.database_utils import fetch_student_by_usn
from scripts import gate_control
from scripts import siren_alert
import time

ENC_PATH = "models/face_encodings.pkl"

# Load known face encodings
with open(ENC_PATH, "rb") as f:
    known_faces = pickle.load(f)

known_encodings = []
known_usns = []

for usn_name, enc_list in known_faces.items():
    usn = usn_name.split("_")[0]
    for enc in enc_list:
        known_encodings.append(enc)
        known_usns.append(usn)

# Initialize webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Cannot open webcam")
    exit()

print("✅ Webcam opened. Press 'q' to quit.")

recognized_usns = set()
label_timers = {}   # usn -> remaining frames
denied_cache = set()  # to avoid siren spam
LABEL_FRAMES = 30   # ~1 sec display at 30fps

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to grab frame")
        break

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for face_encoding, face_location in zip(face_encodings, face_locations):
        matches = face_recognition.compare_faces(known_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_encodings, face_encoding)

        best_match_index = np.argmin(face_distances) if len(face_distances) > 0 else None

        if best_match_index is not None and matches[best_match_index]:
            usn = known_usns[best_match_index]
            student = fetch_student_by_usn(usn)
            name = student['name'] if student else usn
            status = "Access Granted ✅"

            if usn not in recognized_usns:
                recognized_usns.add(usn)
                try:
                    gate_control.open_gate()
                except:
                    print("⚠️ Gate control not available")

            label_timers[usn] = LABEL_FRAMES
        else:
            usn = None
            name = "Unknown"
            status = "Access Denied ❌"

            # 🚨 Trigger siren ONCE for new unknown detection
            if name not in denied_cache:
                denied_cache.add(name)
                siren_alert.play_siren(duration=3)

        # Scale face location back to original frame size
        top, right, bottom, left = [v * 4 for v in face_location]
        color = (0, 255, 0) if status.startswith("Access Granted") else (0, 0, 255)
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.putText(frame, f"{name}: {status}", (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Show labels for recognized USNs
    for usn in list(label_timers.keys()):
        if label_timers[usn] > 0:
            student = fetch_student_by_usn(usn)
            name = student['name'] if student else usn
            cv2.putText(frame, f"{name}: Access Granted ✅",
                        (20, 30 + 30 * list(label_timers.keys()).index(usn)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            label_timers[usn] -= 1
        else:
            del label_timers[usn]

    cv2.imshow('Face Recognition', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
