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
capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


if capture.isOpened():
    hasFrame, frame = capture.read()
else:
    hasFrame = False

detector = HandGesture()

writer = ImageOverwriter()
writer.addImage("./dog.jpeg")


#マウスの座標
dptx = 200
dpty = 200

#マウスイベントが起こるとここへ来る
def printCoor(event,x,y,flags,param):
    global dptx, dpty #クリックした時の座標
    if event == cv2.EVENT_LBUTTONDOWN:
        dptx = x
        dpty = y

cv2.setMouseCallback("Hand Tracking",printCoor)

x = 100
y = 100
while hasFrame:
    start = time.time()

    hasFrame, frame = capture.read()
    frame = cv2.flip(frame, 1)

    frame = detector.updateGesture(frame)
    ges = detector.getGesture()
    palm = detector.getPalmPos()
    depth = detector.getPalmDepth()

    if(ges=="swing"):
        y, x = int(palm[1]), int(palm[0])

    # print(palm)
    writer.setPosition(y,x)
    # writer.setPosition(int(palm[1]), int(palm[0]))
    # writer.setPosition(dpty, dptx)

    frame = writer.overwrite(frame)

    # print(ges, palm, depth)

    cv2.imshow(WINDOW, frame)
    key = cv2.waitKey(1)
    if key == 27:
        break
    print(1 / (time.time() - start))

capture.release()
# out.release()
cv2.destroyAllWindows()
