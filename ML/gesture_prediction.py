# import os
# from torch.utils.data import Dataset
# from torch.utils.data import DataLoader
import torch
import torch.nn as nn
import numpy as np
# import matplotlib.pyplot as plt

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

if __name__ == '__main__':
    # device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    path = './1'
    device = 'cpu'
    model = MyImageNetwork(10).to(device)
    last_state = torch.load(path+'/model_cpu.pt')  # データファイルの読み込み
    model.load_state_dict(last_state)
    model.eval() # モデルを推論モードに変更

    test_data = torch.load('./test.pt')
    pose = test_data[0][0]
    pose = torch.unsqueeze(pose,0)

    pose = pose.to(device, dtype=torch.float)
    with torch.no_grad(): # 推論時には勾配は不要
        outputs = model(pose) # 順伝播の計算
        prob, predicted = torch.max(outputs.data, 1) # 確率が最大のラベルを取得
        print(prob, predicted)
