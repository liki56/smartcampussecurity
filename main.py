# main.py
import cv2, pickle, os, time
from scripts.id_ocr import detect_card_and_crop, ocr_text, extract_card_face_encoding
from scripts.database_utils import load_all_students
from scripts.gate_control import init_hardware, open_gate, alert_buzzer
import face_recognition, numpy as np

# Load DB students
students = load_all_students()
# Flatten encodings for quick matching
known_encodings = []
known_usns = []
for s in students:
    for e in s['encodings']:
        known_encodings.append(e)
        known_usns.append(s['usn'])

TOL_FACE = 0.50
TOL_CARD_PHOTO = 0.50

init_hardware()
cap = cv2.VideoCapture(0)
print("Starting main loop. Press q to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        continue
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locs = face_recognition.face_locations(rgb, model='hog')
    face_encs = face_recognition.face_encodings(rgb, face_locs)
    for (top,right,bottom,left), face_enc in zip(face_locs, face_encs):
        # match face
        dists = face_recognition.face_distance(known_encodings, face_enc)
        if len(dists)==0:
            match_usn = None
            name_label = "Unknown"
        else:
            i = np.argmin(dists)
            if dists[i] <= TOL_FACE:
                match_usn = known_usns[i]
                name_label = match_usn
            else:
                match_usn = None
                name_label = "Unknown"

        # Draw face box
        cv2.rectangle(frame, (left,top), (right,bottom), (0,255,0), 2)
        cv2.putText(frame, name_label, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        # Try detect ID card in area below face (heuristic)
        roi_y_start = bottom
        roi_y_end = min(frame.shape[0], bottom + 300)
        roi_x_start = max(0, left - 50)
        roi_x_end = min(frame.shape[1], right + 50)
        roi = frame[roi_y_start:roi_y_end, roi_x_start:roi_x_end]

        if roi.size != 0:
            card_crop, bbox = detect_card_and_crop(roi)
            if card_crop is not None:
                cx,cy,cw,ch = bbox
                # Draw card box on main frame
                cv2.rectangle(frame, (roi_x_start+cx, roi_y_start+cy), (roi_x_start+cx+cw, roi_y_start+cy+ch), (255,0,0), 2)
                # OCR text
                text = ocr_text(card_crop)
                card_enc = extract_card_face_encoding(card_crop)

                # Verification logic:
                card_ok = False
                face_ok = False
                # check OCR contains matched USN or name (simple substring match)
                if match_usn:
                    # find student record from students
                    srec = next((s for s in students if s['usn'] == match_usn), None)
                    if srec:
                        # check OCR vs DB text
                        if srec['usn'].lower() in text.lower() or srec['name'].lower() in text.lower():
                            card_ok = True
                        # compare card photo to student's encodings
                        if card_enc is not None:
                            dists_card = face_recognition.face_distance(srec['encodings'], card_enc)
                            if len(dists_card)>0 and min(dists_card) <= TOL_CARD_PHOTO:
                                face_ok = True

                # Decision
                if match_usn and card_ok and face_ok:
                    cv2.putText(frame, "ACCESS GRANTED", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,255,0), 3)
                    print("ACCESS GRANTED for", match_usn)
                    open_gate(duration=2)
                else:
                    cv2.putText(frame, "ACCESS DENIED", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,255), 3)
                    print("ACCESS DENIED. match_usn:", match_usn, "card_ok:", card_ok, "face_ok:", face_ok)
                    alert_buzzer(duration=1)

    cv2.imshow("SmartGate", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
