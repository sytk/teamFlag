import cv2


class ImageOverwriter:
    image_list = []
    __gesture_list = {"curr": 0, "prev": 0}
    __grab_image_index = None
    __base_depth = 1
    __hidden_image_list = []
    __stay_time = 0

    def __init__(self):
        pass

    def addImage(self, path):
        org_img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        scale = 250 / org_img.shape[1]
        img = cv2.resize(org_img, (int(org_img.shape[1] * scale), int(org_img.shape[0] * scale)))
        dict = {"path": path, "org_img": org_img, "img": img, "scale": scale, "visible": False, "pos": (None, None)}
        self.image_list.append(dict)
        self.__hidden_image_list.append(len(self.image_list) - 1)

    def addImages(self, path_list):
        org_images = []
        scale = 0
        for path in path_list:
            org_img = cv2.imread(path, cv2.IMREAD_UNCHANGED)

            scale = 250 / org_img.shape[1]
            org_images.append(org_img)
        img = cv2.resize(org_images[0], (int(org_images[0].shape[1] * scale), int(org_images[0].shape[0] * scale)))
        dict = {"path": path_list, "org_img": org_images, "img": img, "index": 0, "scale": scale, "visible": False, "pos": (None, None)}
        self.image_list.append(dict)
        self.__hidden_image_list.append(len(self.image_list) - 1)

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
            width = self.image_list[num]["img"].shape[1]
            height = self.image_list[num]["img"].shape[0]
            start_height = sum([self.image_list[i]["img"].shape[0] for i in range(num)])
            self.image_list[num]["pos"] = (width // 2, height // 2 + start_height)

    def applyScale(self, index):
        image = self.image_list[index]
        scale = image["scale"]
        if type(image["org_img"]) is list:
            org_img_index = image["index"]
            self.image_list[index]["img"] = cv2.resize(image["org_img"][org_img_index], (int(image["org_img"][org_img_index].shape[1] * scale), int(image["org_img"][org_img_index].shape[0] * scale)))
        else:
            self.image_list[index]["img"] = cv2.resize(image["org_img"], (int(image["org_img"].shape[1] * scale), int(image["org_img"].shape[0] * scale)))

    def updateGesture(self, gesture):
        self.__gesture_list["prev"] = self.__gesture_list["curr"]
        self.__gesture_list["curr"] = gesture

    def getPrevGesture(self):
        return self.__gesture_list["prev"]

    def isGrab(self):
        return self.__grab_image_index is not None

    def changePage(self, num, direction):
        org_img = self.image_list[num]["org_img"]
        if type(org_img) is list:
            index = self.image_list[num]["index"]
            if direction == "prev":
                index -= 1
                if index < 0:
                    index = len(org_img) - 1
            elif direction == "next":
                index += 1
                if index >= len(org_img):
                    index = 0
            self.image_list[num]["index"] = index
            self.applyScale(num)

    def grabImage(self, index, depth):
        scale = self.image_list[index]["scale"]
        if not self.isGrab():
            self.__base_depth = depth / scale
        self.image_list[index]["scale"] = depth / self.__base_depth
        self.__grab_image_index = index
        if index in self.__hidden_image_list:
            self.__hidden_image_list.remove(index)
        self.applyScale(index)

    def releaseImage(self):
        self.__grab_image_index = None
        self.__base_depth = 1.0

    def showImage(self, pos):
        index = self.__hidden_image_list.pop()
        self.applyScale(index)
        self.image_list[index]["visible"] = True
        self.image_list[index]["pos"] = (pos[0], pos[1])

    def hideImage(self, index):
        if type(self.image_list[index]["org_img"]) is list:
            self.image_list[index]["scale"] = 250 / self.image_list[index]["org_img"][0].shape[1]
        else:
            self.image_list[index]["scale"] = 250 / self.image_list[index]["org_img"].shape[1]
        self.applyScale(index)
        self.setPosition(index, None)
        self.image_list[index]["visible"] = False
        self.__hidden_image_list.append(index)

    def overwrite(self, frame, ges, palm, depth):
        self.updateGesture(ges)
        overlapped_images = self.checkOverlap(palm)
        prev_ges = self.__gesture_list["prev"]

        if ges != 5:
            self.releaseImage()
        if ges == 2:
            if prev_ges != 2 and len(overlapped_images) > 0:
                self.changePage(overlapped_images[0], "prev")
        if ges == 3:
            if prev_ges != 3 and len(overlapped_images) > 0:
                self.changePage(overlapped_images[0], "next")
        if ges == 4:
            if prev_ges != 4 and len(self.__hidden_image_list):
                self.showImage(palm)
        if ges == 5:
            if len(overlapped_images) > 0:
                index = 0
                if prev_ges != 5:
                    index = overlapped_images[0]
                elif self.isGrab():
                    index = self.__grab_image_index
                if self.image_list[index]["visible"]:
                    self.grabImage(index, depth)
                    self.setPosition(index, palm)
                    half_width = self.image_list[index]["img"].shape[1] // 2
                    half_height = self.image_list[index]["img"].shape[0] // 2
                    begin = (palm[0] - half_width - 2, palm[1] - half_height - 2)
                    end = (palm[0] + half_width + 2, palm[1] + half_height + 2)
                    cv2.rectangle(frame, begin, end, (255, 0, 0), thickness=2, lineType=cv2.LINE_8, shift=0)
            else:
                self.releaseImage()
        if ges == 6:
            if prev_ges != 6 and len(overlapped_images) > 0:
                self.hideImage(overlapped_images[0])
        if ges == 7:
            pass

        for i, image in enumerate(self.image_list):
            if image["pos"][0] is None or image["pos"][1] is None:
                image["visible"] = False
            if i in self.__hidden_image_list:
                if 0 < palm[0] <= 200:
                    image["visible"] = True
                else:
                    image["visible"] = False

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
                    # 上記の結果から画像を切り取り
                    # cutheight, cutwidth = cutimg.shape[:2] #カットした写真のサイズ
                    cutimg = cutimage[cutimage1:cutimage2, cutimage3:cutimage4]
                    # カットした写真を合成
                    # frame[カーソルの位置Y-画像の半分 : カーソルの位置Y-画像の半分の場所に画像の高さ分を追加、カーソルの位置X-画像の半分 : カーソルの位置X-画像の半分の場所に画像の高さ分を追加]
                    frame[
                    dpty - imgheight // 2 + upoutsideimg:dpty - imgheight // 2 + imgheight - downoutsideimg,
                    dptx - imgwidth // 2 + leftoutsideimg:dptx - imgwidth // 2 + imgwidth - rightoutsideimg] = cutimg

                # 　外にはみ出る物がない時
                else:
                    # cutimg = cutimage[0:reimgheight, 0:reimgwidth]
                    # frame[カーソルの位置Y-画像の半分 : カーソルの位置Y-画像の半分の場所に画像の高さ分を追加、カーソルの位置X-画像の半分 : カーソルの位置X-画像の半分の場所に画像の高さ分を追加]
                    frame[dpty - imgheight // 2:dpty - imgheight // 2 + imgheight,
                    dptx - imgwidth // 2:dptx - imgwidth // 2 + imgwidth] = cutimage
        return frame
