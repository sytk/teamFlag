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
        self.gesture = "first"
        self.palm_depth = 0

        path = './ML/1'
        self.device = 'cpu'

        self.model = MyImageNetwork(10).to(self.device)
        last_state = torch.load(path+'/model_cpu.pt')  # データファイルの読み込み
        self.model.load_state_dict(last_state)

        self.model.eval() # モデルを推論モードに変更

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
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        hand = self.detector(img)

        if hand is not None :#and len(hand) > 0:
            points = hand['joints']
            box = hand['bbox']
            bkp = hand['base_joints']

            kp = self.get_pose(bkp,box)

            pose = torch.from_numpy(np.asarray(kp))
            pose = torch.unsqueeze(pose,0)
            # print(pose.size())
            pose = pose.to(self.device, dtype=torch.float)
            with torch.no_grad(): # 推論時には勾配は不要
                outputs = self.model(pose) # 順伝播の計算
                prob, predicted = torch.max(outputs.data, 1) # 確率が最大のラベルを取得
                # print(prob, predicted)

            # res = self.tree.get_n_nearest_neighbors(kp,1)[0]
            # a = np.mean(res[1])
            # # print(res[0],np.where(idx_m == a)[0][0])
            # idx = np.where(self.idx_m == a)[0][0]
            # # print(self.indexes[idx])
            self.gesture = np.asarray(predicted)[0]

            if prob > 0.6:
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(frame,str(predicted),(20,100), font, 2,(255,0,0),2,cv2.LINE_AA)
                cv2.putText(frame, str(prob),(20,30), font, 1,(255,0,0),2,cv2.LINE_AA)
            else:
                self.gesture = 0

            #
            if points is not None:
                for point in points:
                    x, y = point
                    cv2.circle(frame, (int(x), int(y)), self.THICKNESS * 2, self.POINT_COLOR, self.THICKNESS)
                for connection in self.connections:
                    x0, y0 = points[connection[0]]
                    x1, y1 = points[connection[1]]
                    cv2.line(frame, (int(x0), int(y0)), (int(x1), int(y1)), self.CONNECTION_COLOR, self.THICKNESS)

            palms = np.asarray([points[0], points[5],points[9],points[13], points[17]])
            self.palm_pos = palms.mean(axis=0)
            cv2.circle(frame, (int(self.palm_pos[0]), int(self.palm_pos[1])), self.THICKNESS * 2, self.POINT_COLOR, self.THICKNESS)
            # out.write(frame)
            self.palm_depth = self.__computePalmDepth(points[5], points[17])
        else:
            self.gesture = "None"
        return frame

    def getGesture(self):
        return self.gesture;

    def getPalmPos(self):
        return self.palm_pos;

    def getPalmDepth(self):
        return self.palm_depth;

    def __computePalmDepth(self, a, b):
        A = np.asarray(a)
        B = np.asarray(b)
        return np.linalg.norm(A-B)

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
