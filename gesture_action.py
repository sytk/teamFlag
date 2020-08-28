# -*- coding: utf-8 -*-

class GestureActionExecutor():
    __curr_gesture = "none"
    __prev_gesture = "none"
    __state = "none"
    __base_depth = 0
    __image_size_ratio = 1.0
    MIN_IMAGE_SIZE_RATIO = 0.2
    MAX_IMAGE_SIZE_RATIO = 2.0

    def __init__(self):
        pass

    def updateGesture(self, gesture):
        """現在のジェスチャーと1つ前のジェスチャーを更新する

        Args:
            gesture(str): 現在のジェスチャー

        Returns:
            None
        """
        self.__prev_gesture = self.__curr_gesture
        self.__curr_gesture = gesture

    def updateState(self, state, depth):
        """画像の状態を更新する

        Args:
            depth(str):現在のPalmDepth
            state(str):現在の状態

        Returns:
            None

        """
        if self.__state == "none" and state == "grip":
            self.__base_depth = depth
            self.__image_size_ratio = 1.0
        else:
            self.__image_size_ratio = depth / self.__base_depth
            self.__image_size_ratio = max(self.MIN_IMAGE_SIZE_RATIO, min(self.MAX_IMAGE_SIZE_RATIO, self.__image_size_ratio))

        self.__state = state

    def getGestures(self):
        """現在のジェスチャーと1つ前のジェスチャーを取得する

        Returns:
            dict["curr", "prev"]

        """
        return {"curr": self.__curr_gesture, "prev": self.__prev_gesture}

    def getState(self):
        """現在の状態を取得する

        Returns:
            state
        """
        return self.__state

    def getImageSizeRatio(self):
        """画像に適用するサイズ比を返す

        Returns:
            image_size_ratio(float)

        """
        return self.__image_size_ratio