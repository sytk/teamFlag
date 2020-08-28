class GestureActionExecutor():
    __curr_gesture = "None"
    __prev_gesture = "None"
    __state = "None"

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

    def updateState(self, state):
        """画像との接触状態を更新する

        Args:
            state(str):現在の状態

        Returns:
            None

        """
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
