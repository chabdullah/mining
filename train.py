import torch
import torchvision
import torchvision.transforms as transforms
from shutil import copy2
import os
import numpy as np
import torch
import torchvision
import matplotlib.pyplot as plt
# from sklearn.metrics import confusion_matrix
from time import time

from torch.optim.lr_scheduler import StepLR
from torchvision import datasets, transforms
from torch import nn, optim
import torch.nn.functional as F
from tensorboardX import SummaryWriter
from torchvision.utils import save_image
from itertools import product
from NnModel import NnModel
from utility import slimJson, extractImagesInfoIntoJson, extractCroppedFigures, testFigure, testResults


def load_data(batch_size):
  traindata_path = './resources/docFigure/data/training'
  valdata_path = './resources/docFigure/data/validation'

  train_dataset = torchvision.datasets.ImageFolder(
          root=traindata_path,
          transform=torchvision.transforms.Compose([
            torchvision.transforms.Resize(img_size),
            torchvision.transforms.ToTensor(),
          ])
      )
  val_dataset = torchvision.datasets.ImageFolder(
    root=valdata_path,
    transform=torchvision.transforms.Compose([
      torchvision.transforms.Resize(img_size),
      torchvision.transforms.ToTensor(),
    ])
  )
  #print("Train: Detected Classes are: ", train_dataset.class_to_idx)
  train_loader = torch.utils.data.DataLoader(
      train_dataset,
      batch_size=batch_size,
      num_workers=0,
      shuffle=True
  )
  val_loader = torch.utils.data.DataLoader(
      val_dataset,
      batch_size=batch_size,
      num_workers=0,
      shuffle=True
  )
  return train_loader, val_loader


def train(epoch):
  network.train()
  total_loss = 0
  correct = 0
  for batch_id, (data, target) in enumerate(train_loader):
    #data = data.narrow(1,0,1)
    data = data.to(device)
    target = target.to(device)
    optimizer.zero_grad()
    output = network(data)
    loss = criterion(output, target)
    total_loss += loss.item()
    loss.backward()
    optimizer.step()
    pred = output.data.max(1, keepdim=True)[1]
    correct += pred.eq(target.data.view_as(pred)).sum()
    if batch_id % log_interval == 0:
      print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(epoch, batch_id * len(data), len(train_loader.dataset),
        100. * batch_id / len(train_loader), loss.item()))
      torch.save(network.state_dict(), './resources//docFigure/model128_2_classi.pth')
      #torch.save(optimizer.state_dict(), './savedState/optimizer'+dataset_type+'.pth')
  tb.add_scalar('Train Loss', 100.0 * total_loss/len(train_loader.dataset), epoch)
  tb.add_scalar('Train Accuracy', 100 * correct / len(train_loader.dataset), epoch)


  #for name, param in network.named_parameters():
    #tb.add_histogram(name, param, epoch)
    #tb.add_histogram(f'{name}.grad', param.grad, epoch)


def test(epoch):
  network.eval()
  train_loss = 0
  correct = 0
  with torch.no_grad():
    for batch_id, (data, target) in enumerate(val_loader):
      #data = data.narrow(1,0,1)
      data = data.to(device)
      target = target.to(device)
      output = network(data)
      train_loss += criterion(output, target).item()
      pred = output.data.max(1, keepdim=True)[1]
      correct += pred.eq(target.data.view_as(pred)).sum()
  train_loss /= len(val_loader.dataset)
  print('\nTest set: Avg. loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
    train_loss, correct, len(val_loader.dataset),
    100. * correct / len(val_loader.dataset)))
  tb.add_scalar('Test Loss', 100.0 * train_loss, epoch)
  tb.add_scalar('Test Accuracy', 100. * correct/len(val_loader.dataset), epoch)


def setDatasetFolder(dataset):
    with open('./resources/docFigure/annotation/'+dataset+'.txt') as f:
        line = f.readline()
        while line:
            imageName, imageType = line.strip().split(", ")
            imageType = imageType.replace(" ","_")
            print("{} -> {}".format(imageName,imageType))
            srcPath = './resources/docFigure/grec_19/images/'+imageName
            dstPath = './resources/docFigure/data/validation/'+imageType
            if not os.path.exists(dstPath):
                os.makedirs(dstPath)
            copy2(srcPath,dstPath)
            line = f.readline()


#setDatasetFolder("test")
dim_descrittore = 1024
kernel_size = 5
device = "cpu"
lr = 0.01
momentum = 0.5
log_interval = 10
batch_size = 16
n_epochs = 5
img_size = (128,128)
pretrained = False

train_loader, val_loader = load_data(batch_size)
network = NnModel(dim_descrittore, kernel_size)
if pretrained:
    network.load_state_dict(torch.load('./resources/docFigure/model128_2_classi.pth'))
network = network.to(device)
optimizer = optim.SGD(network.parameters(), lr=lr, momentum=momentum)
#optimizer.load_state_dict(torch.load('./savedState/optimizer' + dataset_type + '.pth'))
#scheduler = StepLR(optimizer, step_size=30, gamma=0.1)
criterion = nn.CrossEntropyLoss()

images, labels = next(iter(train_loader))
grid = torchvision.utils.make_grid(images)

tb = SummaryWriter(comment=f' batch_size={batch_size} dim_descrittore={dim_descrittore} kernel_size= {kernel_size}')
tb.add_image('Faces', grid)


print('\033[92m' + 'batch_size=%s \ndim_descrittore=%s kernel_size=%s \033[0m'% (batch_size, dim_descrittore, kernel_size))
for epoch in range(n_epochs):
    #scheduler.step()
    train(epoch)
    test(epoch)
tb.close()

### Testare i risultati dopo l'addestramento ###
#Pulire train.json per memorizzare solo le informazioni sulle figure
slimJson()

extractImagesInfoIntoJson()
extractCroppedFigures()
testFigure()
testResults()

