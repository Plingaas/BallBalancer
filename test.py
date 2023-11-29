import cv2
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

get, img = cap.read()
h, w, _ = img.shape

while True:
    _, frame = cap.read()
    cv2.imshow("Frame", frame)
    cv2.waitKey(1)