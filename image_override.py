import cv2


class ImageOverwriter:
    image_list = []
    __gesture_list = {"curr": 0, "prev": 0}
    __grab_image_num = None
    __base_depth = 1
    __hidden_image_index = []
    __stay_time = 0

    def __init__(self):
        pass

    def addImage(self, path):
        img = cv2.imread(path, cv2.IMREAD_UNCHANGED)

        scale = 250 / img.shape[1]
        img = cv2.resize(img, (int(img.shape[1] * scale), int(img.shape[0] * scale)))

        dict = {"path": path, "org_img": img, "img": img, "scale": 1.0, "visible": True, "pos": (None, None),
                "out_screen": False}
        self.image_list.append(dict)

    def addImages(self, path_list):
        images = []
        for path in path_list:
            img = cv2.imread(path, cv2.IMREAD_UNCHANGED)

            scale = 250 / img.shape[1]
            img = cv2.resize(img, (int(img.shape[1] * scale), int(img.shape[0] * scale)))
            images.append(img)
        dict = {"path": path_list, "org_img": images, "img": images[0], "index": 0, "scale": 1.0, "visible": True, "pos": (None, None), "out_screen": False}
        self.image_list.append(dict)

    def checkOverlap(self, pos):
        overlapped_img = []
        for i, dict in enumerate(self.image_list):
            x, y = dict["pos"][0], dict["pos"][1]

            if x is None or y is None:
                continue

            half_w = dict["img"].shape[1] // 2
            half_h = dict["img"].shape[0] // 2

            left_top = (x - half_w, y - half_h)
            right_bottom = (x + half_w, y + half_h)

            continue_flag = False

            for p, min, max in zip(pos, left_top, right_bottom):
                if not min < p < max:
                    continue_flag = True

            if continue_flag:  # pos isn't in img
                continue

            overlapped_img.append(i)  # pos is in img
        return overlapped_img

    def setPosition(self, num, pos):
        if pos is not None:
            self.image_list[num]["pos"] = (pos[0], pos[1])
        else:
            if type(self.image_list[num]["org_img"]) is list:
                index = self.image_list[num]["index"]
                width = self.image_list[num]["org_img"][index].shape[1]
            else:
                width = self.image_list[num]["org_img"].shape[1]

            self.image_list[num]["pos"] = (-width, 0)

    def updateGesture(self, gesture):
        self.__gesture_list["prev"] = self.__gesture_list["curr"]
        self.__gesture_list["curr"] = gesture

    def getPrevGesture(self):
        return self.__gesture_list["prev"]

    def isGrab(self):
        return self.__grab_image_num is not None

    def changePage(self, num, direction):
        if type(self.image_list[num]["org_img"]) is list:
            if direction == "prev":
                index = self.image_list[num]["index"] - 1
                if index < 0:
                    index = len(self.image_list[num]["org_img"]) - 1
                self.image_list[num]["index"] = index
                self.image_list[num]["img"] = self.image_list[num]["org_img"][index]
            elif direction == "next":
                index = self.image_list[num]["index"] + 1
                if index >= len(self.image_list[num]["org_img"]):
                    index = 0
                self.image_list[num]["index"] = index
                self.image_list[num]["img"] = self.image_list[num]["org_img"][index]

    def grabImage(self, num, depth):
        scale = self.image_list[num]["scale"]
        if not self.isGrab():
            self.__base_depth = depth / scale

        image = self.image_list[num]["org_img"]
        if type(image) is list:
            index = self.image_list[num]["index"]
            self.image_list[num]["img"] = cv2.resize(image[index], (int(image[index].shape[1] * scale), int(image[index].shape[0] * scale)))
        else:
            self.image_list[num]["img"] = cv2.resize(image, (int(image.shape[1] * scale), int(image.shape[0] * scale)))

        self.image_list[num]["scale"] = depth / self.__base_depth
        self.__grab_image_num = num

    def releaseImage(self):
        self.__grab_image_num = None
        self.__base_depth = 1.0

    def showImage(self, pos):
        if len(self.__hidden_image_index) > 0:
            index = self.__hidden_image_index.pop()
            self.image_list[index]["visible"] = True
            self.image_list[index]["pos"] = (pos[0], pos[1])

    def hideImage(self, num):
        self.image_list[num]["visible"] = False
        self.__hidden_image_index.append(num)

    def pullImage(self, pos):
        for i, image in enumerate(self.image_list):
            if image["out_screen"]:
                self.setPosition(i, pos)
                image["out_screen"] = False
                break

    def overwrite(self, frame, ges, palm, depth):
        self.updateGesture(ges)
        overlapped_images = self.checkOverlap(palm)

        if ges != 5:
            self.releaseImage()
        if ges == 2:
            prev_ges = self.__gesture_list["prev"]
            if prev_ges != 2 and len(overlapped_images) > 0:
                self.changePage(overlapped_images[0], "prev")
        if ges == 3:
            prev_ges = self.__gesture_list["prev"]
            if prev_ges != 3 and len(overlapped_images) > 0:
                self.changePage(overlapped_images[0], "next")
        if ges == 4:
            self.showImage(palm)
        if ges == 5:
            prev_ges = self.__gesture_list["prev"]
            if prev_ges != 5:
                if len(overlapped_images) > 0:
                    self.grabImage(overlapped_images[0], depth)
                    self.setPosition(overlapped_images[0], palm)
            elif self.isGrab():
                self.grabImage(self.__grab_image_num, depth)
                self.setPosition(self.__grab_image_num, palm)
            else:
                self.releaseImage()
        if ges == 6:
            if len(overlapped_images) > 0:
                self.hideImage(overlapped_images[0])
        if ges == 7:
            prev_ges = self.__gesture_list["prev"]
            if prev_ges != 7:
                self.pullImage(palm)
        elif 0 < palm[0] < 100:
            self.__stay_time += 1
            if self.__stay_time >= 5:
                self.pullImage(palm)
                self.__stay_time = 0
        else:
            self.__stay_time = 0

        for image in self.image_list:
            if image["pos"][0] is None or image["pos"][1] is None:
                image["visible"] = False
            elif image["pos"][0] < 0 or image["pos"][1] < 0:
                image["out_screen"] = True
                continue

            if image["visible"]:
                cutimage = image["img"]
                dptx = image["pos"][0]
                dpty = image["pos"][1]

                width = frame.shape[1]
                height = frame.shape[0]

                outsideflag = True  # はみ出ているかフラグ
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

                # 左にはみ出てたら
                if dptx - imgwidth // 2 < 0:
                    outsideflag = True
                    leftoutsideimg = imgwidth // 2 - dptx
                    cutimage3 = leftoutsideimg

                # 右にはみ出てたら
                if width < dptx - imgwidth // 2 + imgwidth:
                    outsideflag = True
                    rightoutsideimg = dptx - imgwidth // 2 + imgwidth - width
                    cutimage4 = imgwidth - int(rightoutsideimg)

                # 左にはみ出てたら
                if dpty - imgheight // 2 < 0:
                    outsideflag = True
                    upoutsideimg = imgheight // 2 - dpty
                    cutimage1 = upoutsideimg

                # 下にはみ出てたら
                if height < dpty - imgheight // 2 + imgheight:
                    outsideflag = True
                    downoutsideimg = dpty - imgheight // 2 + imgheight - height
                    cutimage2 = imgheight - downoutsideimg

                # はみ出ているフラグが立ってたら
                if outsideflag:
                    try:
                        # 上記の結果から画像を切り取り
                        # cutheight, cutwidth = cutimg.shape[:2] #カットした写真のサイズ
                        cutimg = cutimage[cutimage1:cutimage2, cutimage3:cutimage4]
                        # カットした写真を合成
                        # frame[カーソルの位置Y-画像の半分 : カーソルの位置Y-画像の半分の場所に画像の高さ分を追加、カーソルの位置X-画像の半分 : カーソルの位置X-画像の半分の場所に画像の高さ分を追加]
                        frame[
                        dpty - imgheight // 2 + upoutsideimg:dpty - imgheight // 2 + imgheight - downoutsideimg,
                        dptx - imgwidth // 2 + leftoutsideimg:dptx - imgwidth // 2 + imgwidth - rightoutsideimg] = cutimg
                    except ValueError:
                        image["out_screen"] = True
                        continue

                # 　外にはみ出る物がない時
                else:
                    # cutimg = cutimage[0:reimgheight, 0:reimgwidth]
                    # frame[カーソルの位置Y-画像の半分 : カーソルの位置Y-画像の半分の場所に画像の高さ分を追加、カーソルの位置X-画像の半分 : カーソルの位置X-画像の半分の場所に画像の高さ分を追加]
                    frame[dpty - imgheight // 2:dpty - imgheight // 2 + imgheight,
                    dptx - imgwidth // 2:dptx - imgwidth // 2 + imgwidth] = cutimage
        return frame
