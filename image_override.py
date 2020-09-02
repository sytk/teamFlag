import cv2


class ImageOverwriter:
    image_list = []
    __prev_data = {"ges": 0, "palm": (0, 0)}
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
        dict = {"path": path, "org_img": org_img, "img": img, "default_scale": scale, "scale": scale, "visible": False,
                "pos": (None, None), "hide_img_shape": img.shape}
        self.image_list.append(dict)
        self.__hidden_image_list.insert(0, len(self.image_list) - 1)

    def addImages(self, path_list):
        org_images = []
        scale = 0
        for path in path_list:
            org_img = cv2.imread(path, cv2.IMREAD_UNCHANGED)

            scale = 250 / org_img.shape[1]
            org_images.append(org_img)
        img = cv2.resize(org_images[0], (int(org_images[0].shape[1] * scale), int(org_images[0].shape[0] * scale)))
        dict = {"path": path_list, "org_img": org_images, "img": img, "index": 0, "default_scale": scale,
                "scale": scale, "visible": False, "pos": (None, None), "hide_img_shape": img.shape}
        self.image_list.append(dict)
        self.__hidden_image_list.insert(0, len(self.image_list) - 1)

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
            width = self.image_list[num]["hide_img_shape"][1]
            height = self.image_list[num]["hide_img_shape"][0]
            start_height = sum([self.image_list[i]["hide_img_shape"][0] for i in range(num)])
            self.image_list[num]["pos"] = (width // 2, height // 2 + start_height)

    def applyScale(self, index, restore_default):
        image = self.image_list[index]
        scale = 0
        if restore_default:
            scale = image["default_scale"]
        else:
            scale = image["scale"]
        if type(image["org_img"]) is list:
            org_img_index = image["index"]
            self.image_list[index]["img"] = cv2.resize(image["org_img"][org_img_index], (
            int(image["org_img"][org_img_index].shape[1] * scale),
            int(image["org_img"][org_img_index].shape[0] * scale)))
        else:
            self.image_list[index]["img"] = cv2.resize(image["org_img"], (
            int(image["org_img"].shape[1] * scale), int(image["org_img"].shape[0] * scale)))

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
            self.applyScale(num, restore_default=False)

    def grabImage(self, index, palm, depth):
        if self.image_list[index]["visible"]:
            pos = self.image_list[index]["pos"]
            x = pos[0] + palm[0] - self.__prev_data["palm"][0]
            y = pos[1] + palm[1] - self.__prev_data["palm"][1]
            self.setPosition(index, (x, y))

            scale = self.image_list[index]["scale"]
            if not self.isGrab():
                self.__base_depth = depth / scale
            self.image_list[index]["scale"] = depth / self.__base_depth

            self.__grab_image_index = index
            if index in self.__hidden_image_list:
                self.__hidden_image_list.remove(index)
            self.applyScale(index, restore_default=False)

    def releaseImage(self):
        self.__grab_image_index = None
        self.__base_depth = 1.0

    def showImage(self, pos):
        index = self.__hidden_image_list.pop()
        self.applyScale(index, restore_default=False)
        self.setPosition(index, (pos[0], pos[1]))
        self.image_list[index]["visible"] = True

    def hideImage(self, index):
        self.applyScale(index, restore_default=True)
        self.setPosition(index, None)
        self.image_list[index]["visible"] = False
        self.__hidden_image_list.append(index)

    def overwrite(self, frame, ges, palm, depth, bg):
        overlapped_images = self.checkOverlap(palm)
        prev_ges = self.__prev_data["ges"]
        if bg is not None:
            ftimg = frame.copy()
            bgimg = bg.copy()
            bggray = cv2.cvtColor(bgimg, cv2.COLOR_BGR2GRAY)
            bgblur = cv2.GaussianBlur(bggray,(5,5),5)
            bgblur = cv2.blur(bgblur,(30,30))
        if ges != 5:
            self.releaseImage()
        if ges == 2:
            if prev_ges != 2 and len(overlapped_images) > 0:
                self.changePage(overlapped_images[0], "prev")
        if ges == 3:
            if prev_ges != 3 and len(overlapped_images) > 0:
                self.changePage(overlapped_images[0], "next")
        if ges == 4:
            pass
        if ges == 5:
            if len(overlapped_images) > 0:
                if prev_ges != 5:
                    self.grabImage(overlapped_images[0], palm, depth)
                elif self.isGrab() and self.__grab_image_index in overlapped_images:
                    self.grabImage(self.__grab_image_index, palm, depth)
            else:
                self.releaseImage()
        if ges == 6:
            if prev_ges != 6 and len(overlapped_images) > 0:
                self.hideImage(overlapped_images[0])
        if ges == 7:
            if prev_ges != 7 and len(self.__hidden_image_list) > 0:
                self.showImage(palm)

        self.__prev_data["ges"] = ges
        self.__prev_data["palm"] = palm
        try:
            for i, image in enumerate(self.image_list):
                if image["pos"][0] is None or image["pos"][1] is None:
                    image["visible"] = False
                if i in self.__hidden_image_list:
                    if i in overlapped_images:
                        image["visible"] = True
                    else:
                        image["visible"] = False

                if image["visible"]:
                    cutimage = image["img"]
                    dptx = image["pos"][0]
                    dpty = image["pos"][1]

                    if bg is not None:
                        width = bgimg.shape[1]
                        height = bgimg.shape[0]

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
                    half_img_width = imgwidth // 2
                    half_img_height = imgheight // 2

                    # 左にはみ出てたら
                    if dptx - half_img_width < 0:
                        outsideflag = True
                        leftoutsideimg = half_img_width - dptx
                        cutimage3 = leftoutsideimg

                    # 右にはみ出てたら
                    if width < dptx - half_img_width + imgwidth:
                        outsideflag = True
                        rightoutsideimg = dptx - half_img_width + imgwidth - width
                        cutimage4 = imgwidth - int(rightoutsideimg)

                    # 左にはみ出てたら
                    if dpty - half_img_height < 0:
                        outsideflag = True
                        upoutsideimg = half_img_height - dpty
                        cutimage1 = upoutsideimg

                    # 下にはみ出てたら
                    if height < dpty - half_img_height + imgheight:
                        outsideflag = True
                        downoutsideimg = dpty - half_img_height + imgheight - height
                        cutimage2 = imgheight - downoutsideimg

                    # はみ出ているフラグが立ってたら
                    if outsideflag:
                        # 上記の結果から画像を切り取り
                        # cutheight, cutwidth = cutimg.shape[:2] #カットした写真のサイズ
                        cutimg = cutimage[cutimage1:cutimage2, cutimage3:cutimage4]
                        if bg is not None:
                            # カットした写真を合成
                            # frame[カーソルの位置Y-画像の半分 : カーソルの位置Y-画像の半分の場所に画像の高さ分を追加、カーソルの位置X-画像の半分 : カーソルの位置X-画像の半分の場所に画像の高さ分を追加]
                            bgimg[
                            dpty - half_img_height + upoutsideimg:dpty - half_img_height + imgheight - downoutsideimg,
                            dptx - half_img_width + leftoutsideimg:dptx - half_img_width + imgwidth - rightoutsideimg] = cutimg
                        else:
                            frame[
                            dpty - half_img_height + upoutsideimg:dpty - half_img_height + imgheight - downoutsideimg,
                            dptx - half_img_width + leftoutsideimg:dptx - half_img_width + imgwidth - rightoutsideimg] = cutimg

                    # 　外にはみ出る物がない時
                    else:
                        if bg is not None:
                            # cutimg = cutimage[0:reimgheight, 0:reimgwidth]
                            # frame[カーソルの位置Y-画像の半分 : カーソルの位置Y-画像の半分の場所に画像の高さ分を追加、カーソルの位置X-画像の半分 : カーソルの位置X-画像の半分の場所に画像の高さ分を追加]
                            bgimg[dpty - half_img_height:dpty - half_img_width + imgheight,
                            dptx - half_img_width:dptx - half_img_width + imgwidth] = cutimage
                        else:
                            frame[dpty - half_img_height:dpty - half_img_width + imgheight,
                            dptx - half_img_width:dptx - half_img_width + imgwidth] = cutimage
                        
        except Exception:
            pass
        if bg is not None:
            ftgray = cv2.cvtColor(ftimg, cv2.COLOR_BGR2GRAY)
            ftblur = cv2.GaussianBlur(ftgray,(5,5),5)
            ftblur = cv2.blur(ftblur,(30,30))    
            #sabun
            subimg = cv2.subtract(bgblur, ftblur)
            #画像の二値化
            mask = cv2.threshold(subimg, 0, 255, cv2.THRESH_BINARY)[1]
            #imgのマスク合成画像作成
            imgmask = cv2.bitwise_and(ftimg, ftimg,mask=mask)
            # 白 (255, 255, 255) のピクセルを取得する。
            white_pixels = (imgmask == (0, 0, 0)).all(axis=-1)
            # 白のピクセルを黒 (0, 0, 0) にする。
            #imgmask[white_pixels] = (130, 170, 180)
            imgmask[white_pixels] = (255, 255, 255)
            frame = cv2.addWeighted(imgmask, 0.3, bgimg, 0.7, 0)

        if self.isGrab():
            index = self.__grab_image_index
            half_img_width = self.image_list[index]["img"].shape[1] // 2
            half_img_height = self.image_list[index]["img"].shape[0] // 2
            dx = self.image_list[index]["pos"][0] + palm[0] - self.__prev_data["palm"][0]
            dy = self.image_list[index]["pos"][1] + palm[1] - self.__prev_data["palm"][1]
            begin = (dx - half_img_width - 2, dy - half_img_height - 2)
            end = (dx + half_img_width + 2, dy + half_img_height + 2)
            cv2.rectangle(frame, begin, end, (255, 0, 0), thickness=2, lineType=cv2.LINE_8, shift=0)

        return frame

