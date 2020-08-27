import cv2

class ImageOverwriter():
    def __init__(self):
        self.image_list = []

    def addImage(self, path):
        img = cv2.imread(path,cv2.IMREAD_UNCHANGED)
        h = int(img.shape[0]/4)
        w = int(img.shape[1]/4)
        resized_image = cv2.resize(img, (w,h))

        dict = {"path":path, "img":resized_image, "scale":1, "state":1, "pos":(None,None)}
        dict["pos"] = (200,200)
        self.image_list.append(dict)

    def setPosition(self, x, y):
        self.image_list[0]["pos"] = (x,y)

    def overwrite(self, frame):

        for image in self.image_list:
            if image["pos"][0] == None or image["pos"][1] == None:
                image["state"] == 0
            if image["state"] == 1:
                print(frame.shape)
                cutimage = image["img"]
                dptx = image["pos"][1]
                dpty = image["pos"][0]

                width = frame.shape[1]
                height = frame.shape[0]

                outsideflag = 0 # はみ出ているかフラグ
                leftoutsideimg = 0 # 左側の画面外に出ている部分のサイズ
                rightoutsideimg = 0
                upoutsideimg = 0
                downoutsideimg = 0
                #デフォルト値を設定
                #cutimage = cutimage[0:reimgheight, 0:reimgwidth]

                cutimage1 = 0
                cutimage2 = cutimage.shape[0]
                cutimage3 = 0
                cutimage4 = cutimage.shape[1]

                imgwidth = cutimage.shape[1]
                imgheight = cutimage.shape[0]
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
                    # cutimg = cutimage[0:reimgheight, 0:reimgwidth]
                    #frame[カーソルの位置Y-画像の半分 : カーソルの位置Y-画像の半分の場所に画像の高さ分を追加、カーソルの位置X-画像の半分 : カーソルの位置X-画像の半分の場所に画像の高さ分を追加]
                    frame[dpty - int(imgheight/2):dpty - int(imgheight/2) + imgheight, dptx - int(imgwidth/2):dptx - int(imgwidth/2) + imgwidth] = cutimage
        return frame
