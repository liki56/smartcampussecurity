# scripts/id_ocr.py
import cv2, pytesseract, face_recognition, numpy as np

def detect_card_and_crop(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edges = cv2.Canny(blur, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in sorted(contours, key=cv2.contourArea, reverse=True)[:15]:
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
        if len(approx) == 4:
            x,y,w,h = cv2.boundingRect(approx)
            # reject tiny boxes
            if w*h < 5000:
                continue
            crop = frame[y:y+h, x:x+w]
            return crop, (x,y,w,h)
    return None, None

def ocr_text(card_img):
    gray = cv2.cvtColor(card_img, cv2.COLOR_BGR2GRAY)
    _, thr = cv2.threshold(gray,0,255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    text = pytesseract.image_to_string(thr)
    return text

def extract_card_face_encoding(card_img):
    rgb = cv2.cvtColor(card_img, cv2.COLOR_BGR2RGB)
    locs = face_recognition.face_locations(rgb)
    if not locs:
        return None
    encs = face_recognition.face_encodings(rgb, locs)
    if encs:
        return encs[0]
    return None
