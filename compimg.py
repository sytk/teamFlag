import numpy as np
import cv2
import matplotlib.pyplot as plt

def save_frame_camera_key():
    capture = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("can not use camera")
        caprelease()
        exit()
    print("cを押して背景写真を撮影\n")
    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        cv2.imshow("window_name", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            bgimg = frame
            break
        elif key == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            exit()
    #cap.release()
    #cv2.destroyAllWindows()
    return bgimg

cap = cv2.VideoCapture(0)
bgimg = save_frame_camera_key()
#bgimg = cv2.flip(bgimg, 1)
bggray = cv2.cvtColor(bgimg, cv2.COLOR_BGR2GRAY)
#bgblur = cv2.blur(bggray,(30,30))
bgblur = cv2.GaussianBlur(bggray,(5,5),5)
bgblur = cv2.blur(bgblur,(30,30))
#n=1
while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    imggray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #bokasi
    #imgblur = cv2.blur(imggray,(30,30))
    imgblur = cv2.GaussianBlur(imggray,(5,5),5)
    imgblur = cv2.blur(imgblur,(30,30))
    #sabun
    subimg = cv2.subtract(bgblur, imgblur)
    #画像の二値化
    mask = cv2.threshold(subimg, 0, 255, cv2.THRESH_BINARY)[1]
    #mask2bgra = cv2.cvtColor(mask, cv2.COLOR_BGR2BGRA)                     # -1はAlphaを含んだ形式(0:グレー, 1:カラー)
    #mask2bgra[:, :, 3] = np.where(np.all(mask2bgra == 0, axis=-1), 0, 255)  # 白色のみTrueを返し、Alphaを0にする
    #mask = cv2.cvtColor(mask2bgra, cv2.COLOR_BGRA2BGR)  
    #imgのマスク合成画像作成
    imgmask = cv2.bitwise_and(frame, frame,mask=mask)
    
    # 白 (255, 255, 255) のピクセルを取得する。
    white_pixels = (imgmask == (0, 0, 0)).all(axis=-1)
    # 白のピクセルを黒 (0, 0, 0) にする。
    imgmask[white_pixels] = (130, 170, 180)
    #imgmask2bgra = cv2.cvtColor(imgmask, cv2.COLOR_BGR2BGRA)
    #mask2bgra[:, :, 3] = 128
    #imgmask = cv2.cvtColor(mask2bgra, cv2.COLOR_BGRA2BGR)
    #img[:, :, 3] = np.where(np.all(img == 255, axis=-1), 0, 255)
    #imgmask2bgra[:, :, 3] = np.where(np.all(imgmask2bgra == 0, axis=-1), 0, 255)  # 白色のみTrueを返し、Alphaを0にする
    # マスク画像の白黒を反転
    turnmask = cv2.bitwise_not(mask)
    #color_lower = np.array([0, 0, 0, 255])                 # 抽出する色の下限(BGR形式)
    #color_upper = np.array([0, 0, 0, 255])                 # 抽出する色の上限(BGR形式)
    #img_mask = cv2.inRange(imgmask2bgra, color_lower, color_upper)    # 範囲からマスク画像を作成
    ########imgmask2bgra = cv2.bitwise_not(imgmask2bgra, imgmask2bgra, mask=turnmask)      # 元画像とマスク画像の演算(背景を白くする)

    #color_lower = np.array([1, 1, 1, 255])                 # 抽出する色の下限(BGR形式)
    #color_upper = np.array([255, 255, 255, 255])                 # 抽出する色の上限(BGR形式)
    #img_mask = cv2.inRange(imgmask2bgra, color_lower, color_upper)    # 範囲からマスク画像を作成
    #imgmask2bgra[:,:,3] = 128

    #color_lower = np.array([1, 1, 1, 255])                 # 抽出する色の下限(BGR形式)
    #color_upper = np.array([255, 255, 255, 255])                 # 抽出する色の上限(BGR形式)
    ##img_mask = cv2.inRange(imgmask2bgra, color_lower, color_upper)    # 範囲からマスク画像を作成
    #ima_mask[i][j][3] = 128
    #imgmask2bgra

    #width, height = imgmask2bgra.shape[:2]

    #mask3 = imgmask2bgra[:,:,3]  # アルファチャンネルだけ抜き出す。
    #mask3 = cv2.cvtColor(mask3, cv2.COLOR_GRAY2BGR)  # 3色分に増やす。
    #mask3 = mask3 / 255  # 0-255だと使い勝手が悪いので、0.0-1.0に変更。

    #imgmask2bgra = imgmask2bgra[:,:,:3]  # アルファチャンネルは取り出しちゃったのでもういらない。

    #bgimg[0:height:, 0:width] *= 1 - mask3  # 透過率に応じて元の画像を暗くする。
    #bgimg[0:height:, 0:width] += imgmask2bgra * mask3  # 貼り付ける方の画像に透過率をかけて加算。


    #bgimg2 = cv2.cvtColor(bgimg, cv2.COLOR_BGR2BGRA)

    # bgからimg_msknの部分を切り出す
    bgmask = cv2.bitwise_and(bgimg, bgimg,mask=turnmask)

    # img_src1、img_src2の切り出し画像を合成
    #frame4 = cv2.addWeighted(imgmask, 0.3, bgimg, 1, 0)
    #frame1 = cv2.addWeighted(imgmask2bgra, 0.5, bgimg2, 1, 0) #-100にする暗くなる
    #frame2 = cv2.addWeighted(imgmask2bgra, 1, bgimg2, 1, 0)
    #frame3 = cv2.addWeighted(imgmask2bgra, 1, bgimg2, 0.5, 0)
    #frame2 = cv2.addWeighted(imgmask2bgra, 0.2, bgimg2, 0.7, 50)
    #frame3 = cv2.addWeighted(imgmask2bgra, 0.2, bgimg2, 0.8, 50)
    #compimg = cv2.bitwise_or(imgmask,bgmask)
    frame = cv2.addWeighted(imgmask, 0.3, bgimg, 0.7, 0)

    cv2.imshow("frame1", frame)
    #cv2.imshow("frame2", frame2)
    #cv2.imshow("frame3", frame3)
    #cv2.imshow("frame", frame4)
    
    #n = n+1
    #print(n)
    #if n== 50:
    #    cv2.imwrite("/Users/sho/work/alpha.png", imgmask2bgra)
    #    print("hoson")

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        
        break
cap.release()
cv2.destroyAllWindows()




