import cv2

cap = cv2.VideoCapture("/dev/video0", cv2.CAP_V4L2)
print("Opened:", cap.isOpened())

count = 0
while count < 5:
    ret, frame = cap.read()
    print("Read:", ret, "Frame shape:", None if frame is None else frame.shape)
    count += 1