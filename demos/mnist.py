from matplotlib import pylab
from sklearn.datasets import load_digits

digits = load_digits()
print(digits.data.shape)

pylab.gray()
pylab.matshow(digits.images[0])
pylab.show()
