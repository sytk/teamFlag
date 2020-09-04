import os
from src.hand_tracker import HandTracker
import cv2
import numpy as np
import math
import vptree
from statistics import mean
from sklearn.preprocessing import normalize
import time
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import torch
import torch.nn as nn
import numpy as np

#        8   12  16  20
#        |   |   |   |
#        7   11  15  19
#    4   |   |   |   |
#    |   6   10  14  18
#    3   |   |   |   |
#    |   5---9---13--17
#    2    \         /
#     \    \       /
#      1    \     /
#       \    \   /
#        ------0-


class HandGesture():
    def __init__(self):
        self.palm_model_path = "./models/palm_detection_without_custom_op.tflite"
        self.landmark_model_path = "./models/hand_landmark.tflite"
        self.anchors_path = "./models/anchors.csv"

        self.detector = HandTracker(self.palm_model_path, self.landmark_model_path, self.anchors_path,box_shift=0.2, box_enlarge=1.3)
        # self.idx_m = np.mean(self.poseData,axis=1)
        # self.tree = vptree.VPTree(self.poseData, HandGesture.cosineDistanceMatching)

        self.points = None
        self.POINT_COLOR = (0, 255, 0)
        self.CONNECTION_COLOR = (255, 0, 0)
        self.THICKNESS = 2
        self.connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),
            (5, 6), (6, 7), (7, 8),
            (9, 10), (10, 11), (11, 12),
            (13, 14), (14, 15), (15, 16),
            (17, 18), (18, 19), (19, 20),
            (0, 5), (5, 9), (9, 13), (13, 17), (0, 17)
        ]

        self.palm_pos = [0,0]
        self.gesture = 0
        self.palm_depth = 0

        path = './ML/1'
        self.device = 'cpu'

        self.model = MyImageNetwork(10).to(self.device)
        last_state = torch.load(path+'/model_cpu.pt')  # データファイルの読み込み
        self.model.load_state_dict(last_state)

        self.model.eval() # モデルを推論モードに変更
        self.last_palm_depth = 0
        self.last_palm_pos = [0,0]

        self.pre_ges = []
        self.return_ges = 0

        self.finger_pos = [0,0]
        self.last_finger_pos = [0,0]
        self.frame_width = None
        self.frame_height = None
    def get_pose(self, kp,box):
        x0, y0 = 0,0
        max_size = 400
        box_width = np.linalg.norm(box[1] - box[0])
        box_height = np.linalg.norm(box[3] - box[0])
        x1 = ((kp[:,0] - x0) * max_size) / box_width
        y1 = ((kp[:,1] - y0) * max_size) / box_height
        a = np.array([x1,y1])
        v = a.transpose().flatten()
        return normalize([v],norm='l2')[0]

    def updateGesture(self, frame):
        self.frame_width = frame.shape[1]
        self.frame_height = frame.shape[0]

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # scale = 1
        # img_ = cv2.resize(img, (int(img.shape[1] * scale), int(img.shape[0] * scale)))
        img_ = img
        hand = self.detector(img_)

        if hand is not None :#and len(hand) > 0:
            self.points = hand['joints']
            box = hand['bbox']
            bkp = hand['base_joints']

        if hand is not None and self.points[5][0] < self.points[17][0]:
            kp = self.get_pose(bkp,box)

            pose = torch.from_numpy(np.asarray(kp))
            pose = torch.unsqueeze(pose,0)
            # print(pose.size())
            pose = pose.to(self.device, dtype=torch.float)
            with torch.no_grad(): # 推論時には勾配は不要
                outputs = self.model(pose) # 順伝播の計算
                prob, predicted = torch.max(outputs.data, 1) # 確率が最大のラベルを取得
                # print(prob, predicted)

            if prob < 0.6:
                self.gesture = 0
            else:
                self.gesture = np.asarray(predicted)[0]

            # if self.points is not None:
            #    self.points = [point/scale for point in self.points]

            palms = np.asarray([self.points[0], self.points[5],self.points[9],self.points[13], self.points[17]])
            self.palm_pos = palms.mean(axis=0)
            self.palm_pos = [int(p) for p in self.palm_pos]
            self.finger_pos = [int(p) for p in self.points[8]]

            cv2.circle(frame, (self.palm_pos[0], self.palm_pos[1]), self.THICKNESS * 2, self.POINT_COLOR, self.THICKNESS)
            # out.write(frame)
            # print(self.points[5], self.points[17])
            self.palm_depth = self.__computePalmDepth(self.points[5], self.points[17])
        else:
            self.gesture = "None"
            self.pal_pos = [0,0]
            self.finger_pos = [0,0]
            # self.palm_depth = 0
        return frame

    def getGesture(self):
        if len(self.pre_ges) == 3:
            self.pre_ges.pop(0)
        self.pre_ges.append(self.gesture)
        if self.pre_ges.count(self.gesture) == 3:
            self.return_ges = self.gesture
            return self.return_ges
        elif self.gesture == 5:
            return 5
        else:
            return None

    def getPalmPos(self):
        if self.last_palm_pos == [0,0]:
            self.last_palm_pos = self.palm_pos
        k = 0.4
        LPF = []
        for pre, curr in zip(self.last_palm_pos, self.palm_pos):
            LPF.append( (1 - k) * pre + k * curr)
        self.last_palm_pos = LPF
        LPF = [int(p) for p in LPF]

        if LPF[0] < 0:
            LPF[0] = 0
        if LPF[1] < 0:
            LPF[1] = 0
        if LPF[0] > self.frame_width:
            LPF[0] = self.frame_width
        if LPF[1] > self.frame_height:
            LPF[1] = self.frame_height
        return LPF

        # return self.palm_pos

    def getPalmDepth(self, is_grab):
        if self.last_palm_depth == 0:
            self.last_palm_depth = self.palm_depth
        k = 0.2
        LPF = (1 - k) * self.last_palm_depth + k * self.palm_depth;
        self.last_palm_depth = LPF

        if is_grab:
            return LPF
        else:
            return self.palm_depth
        # return self.palm_depth

    def getFingerPos(self):
        if self.last_finger_pos == [0,0]:
            self.last_finger_pos = self.finger_pos
        k = 0.4
        LPF = []
        for pre, curr in zip(self.last_finger_pos, self.finger_pos):
            LPF.append( (1 - k) * pre + k * curr)
        self.last_finger_pos = LPF
        return [int(p) for p in LPF]

    def __computePalmDepth(self, a, b):
        A = np.asarray(a)
        B = np.asarray(b)
        return np.linalg.norm(A-B)

    def drawPalmFrame(self, frame):
        if self.points is not None:
            #points = [point/scale for point in points]
            for point in self.points:
                x, y = point
                cv2.circle(frame, (int(x), int(y)), self.THICKNESS * 2, self.POINT_COLOR, self.THICKNESS)
            for connection in self.connections:
                x0, y0 = self.points[connection[0]]
                x1, y1 = self.points[connection[1]]
                cv2.line(frame, (int(x0), int(y0)), (int(x1), int(y1)), self.CONNECTION_COLOR, self.THICKNESS)
            font = cv2.FONT_HERSHEY_SIMPLEX

            cv2.rectangle(frame, (0, frame.shape[0] - 100), (200, frame.shape[0]), (255,255,255), -1)

            cv2.putText(frame,str(self.gesture),(20,frame.shape[0] - 40), font, 2,(255,0,0),2,cv2.LINE_AA)


        return frame

    @staticmethod
    def similarity(v1,v2):
        return np.dot(v1,v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

    @staticmethod
    def cosineDistanceMatching(poseVector1, poseVector2):
          cosineSimilarity = HandGesture.similarity(poseVector1, poseVector2)
          distance = 2 * (1 - cosineSimilarity)
          return np.sqrt(distance)

class MyImageNetwork(nn.Module):  # 画像識別用ネットワークモデル
    def __init__(self, num_classes):
        super().__init__()
        self.block1 = nn.Sequential(
            nn.Conv2d(3,64,3),
            nn.ReLU(),
            nn.Conv2d(64,64,3),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Dropout(0.25)
        )
        self.block2 = nn.Sequential(
            nn.Conv2d(64,128,3),
            nn.ReLU(),
            nn.Conv2d(128,128,3),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Dropout(0.25)
        )
        self.full_connection = nn.Sequential(
            nn.Linear(42, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            # nn.Dropout(),
            nn.Linear(64, num_classes)
        )
        self.optimizer = torch.optim.Adam(self.parameters(), lr=3e-4)

    def forward(self, x):
        # x = self.block1(x)
        # x = self.block2(x)
        # x = torch.flatten(x, start_dim=1)  # 値を１次元化
        x = self.full_connection(x)
        # return x #クロスエントロピーにはsoftmaxが入ってるらしい
        return torch.softmax(x, dim=1)  # SoftMax 関数の計算結果を出力

    def loss_function(self, estimate, target):
        return nn.functional.cross_entropy(estimate, target)  # 交差エントロピーでクラス判別
