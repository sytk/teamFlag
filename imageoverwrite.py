# coding: utf-8
import cv2

# カメラ準備
cap = cv2.VideoCapture(0)
# カメラ情報の取得
fps    = cap.get(cv2.CAP_PROP_FPS)
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
# 入力する画像のパス指定。
# imagepath = "/Users/sho/work/hacku2020/images/P8222296.JPG"
imagepath = "./dog.jpeg"
# 入力画像を読み込み
image = cv2.imread(imagepath,cv2.IMREAD_UNCHANGED)
#入力画像のサイズ指定
rescale = 3
imgwidth = int(width/3)#426
imgheight = int(height/3)#240
# 像をリサイズ
resized_image = cv2.resize(image, (imgwidth,imgheight))
reimgheight, reimgwidth = resized_image.shape[:2]
print(reimgheight)
print(reimgwidth)
cutimage = resized_image.copy()

#マウスの座標
dptx = None
dpty = None


#マウスイベントが起こるとここへ来る
def printCoor(event,x,y,flags,param):
    global dptx, dpty #クリックした時の座標
    #　マウスが左クリックされたとき
    if event == cv2.EVENT_LBUTTONDOWN:
        dptx = x
        dpty = y
        print("Push")
        outsideflag = 0

#画像のウインドウに名前をつけ、コールバック関数をセット
cv2.namedWindow('image')
cv2.setMouseCallback('image',printCoor)

# 無限ループ
while True:
    # キー押下で終了
    key = cv2.waitKey(1)
    if key != -1:
        break

    # カメラ画像読み込み
    ret, frame = cap.read()
    #frame[0:imgheight, 0:imgwidth] = img
    #print(ptx)
    if dptx != None and dpty != None:
        outsideflag = 0 # はみ出ているかフラグ
        leftoutsideimg = 0 # 左側の画面外に出ている部分のサイズ
        rightoutsideimg = 0
        upoutsideimg = 0
        downoutsideimg = 0
        #デフォルト値を設定
        #cutimage = cutimage[0:reimgheight, 0:reimgwidth]
        cutimage1 = 0
        cutimage2 = reimgheight
        cutimage3 = 0
        cutimage4 = reimgwidth

        #print(dptx,dpty)
        #左にはみ出てたら
        if (dptx - int(imgwidth/2) < 0):
            outsideflag = 1
            leftoutsideimg = int(imgwidth/2) - dptx
            #print(leftoutsideimg)
            cutimage3 = leftoutsideimg

        #右にはみ出てたら
        if (width < dptx - int(imgwidth/2) + imgwidth):
            outsideflag = 1
            rightoutsideimg = dptx - int(imgwidth/2) + imgwidth - width
            #print(rightoutsideimg)
            cutimage4 = imgwidth - int(rightoutsideimg)

        #左にはみ出てたら
        if (dpty - int(imgheight/2) < 0):
            outsideflag = 1
            upoutsideimg = int(imgheight/2) - dpty
            #print(upoutsideimg)
            cutimage1 = upoutsideimg

        #下にはみ出てたら
        if (height < dpty - int(imgheight/2) + imgheight):
            outsideflag = 1
            downoutsideimg = dpty - int(imgheight/2) + imgheight - height
            cutimage2 = imgheight - downoutsideimg

        #はみ出ているフラグが立ってたら
        if (outsideflag == 1):
            #上記の結果から画像を切り取り
            cutimg = cutimage[cutimage1:cutimage2, cutimage3:cutimage4]
            #cutheight, cutwidth = cutimg.shape[:2] #カットした写真のサイズ
            #カットした写真を合成
            #frame[カーソルの位置Y-画像の半分 : カーソルの位置Y-画像の半分の場所に画像の高さ分を追加、カーソルの位置X-画像の半分 : カーソルの位置X-画像の半分の場所に画像の高さ分を追加]
            frame[dpty - int(imgheight/2) + upoutsideimg:dpty - int(imgheight/2) + imgheight - downoutsideimg, dptx - int(imgwidth/2)+ leftoutsideimg:dptx - int(imgwidth/2) + imgwidth - rightoutsideimg] = cutimg

        #　外にはみ出る物がない時
        else:
            cutimg = resized_image[0:reimgheight, 0:reimgwidth]
            #frame[カーソルの位置Y-画像の半分 : カーソルの位置Y-画像の半分の場所に画像の高さ分を追加、カーソルの位置X-画像の半分 : カーソルの位置X-画像の半分の場所に画像の高さ分を追加]
            frame[dpty - int(imgheight/2):dpty - int(imgheight/2) + imgheight, dptx - int(imgwidth/2):dptx - int(imgwidth/2) + imgwidth] = cutimg

    # frame = frame[:,::-1]
    # 画像表示
    cv2.imshow('image', frame)

# 終了処理
cap.release()
cv2.destroyAllWindows()

#複数ういんどう
#端で消えないように
