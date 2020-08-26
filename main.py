import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import os
import cv2
import numpy as np
import time
from hand_ges import HandGesture

WINDOW = "Hand Tracking"

cv2.namedWindow(WINDOW)
capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
# capture.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
# capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if capture.isOpened():
    hasFrame, frame = capture.read()
else:
    hasFrame = False

# fourcc = cv2.VideoWriter_fourcc(*'XVID')
# out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))

detector = HandGesture()

while hasFrame:
    start = time.time()

    hasFrame, frame = capture.read()
    frame = cv2.flip(frame, 1)

    frame = detector.updateGesture(frame)
    ges, palm = detector.getGesture()

    print(ges)

    cv2.imshow(WINDOW, frame)
    key = cv2.waitKey(1)
    if key == 27:
        break
    print(1 / (time.time() - start))

capture.release()
# out.release()
cv2.destroyAllWindows()
