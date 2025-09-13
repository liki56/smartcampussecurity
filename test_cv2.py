import cv2

# Print OpenCV version
print("OpenCV version:", cv2.__version__)

# Try to open the default camera (webcam)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Cannot open camera")
    exit()

print("✅ Camera opened successfully. Press 'q' to exit.")

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to grab frame")
        break

    # Display the resulting frame
    cv2.imshow('Test Camera', frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture
cap.release()
cv2.destroyAllWindows()
print("✅ Test finished successfully.")
