import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import random

import torch.optim as optim

sin = math.sin
pi = math.pi

"""
Nima I a basic and function doesn't seem complex enough to actually yield
concrete evidence

y(result) = sin(x1*pi/2) + x2
more difficult :)
"""

def function1_samples(number):
    sample = torch.randn(1,1,number,2)
    result = torch.zeros(1,1,number,1)
    for n in range(number):
        result[0][0][n][0] = sin(sample[0][0][n][0]*pi/2)+sample[0][0][n][1]
    return sample.float(),result.float()

def function2_samples(number):
    sample = torch.randn(1,1,number,2)
    result = torch.zeros(1,1,number,1)
    for n in range(number):
        result[0][0][n][0] = sample[0][0][n][0] + sample[0][0][n][1]
    return sample.float(),result.float()
"""
REMOVED AND ADDED TO CLASS
__________________________
linear = nn.Linear(2,2,1)

def forward(x):
    x = self.linear(x)
    return x
"""


"""
So I got here and I realised that the backwards call is probably a function that
was inherited from the Module.nn. This is probably the reason the NN is created
as a class. As such, I've recreated the NN as a class called Net
"""

class Net(nn.Module):

    def __init__(self):
        super(Net, self).__init__()
        self.linear = nn.Linear(2,1) #change tupple to create different archit..

    def forward(self,x):
        return self.linear(x)

net = Net()

#created sample function1 (HARD) function2 (...EASY)
sample, result = function2_samples(10)



# create your optimizer
optimizer = optim.SGD(net.parameters(), lr=0.01)

def less_do_it(iterations):

    for i in range(iterations):
        out = net(sample)
        if i == 1:
            print("First network Output:")
            print(out)
        #define loss function as Mean Square Error
        criterion = nn.MSELoss()
        loss = criterion(out, result)
        print("loss: ",loss)
        net.zero_grad()
        loss.backward()
        optimizer.step()

before_changes = net.forward(sample)

less_do_it(1000)
print("Prior to Optimising:")
print(before_changes)
print("After:")
print(net.forward(sample))
print("Solution:")
print(result)
