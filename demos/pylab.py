from matplotlib import pylab
import numpy as np

x = np.arange(-5, 5, 0.1)

# rectified linear function
relu = np.maximum(0.0, x)
pylab.plot(x, relu)

sigmoid_fn = lambda x: 1. / (1. + np.exp(-x))

sigmoid = 1 / (1 + np.exp(-x))
pylab.plot(x, sigmoid)

sigmoidPrime = sigmoid_fn(x) * (1. - sigmoid_fn(x))
pylab.plot(x, sigmoidPrime)

pylab.grid(1)
pylab.xlabel('x')
pylab.ylabel('f(x)')
pylab.legend(['relu', 'sigmoid', 'sigmoidPrime'])

pylab.show()
