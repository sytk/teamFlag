import queue

import cv2


class ImageOverwriter():
    image_list = []
    __gesture_list = {"curr": 1, "prev": 1}
    __is_grabbed = False
    __base_depth = 1
    __hidden_image_index = queue.Queue()

    def __init__(self):
        pass
        # self.image_list = []

    def addImage(self, path):
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)

        scale = 250 / img.shape[1]
        img = cv2.resize(img, (int(img.shape[1] * scale), int(img.shape[0] * scale)))

        dict = {"path": path, "org_img": img, "img": img, "scale": 1.0, "state": 1, "pos": (None, None)}
        self.image_list.append(dict)

    def checkOverlap(self, pos):
        list = []
        for i, dict in enumerate(self.image_list):
            x, y = dict["pos"][0], dict["pos"][1]

            if x == None or y == None:
                continue

            half_w = int(dict["img"].shape[1] / 2)
            half_h = int(dict["img"].shape[0] / 2)

            left_top = (x - half_w, y - half_h)
            right_bottom = (x + half_w, y + half_h)

            continue_flag = False

            for p, min, max in zip(pos, left_top, right_bottom):
                if not min < p < max:
                    continue_flag = True

            if continue_flag:  # pos isn't in img
                continue

            list.append(i)  # pos is in img
            # return i
        return list

    def setPosition(self, num, x, y):
        self.image_list[num]["pos"] = (x, y)

    def updateGesture(self, gesture):
        self.__gesture_list["prev"] = self.__gesture_list["curr"]
        self.__gesture_list["curr"] = gesture

    def getPrevGesture(self):
        return self.__gesture_list["prev"]

    def isGrab(self):
        return self.__is_grabbed

    def grabImage(self, num, depth):
        scale = self.image_list[num]["scale"]
        if not self.__is_grabbed:
            self.__base_depth = depth / scale

        image = self.image_list[num]["org_img"]
        self.image_list[num]["img"] = cv2.resize(image, (int(image.shape[1] * scale), int(image.shape[0] * scale)))
        self.image_list[num]["scale"] = depth / self.__base_depth

        self.__is_grabbed = True

    def releaseImage(self):
        self.__is_grabbed = False
        self.__base_depth = 1.0

    def showImage(self):
        if self.__hidden_image_index.qsize() > 0:
            index = self.__hidden_image_index.get()
            self.image_list[index]["state"] = 1

    def hideImage(self, num):
        self.image_list[num]["state"] = 0
        self.__hidden_image_index.put(num)

    def overwrite(self, frame):
        for image in self.image_list:
            if image["pos"][0] == None or image["pos"][1] == None:
                image["state"] = 0

            if image["state"] == 1:
                cutimage = image["img"]
                dptx = image["pos"][0]
                dpty = image["pos"][1]

                width = frame.shape[1]
                height = frame.shape[0]

                outsideflag = 0  # はみ出ているかフラグ
                leftoutsideimg = 0  # 左側の画面外に出ている部分のサイズ
                rightoutsideimg = 0
                upoutsideimg = 0
                downoutsideimg = 0
                # デフォルト値を設定
                # cutimage = cutimage[0:reimgheight, 0:reimgwidth]

                cutimage1 = 0
                cutimage2 = cutimage.shape[0]
                cutimage3 = 0
                cutimage4 = cutimage.shape[1]

                imgwidth = cutimage.shape[1]
                imgheight = cutimage.shape[0]
                # print(dptx,dpty)

                # 左にはみ出てたら
                if (dptx - int(imgwidth / 2) < 0):
                    outsideflag = 1
                    leftoutsideimg = int(imgwidth / 2) - dptx
                    # print(leftoutsideimg)
                    cutimage3 = leftoutsideimg

                # 右にはみ出てたら
                if (width < dptx - int(imgwidth / 2) + imgwidth):
                    outsideflag = 1
                    rightoutsideimg = dptx - int(imgwidth / 2) + imgwidth - width
                    # print(rightoutsideimg)
                    cutimage4 = imgwidth - int(rightoutsideimg)

                # 左にはみ出てたら
                if (dpty - int(imgheight / 2) < 0):
                    outsideflag = 1
                    upoutsideimg = int(imgheight / 2) - dpty
                    # print(upoutsideimg)
                    cutimage1 = upoutsideimg

                # 下にはみ出てたら
                if (height < dpty - int(imgheight / 2) + imgheight):
                    outsideflag = 1
                    downoutsideimg = dpty - int(imgheight / 2) + imgheight - height
                    cutimage2 = imgheight - downoutsideimg

                # はみ出ているフラグが立ってたら
                if (outsideflag == 1):
                    # 上記の結果から画像を切り取り
                    cutimg = cutimage[cutimage1:cutimage2, cutimage3:cutimage4]
                    # cutheight, cutwidth = cutimg.shape[:2] #カットした写真のサイズ
                    # カットした写真を合成
                    # frame[カーソルの位置Y-画像の半分 : カーソルの位置Y-画像の半分の場所に画像の高さ分を追加、カーソルの位置X-画像の半分 : カーソルの位置X-画像の半分の場所に画像の高さ分を追加]

                    frame[
                    dpty - int(imgheight / 2) + upoutsideimg:dpty - int(imgheight / 2) + imgheight - downoutsideimg,
                    dptx - int(imgwidth / 2) + leftoutsideimg:dptx - int(
                        imgwidth / 2) + imgwidth - rightoutsideimg] = cutimg

                # 　外にはみ出る物がない時
                else:
                    # cutimg = cutimage[0:reimgheight, 0:reimgwidth]
                    # frame[カーソルの位置Y-画像の半分 : カーソルの位置Y-画像の半分の場所に画像の高さ分を追加、カーソルの位置X-画像の半分 : カーソルの位置X-画像の半分の場所に画像の高さ分を追加]
                    frame[dpty - int(imgheight / 2):dpty - int(imgheight / 2) + imgheight,
                    dptx - int(imgwidth / 2):dptx - int(imgwidth / 2) + imgwidth] = cutimage
        return frame
