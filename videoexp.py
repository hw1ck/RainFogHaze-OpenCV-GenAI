import cv2

cap = cv2.VideoCapture("test.mp4")
ret, frame = cap.read()
if ret:
    cv2.imwrite("frame.jpg", frame)
cap.release()