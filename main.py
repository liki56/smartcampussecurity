# main.py
import cv2, threading
import face_recognition
import numpy as np

from scripts.database_utils import load_all_students
from scripts.gate_control import init_hardware, open_gate, alert_buzzer, cleanup
from scripts.siren_alert import play_siren  # Siren sound module

# Load DB students
students = load_all_students()

# Flatten encodings for quick matching
known_encodings = []
known_usns = []
for s in students:
    for e in s['encodings']:
        known_encodings.append(e)
        known_usns.append(s['usn'])

# Threshold for face recognition
TOL_FACE = 0.50

# Initialize hardware
init_hardware()

# Start webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Cannot open webcam")
    exit()

print("Starting main loop. Press 'q' to quit.")

# Serial number tracking for access granted
serial_counter = 1
serial_mapping = {}  # usn -> serial no
label_timers = {}    # usn -> remaining frames
LABEL_FRAMES = 30    # ~1 second at 30 FPS

# Track unknown faces to prevent repeated siren
recent_unknowns = set()
SIREN_COOLDOWN_FRAMES = 30

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locs = face_recognition.face_locations(rgb, model='hog')
        face_encs = face_recognition.face_encodings(rgb, face_locs)

        # Temporary set to track current frame unknowns
        current_frame_unknowns = set()

        for (top, right, bottom, left), face_enc in zip(face_locs, face_encs):
            # Check if face matches known IDs
            match_usn = None
            if len(known_encodings) > 0:
                dists = face_recognition.face_distance(known_encodings, face_enc)
                i = np.argmin(dists)
                if dists[i] <= TOL_FACE:
                    match_usn = known_usns[i]

            if match_usn:  # ✅ Known ID
                if match_usn not in serial_mapping:
                    serial_mapping[match_usn] = serial_counter
                    serial_counter += 1
                serial_no = serial_mapping[match_usn]

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, f"{match_usn} - ACCESS GRANTED", (left, top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                print(f"✅ ACCESS GRANTED for {match_usn} (Serial {serial_no})")
                open_gate(duration=2)
                label_timers[match_usn] = LABEL_FRAMES

            else:  # ❌ Unknown ID
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.putText(frame, "UNKNOWN - ACCESS DENIED", (left, top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                print("❌ ACCESS DENIED - Unknown ID")
                alert_buzzer(duration=1)

                # Use face coordinates as temporary ID
                face_id = (top, right, bottom, left)
                current_frame_unknowns.add(face_id)

                if face_id not in recent_unknowns:
                    threading.Thread(target=play_siren, daemon=True).start()
                    recent_unknowns.add(face_id)

        # Update recent_unknowns
        recent_unknowns = recent_unknowns.intersection(current_frame_unknowns)

        # Show persistent access labels
        for usn in list(label_timers.keys()):
            if label_timers[usn] > 0:
                cv2.putText(frame, f"{usn}: Access Granted ✅",
                            (20, 30 + 30*list(label_timers.keys()).index(usn)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                label_timers[usn] -= 1
            else:
                del label_timers[usn]

        # Display frame safely
        try:
            cv2.imshow("SmartGate", frame)
        except cv2.error:
            pass

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    try:
        cv2.destroyAllWindows()
    except cv2.error:
        pass
    cleanup()
    print("System exited cleanly.")
