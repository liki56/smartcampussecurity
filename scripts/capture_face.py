# scripts/capture_faces.py
import cv2, os
out_root = "dataset"
os.makedirs(out_root, exist_ok=True)

usn = input("Enter USN (unique id): ").strip()
name = input("Enter name: ").strip()
folder = os.path.join(out_root, f"{usn}_{name}")
os.makedirs(folder, exist_ok=True)

cap = cv2.VideoCapture(0)
print("Press 'c' to capture face, 'q' to quit")
count = len(os.listdir(folder))
while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow("Capture Faces", frame)
    k = cv2.waitKey(1) & 0xFF
    if k == ord('c'):
        path = os.path.join(folder, f"{count}.jpg")
        cv2.imwrite(path, frame)
        print("Saved", path)
        count += 1
    elif k == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
