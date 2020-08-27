import os
import glob
import numpy as np
import shutil
import torch
from PIL import Image , ImageOps
from torchvision import datasets, transforms
dir = './sample'

files = glob.glob(os.path.join(dir, '*.jpg'))
print(len(files))

categories = []
for file in files:
    cat = file.split('\\')[-1].split('_')[0]
    if not cat in categories:
        categories.append(cat)

cat_dict = {name:val for val, name in enumerate(categories)}

file = open('label.txt', 'w')
for key,item in cat_dict.items():
    # print(key,item)
    file.write(key+' '+str(item)+'\n')
file.close()

X_train = []
X_test = []
Y_train = []
Y_test = []

for cat in categories:
    files = glob.glob(os.path.join(dir, cat+'_*.jpg'))
    y = cat_dict[cat]
    num_all = len(files)
    num_train = round(num_all * 4 / 5)
    id_all   = np.random.choice(num_all, num_all, replace=False)

    for i in id_all[0:num_train]:
        x = np.array(Image.open(files[i]))
        X_train.append(x)
        Y_train.append(y)
    for i in id_all[num_train:]:
    # for file in files[num_train:]:
        x = np.array(Image.open(files[i]))
        X_test.append(x)
        Y_test.append(y)

# X_train = torch.from_numpy(np.asarray(X_train).reshape(-1,3,64,64)).clone()
# Y_train = torch.from_numpy(np.asarray(Y_train)).clone()
# X_test = torch.from_numpy(np.asarray(X_test).reshape(-1,3,64,64)).clone()
# Y_test = torch.from_numpy(np.asarray(Y_test)).clone()

X_train = torch.from_numpy(np.asarray(X_train).reshape(-1,3,64,64)/255) #numpyじゃないと除算できなかった
X_test = torch.from_numpy(np.asarray(X_test).reshape(-1,3,64,64)/255)
Y_train = torch.LongTensor(Y_train)
Y_test = torch.LongTensor(Y_test)

print(X_train.shape,Y_train.shape)
print(X_test.shape,Y_test.shape)

print(torch.max(X_train))

train = (X_train,Y_train)
test = (X_test,Y_test)


torch.save(train,'./clipart_train.pt')
torch.save(test,'./clipart_test.pt')
