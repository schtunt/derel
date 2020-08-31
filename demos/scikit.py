import collections
import numpy as np
from matplotlib import pylab
from sklearn.datasets import load_digits
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

class Activation(collections.namedtuple('Activation', ['name', 'fn', 'df'])):
    __slots__ = ()

sigmoid_fn = lambda x: 1/(1+np.exp(-x))
sigmoid_df = lambda x: sigmoid_fn(x) * (1 - sigmoid_fn(x))
sigmoid = Activation('sigmoid', sigmoid_fn, sigmoid_df)


def convert_y_to_vect(y):
    y_vect = np.zeros((len(y), 10))
    for i in range(len(y_vect)):
        y_vect[i, y[i]] = 1
    return y_vect


digits = load_digits()

X_scale = StandardScaler()
X = X_scale.fit_transform(digits.data)

y = digits.target
X_train, X_test, Y_train, Y_test = train_test_split(X, y, test_size=0.8)


class NeuralNet:
    def __init__(self, inputs, hidden, outputs, activation):
        self._activation = activation
        self._structure = [inputs, hidden, outputs]

        self.W = {}
        self.b = {}

        for l in range(1, len(self._structure)):
            l0 = self._structure[l]
            l1 = self._structure[l-1]

            self.W[l] = np.random.random_sample((l0, l1))
            self.b[l] = np.random.random_sample((l0,))

    def generate_mean_accumulation(self):
        tW = {}
        tb = {}

        for l in range(1, len(self._structure)):
            tW[l] = np.zeros((l0, l1))
            tb[l] = np.zeros((l0, ))

        return tW, tb

    def feed_forward(self, x, W, b):
        h = { 1: x }
        z = {}

        #for b, w in zip(self.biases, self.weights):
        #    x = sigmoid(np.dot(w, x) + b)
        #return x

        for l in range(1, len(W)+1):
            inputs = h[l]
            z[l+1] = W[l].dot(inputs) + b[l]
            h[l+1] = self.activation.fn(z[l+1])

        return h, z

    def calculate_out_layer_delta(self, y, h_out, z_out):
        return -(y - h_out) * self._activation.df(z_out)

    def calculate_hidden_layer_delta(self, delta_plus_1, w_l, z_l):
        return np.dot(np.transpose(w_l), delta_plus_1) * self._activation.df(z_l)

    def train(X, y, iter_num=3000, alpha=0.25):
        cnt = 0
        m = len(y)


nn = NeuralNet(digits.data.shape[1], int(digits.data.shape[1]/2), 10, sigmoid)

