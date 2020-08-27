import os
import glob
import numpy as np
import shutil
import torch
from PIL import Image , ImageOps
from torchvision import datasets, transforms

from ges import HandGesture

dir = '../Dataset'

files = glob.glob(os.path.join(dir,'*', '*.JPG'))
print(len(files))

files = glob.glob(os.path.join(dir,'*'))
categories = [file.split('\\')[-1] for file in files]
print(categories)

cat_dict = {name:val for val, name in enumerate(categories)}
print(cat_dict)

file = open('label.txt', 'w')
for key,item in cat_dict.items():
    # print(key,item)
    file.write(key+' '+str(item)+'\n')
file.close()

X_train = []
X_test = []
Y_train = []
Y_test = []

detector = HandGesture()


for cat in categories:
    files = glob.glob(os.path.join(dir, cat, '*.JPG'))
    y = cat_dict[cat]
    num_all = len(files)
    num_train = round(num_all * 4 / 5)
    id_all = np.random.choice(num_all, num_all, replace=False)

    count = 0
    for i in id_all[0:num_train]:
        img = np.asarray(Image.open(files[i]).convert('RGB'))
        for i in range(2):
            x = detector.updateGesture(img)
            if len(x) == 42:
                X_train.append(x)
                Y_train.append(y)
            img = img[:,::-1]

    for i in id_all[num_train:]:
        img = np.asarray(Image.open(files[i]).convert('RGB'))
        for i in range(2):
            x = detector.updateGesture(img)
            if len(x) == 42:
                X_test.append(x)
                Y_test.append(y)
            img = img[:,::-1]

    print(Y_train)
    print(len(X_train),len(Y_train))
    print(len(X_test),len(Y_test))
#
#
# print(np.asarray(X_train).shape,np.asarray(Y_train).shape)
# print(np.asarray(X_test).shape,np.asarray(Y_test).shape)

# # X_train = torch.from_numpy(np.asarray(X_train).reshape(-1,3,64,64)).clone()
# # Y_train = torch.from_numpy(np.asarray(Y_train)).clone()
# # X_test = torch.from_numpy(np.asarray(X_test).reshape(-1,3,64,64)).clone()
# # Y_test = torch.from_numpy(np.asarray(Y_test)).clone()

X_train = torch.from_numpy(np.asarray(X_train)) #numpyじゃないと除算できなかった
X_test = torch.from_numpy(np.asarray(X_test))
Y_train = torch.LongTensor(Y_train)
Y_test = torch.LongTensor(Y_test)

print(X_train.shape,Y_train.shape)
print(X_test.shape,Y_test.shape)
#
# print(torch.max(X_train))
#
train = (X_train,Y_train)
test = (X_test,Y_test)

torch.save(train,'./train.pt')
torch.save(test,'./test.pt')
