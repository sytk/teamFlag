import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
import os
import cv2
import numpy as np
import time
from hand_ges import HandGesture
from image_override import ImageOverwriter

WINDOW = "Hand Tracking"

cv2.namedWindow(WINDOW)
capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if capture.isOpened():
    hasFrame, frame = capture.read()
else:
    hasFrame = False

detector = HandGesture()

writer = ImageOverwriter()
writer.addImage("./dog.jpeg")
writer.addImage("./dog.jpeg")
writer.setPosition(0, 300, 300)
writer.setPosition(1, 200, 200)

while hasFrame:
    start = time.time()

    hasFrame, frame = capture.read()
    frame = cv2.flip(frame, 1)

    frame = detector.updateGesture(frame)
    ges = detector.getGesture()
    palm = detector.getPalmPos()
    depth = detector.getPalmDepth()
    print(ges)

    writer.updateGesture(ges)
    prev_ges = writer.getPrevGesture()
    overlapped_images = writer.checkOverlap((int(palm[0]), int(palm[1])))

    if ges != 5:
        writer.releaseImage()

    if ges == 4:
        writer.showImage(int(palm[0]), int(palm[1]))
        writer.releaseImage()

    if ges == 6:
        if len(overlapped_images) > 0:
            writer.hideImage(overlapped_images[0])
        writer.releaseImage()

    elif ges == 5:
        if prev_ges != 5 or writer.isGrab():
            if len(overlapped_images) > 0:
                writer.grabImage(overlapped_images[0], depth)
                writer.setPosition(overlapped_images[0], int(palm[0]), int(palm[1]))
            else:
                writer.releaseImage()

    frame = writer.overwrite(frame)

    print(writer.checkOverlap((int(palm[0]), int(palm[1]))))
    # print(ges, palm, depth)

    cv2.imshow(WINDOW, frame)
    key = cv2.waitKey(1)
    if key == 27:
        break
    print(1 / (time.time() - start))

capture.release()
# out.release()
cv2.destroyAllWindows()
