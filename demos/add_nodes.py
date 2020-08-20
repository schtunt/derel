import numpy as np

x = np.array([[1,1],[0,1],[1,0],[0,0]])

y = np.array([[1],[0],[0],[0]])

w = np.array([[0.3],[2.0]])

b = 1.0

a = 0.01

z = x.dot(w)+b

def add(w,b,iterate):
    while iterate > 0:
        z = x.dot(w)+b
        w -= a*1/len(x)*(x.transpose().dot(z-y))
        b -= a*1/len(x)*sum(z-y)
        print("Cost: ", sum((z-y)**2)/len(x))
        iterate -= 1

    return w,b
