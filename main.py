import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
import os
import cv2
import numpy as np
import time
from hand_ges import HandGesture
from image_override import ImageOverwriter
from pdf_controller import PdfController
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
writer.setPosition(0, (300, 300))
writer.addImage("./dog.jpeg")
writer.setPosition(1, (200, 200))

# pc = PdfController()
# pdf = pc.convertToImage("IoTLT.pdf")
# for i, image in enumerate(pdf):
#     writer.addImage(image)
#     writer.setPositionOutScreen(i)

executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
finished = {"window": False, "gesture": False}

start = 0
while hasFrame:
    start = time.time()

    hasFrame, frame = capture.read()
    frame = cv2.flip(frame, 1)

    #普通に処理するとき
    frame = detector.updateGesture(frame)

    #並列処理にするとき
    # _frame = copy.copy(frame)
    # executor.submit(detector.updateGesture, _frame)

    ges = detector.getGesture()
    palm = detector.getPalmPos()
    depth = detector.getPalmDepth()

    cv2.circle(frame, (palm[0], palm[1]), 4, (0, 255, 0), 2)

    frame = writer.overwrite(frame, ges, palm, depth)

    print(ges, palm, depth)

    cv2.imshow(WINDOW, frame)
    key = cv2.waitKey(1)
    if key == 27:
        break
    print(1 / (time.time() - start))

capture.release()
executor.shutdown()
# out.release()
cv2.destroyAllWindows()
