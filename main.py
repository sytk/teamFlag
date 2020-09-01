# coding: utf-8
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

pc = PdfController()
pdf = pc.convertToImage("hacku.pdf")
writer.addImages(pdf)
writer.setPosition(0, None)

writer.addImage("./dog.jpeg")
writer.setPosition(1, None)
writer.addImage("./cat.jpeg")
writer.setPosition(2, None)

executor = concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count())
finished = {"window": False, "gesture": False}

start = 0
future_list = []
Skeletonflag = False

while hasFrame:
    start = time.time()

    hasFrame, frame = capture.read()
    frame = cv2.flip(frame, 1)

    #普通に処理するとき
    # frame = detector.updateGesture(frame)

    #並列処理にするとき
    _frame = copy.copy(frame)
    future_list = [f for f in future_list if f.done() == False]
    if len(future_list) < os.cpu_count():
        future_list.append(executor.submit(detector.updateGesture, _frame))
    print(len(future_list))

    ges = detector.getGesture()
    palm = detector.getPalmPos()
    depth = detector.getPalmDepth()
    finger = detector.getFingerPos()

    cv2.circle(frame, (palm[0], palm[1]), 4, (0, 255, 0), 2)

    if Skeletonflag == True: 
        points = detector.points
        connections = detector.connections
        THICKNESS = detector.THICKNESS
        POINT_COLOR = detector.POINT_COLOR
        CONNECTION_COLOR = detector.CONNECTION_COLOR

        if points is not None:
            #points = [point/scale for point in points]
            for point in points:
                x, y = point
                cv2.circle(frame, (int(x), int(y)), THICKNESS * 2, POINT_COLOR, THICKNESS)
            for connection in connections:
                x0, y0 = points[connection[0]]
                x1, y1 = points[connection[1]]
                cv2.line(frame, (int(x0), int(y0)), (int(x1), int(y1)), CONNECTION_COLOR, THICKNESS)

    frame = writer.overwrite(frame, ges, palm, depth)

    if ges == 1:
        cv2.circle(frame, (finger[0], finger[1]), 4, (0, 0, 255), 2)

    print(ges, palm, depth)

    cv2.imshow(WINDOW, frame)
    key = cv2.waitKey(1)
    if key == 27:
        break
    elif key == ord('s'):
        if Skeletonflag == False:
            Skeletonflag = True
        elif Skeletonflag == True:
            Skeletonflag = False
    print(1 / (time.time() - start))

executor.shutdown()
capture.release()
# out.release()
cv2.destroyAllWindows()
