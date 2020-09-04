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
writer = ImageOverwriter()

cv2.namedWindow(WINDOW)
capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if capture.isOpened():
    hasFrame, frame = capture.read()
else:
    hasFrame = False

detector = HandGesture()

pc = PdfController()
pdf = pc.convertToImage("hacku.pdf")
writer.addImages(pdf)
writer.setPosition(0, None)
writer.addImage("./kame.jpeg")
writer.setPosition(1, None)
# writer.addImage("./cat.jpeg")
# writer.setPosition(2, None)

executor = concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count())

start = 0
future_list = []
skeleton_flag = False
pointer_flag = False
panetrate_flag = False
bgimg = None
bgframe = None

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
    depth = detector.getPalmDepth(writer.isGrab())
    finger = detector.getFingerPos()
    print(ges, palm, depth)

    # cv2.circle(frame, (palm[0], palm[1]), 4, (0, 255, 0), 2)

    if skeleton_flag:
        frame = detector.drawPalmFrame(frame)
    
    if panetrate_flag == True:
        if  bgframe is None:
            while True:
                hasFrame, frame = capture.read()
                frame = cv2.flip(frame, 1)
                bgframe = frame.copy()
                cv2.putText(frame, "Press the a key to take a background photo.", (10, 100),cv2.FONT_HERSHEY_PLAIN, 3,(0, 0, 0), 3, cv2.LINE_AA)

                cv2.imshow(WINDOW, frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('a'):
                    bgimg = bgframe
                    #cv2.destroyWindows()
                    break
        elif bgframe is not None:
            bgimg = bgframe
        
    elif panetrate_flag == False:
        bgimg = None
        print(bgimg)

    frame = writer.overwrite(frame, ges, palm, depth, bgimg)

    if pointer_flag:
        cv2.circle(frame, (finger[0], finger[1]), 4, (0, 0, 255), 2)

    cv2.imshow(WINDOW, frame)

    key = cv2.waitKey(1)
    if key == 27:
        break
    elif key == ord('s'):
        skeleton_flag = not skeleton_flag
    elif key == ord('p'):
        pointer_flag = not pointer_flag
    elif key == ord('a'):
        panetrate_flag = not panetrate_flag
        bg = None
        #print("panetrate_flag" + panetrate_flag)

    print(1 / (time.time() - start))

executor.shutdown()
capture.release()
cv2.destroyAllWindows()
