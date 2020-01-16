from torch import nn, optim
import torch.nn.functional as F


class NnModel(nn.Module):
    in_feature = 0
    def __init__(self, dim_descrittore, kernel_size):
        super(NnModel, self).__init__()

        self.conv1 = nn.Conv2d(3, 32, kernel_size=kernel_size)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=kernel_size)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=kernel_size)
        self.conv3_drop = nn.Dropout2d()
        self.in_feature = int((((((((((128-kernel_size)+1)/2)-kernel_size)+1)/2)-kernel_size)+1)/2))
        self.in_feature *= self.in_feature * 128
        self.fc1 = nn.Linear(self.in_feature, dim_descrittore)
        self.fc2 = nn.Linear(dim_descrittore, 2)

    def forward(self, x):
        x = F.relu(F.max_pool2d(self.conv1(x), 2))  # [ (S-k + 2*p)/s + 1 ] / 2
        x = F.relu(F.max_pool2d(self.conv2(x), 2))
        x = F.relu(F.max_pool2d(self.conv3_drop(self.conv3(x)), 2))
        x = x.view(-1, self.in_feature)  # 13*13*20 = 3380
        x = F.relu(self.fc1(x))
        x = F.dropout(x, training=self.training)
        x = self.fc2(x)
        return F.log_softmax(x, dim=1)

