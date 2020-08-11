from matplotlib import pylab
import numpy as np

# define a series of inputs
x = np.arange(-8, 8, 0.1)

# rectified linear function
relu = np.maximum(0.0, x)
pylab.plot(x, relu)
pylab.xlabel('x')
pylab.ylabel('f(x)')

sigmoid = 1 / (1 + np.exp(-x))
pylab.plot(x, sigmoid)
pylab.xlabel('x')
pylab.ylabel('f(x)')

pylab.show()
