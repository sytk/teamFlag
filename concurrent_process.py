import cv2
import numpy as np

from hand_ges import HandGesture


def update_gesture(title, frame):
    frame = cv2.flip(frame, 1)
    detector = HandGesture()

    frame = detector.updateGesture(frame)
    ges = detector.getGesture()
    palm = detector.getPalmPos()
    depth = detector.getPalmDepth()

    print(ges, palm, depth)
    cv2.imshow(title, frame)


