import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
import os
import cv2
import numpy as np
import time
from hand_ges import HandGesture
from image_override import ImageOverwriter
import concurrent.futures
import copy
import time
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

executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
finished = {"window": False, "gesture": False}

start = 0
while hasFrame:
    # start = time.time()

    hasFrame, frame = capture.read()
    frame = cv2.flip(frame, 1)
    _frame = copy.copy(frame)
    # frame = detector.updateGesture(frame)

    # print(executor.submit(detector.updateGesture, _frame).done())
    # if executor.submit(detector.updateGesture, _frame).done():
    #     # print(1 / (time.time() - start))
    #     # print("a")
    #     # executor.submit(detector.updateGesture, _frame)
    #     # start = time.time()
    #     pass

    executor.submit(detector.updateGesture, _frame)

    ges = detector.getGesture()
    palm = detector.getPalmPos()
    depth = detector.getPalmDepth()
    # if len(detector.frame) != 0:
    #     frame = detector.frame

    cv2.circle(frame, (palm[0], palm[1]), 4, (0, 255, 0), 2)

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

    # print(writer.checkOverlap((int(palm[0]), int(palm[1]))))
    # print(ges, palm, depth)

    cv2.imshow(WINDOW, frame)
    key = cv2.waitKey(1)
    if key == 27:
        break
    # print(1 / (time.time() - start))

capture.release()
executor.shutdown()
# out.release()
cv2.destroyAllWindows()
