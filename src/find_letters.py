import cv2
import numpy as np

img = cv2.imread("data/real/line1.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
H, W = gray.shape

blur = cv2.GaussianBlur(gray, (5, 5), 0)
bw = cv2.adaptiveThreshold(
    blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 8)
bw = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))

contours, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
boxes = []
for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)
    if 0.2 * H <= h <= 0.95 * H and 0.2 * h <= w <= 1.6 * h:
        boxes.append((x, y, w, h))
boxes.sort()

for n, (x, y, w, h) in enumerate(boxes, 1):
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.putText(img, str(n), (x, max(15, y - 4)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

cv2.imwrite("data/real/line1_boxes.png", img)
cv2.imwrite("data/real/line1_bw.png", bw)
print("letters found:", len(boxes))