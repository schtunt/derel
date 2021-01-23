import sys
import itertools
import random
from sys import exit
import numpy as np
import tensorflow as tf

ONE = tf.constant(1., dtype=tf.float16)
DTYPE = ONE.dtype

sigmoid = lambda z: 1. / (1. + np.exp(-z))
identity = lambda z: z

FN_ACTIVATION = {
    'identity': {
        "fn":  identity,
        "fn'": lambda z: tf.fill(z.shape, ONE),
    },
    'sigmoid': {
        "fn":  sigmoid,
        "fn'": lambda z: sigmoid(z) * (1. - sigmoid(z)),
    },
    'relu': { #FIXME
        "fn":  lambda z: max(0, z),
        "fn'": lambda z: 1,
    },
}

FN_LOSS = {
    'quadratic': {
        "fn":  lambda yas: [0.5 * (ya[0] - ya[1])**2 for ya in yas],   # (y - a)**2 / 2
        "fn'": lambda yas: [ya[1] - ya[0] for ya in yas]               # (a - y)
    }
}

class NeuralNetwork:
    def __init__(self, topology, alpha=0.1, activation='sigmoid', loss='quadratic'):
        self.error = tf.Variable(ONE)
        self.alpha = alpha
        self.topology = [i+1 for i in topology]
        self.W = [None]
        for i in range(len(self.topology) - 1):
            topology = self.topology[i:i+2][::-1]
            self.W.append(
                tf.Variable(
                    np.random.rand(*topology),
                    dtype=tf.float16
                )
            )

        self.activation = FN_ACTIVATION[activation]["fn"]
        self.activationPrime = FN_ACTIVATION[activation]["fn'"]

        self.loss = FN_LOSS[loss]["fn"]
        self.lossPrime = FN_LOSS[loss]["fn'"]

        #Z[-1] = tf.pad(Z[-1], [[0,0],[1,0]], constant_values=0.)
        #dZdAl = np.delete(dZdAl.numpy(), 0, 1)

    @property
    def layers(self):
        return len(self.topology)

    def forward(self, X):
        # Add the bias
        A = tf.pad(X, [[0,0],[1,0]], constant_values=1.)

        for W in self.W[1:]:
            Z = tf.tensordot(A, W, (1, 1))
            A = tf.map_fn(self.activation, Z)
            A = np.delete(A.numpy(), 0, 1)
            A = tf.pad(A, [[0,0],[1,0]], constant_values=1.)

        A = np.delete(A, 0, 1)
        return A

    def train(self, X, Y):
        X = tf.pad(X, [[0,0],[1,0]], constant_values=1.)
        A = [X]
        Z = []
        for W in self.W[1:]:
            Z.append(tf.tensordot(A[-1], W, (1, 1)))
            a = tf.map_fn(self.activation, Z[-1])
            a = np.delete(a.numpy(), 0, 1)
            a = tf.pad(a, [[0,0],[1,0]], constant_values=1.)
            A.append(a)

        O = np.delete(A[-1].numpy(), 0, 1)
        yas = [ list(zip(actual, expected)) for actual, expected in zip(Y.numpy(), O)]
        T = len(yas)

        self.error = tf.reduce_mean(list(map(self.loss, yas)))

#       print("A", [a.shape for a in A])
#       print("Z", [z.shape for z in Z])
#       print("W", [w.shape for w in self.W[1:]])
        cache = 1
        for l in map(lambda l:l-1, range(self.layers, 1, -1)):
            dZdW = A[l-1]
#           print("#"*80, l)
            if l == self.layers-1:
#               print(l, "0. W", self.W[l].shape)
                dJdA = tf.Variable(list(map(self.lossPrime, yas)))
                dJdA = tf.pad(dJdA, [[0,0],[1,0]], constant_values=0.)
                dAdZ = tf.Variable(list(map(self.activationPrime, Z[-1])))
#               print(l, "1. dJdA", dJdA.shape)
#               print(l, "1. dAdZ", dAdZ.shape)
                cache = dJdA * dAdZ #XXX
#               print(l, "dJdZ", cache.shape)
            elif l > 0:
#               print(l, "0. W", self.W[l].shape)
                dZdAk = self.W[l+1]
#               print(l, "2. dZdAk", dZdAk.shape)
                cache = tf.tensordot(cache, dZdAk, (1, 0))
#               print(l, "2. cache", cache.shape)
                dAkdZk = tf.Variable(list(map(self.activationPrime, Z[l-1])))
                #dAkdZk = tf.pad(dAkdZk, [[0,0],[1,0]], constant_values=1.)
#               print(l, "2. dAkdZk", dAkdZk.shape)
                cache = cache * dAkdZk #XXX
#           print(l, "3. cache", cache.shape)
#           print(l, "3. dZdW", dZdW.shape)
            dJdW = tf.tensordot(cache, dZdW, (0, 0)) / T
#           print(l, "4. dJdW", dZdW.shape)
            self.W[l] = self.W[l] - self.alpha * dJdW

        #dJdW = tf.tensordot(dJdA * dAdZ, dZdW, (0, 0))
        #self.W[-i] = self.W[-i] - self.alpha * dJdW
        #dJdWl = tf.tensordot(dJdA * dAdZ * dZdAl * dAldZl, dZldWl, (0, 0))
        #self.W[-i] = self.W[-i] - self.alpha * dJdWl

trainer = lambda a,b: [(a+b)/2, 1.-(a+b)/2]

T = 99
X = [
    [0.01, 0.01],
    [0.99, 0.99],
]
X.extend(
    [
        round(random.random(), 2),
        round(random.random(), 2),
    ] for i in range(T-2)
)
X = tf.Variable(X, dtype=tf.float16)

Y = tf.Variable(
    [trainer(a, b) for a,b in X.numpy() ], dtype=tf.float16
)

#nn = NeuralNetwork([2, 10, 2], activation='identity', loss='quadratic', alpha=.11)
nn = NeuralNetwork([2, 10, 2], activation='sigmoid', loss='quadratic', alpha=.99)
lastE = 1
i=0
while True:
    nn.train(X, Y)
    e = nn.error.numpy()

    i += 1
    if e/lastE > 1.01:
        print("Error increased from %0.5f to %0.5f; reducing alpha from %0.3f to %0.3f" % (
            lastE, e,
            nn.alpha, nn.alpha * 0.67
        ))
        print()
        nn.alpha *= 0.67
        lastE = e
    elif e/lastE < 0.99 or i % 100 == 0:
        lastE = e
        testing = tf.Variable(
            [
                [
                    round(random.random(), 2),
                    round(random.random(), 2),
                ] for i in range(7)
            ], dtype=tf.float16
        )
        results = zip(
            testing.numpy(),
            nn.forward(testing),
            [trainer(a, b) for a,b in testing.numpy()],
        )
        for ingress, egress, expected in sorted(results, key=lambda x: x[2]):
            print("{ f(%0.2f, %0.2f) -> [%0.3f / %0.3f] vs [%0.3f / %0.3f] }" % tuple(
                itertools.chain.from_iterable([
                    ingress,
                    egress,
                    expected,
                ])
            ), " --> %12.3f%%" % (
                100.0 * (
                    abs((egress[0]-expected[0])/expected[0])
                ),
            ))
        print("I:%5d, Error: %0.9f, Alpha: %0.9f" % (i, e, nn.alpha))
        print()
