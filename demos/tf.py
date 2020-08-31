import sys
import numpy as np
import tensorflow as tf

print(
    "Num GPUs Available: %d",
    len(tf.config.experimental.list_physical_devices('GPU'))
)


AND = lambda a, b: int(all((a, b)))
OR  = lambda a, b: int(any((a, b)))

sigmoid = lambda z: 1. / (1. + np.exp(-z))
sigmoidDash = lambda z: sigmoid(z) * (1. - sigmoid(z))

loss = lambda ya: 0.5 * (ya[0] - ya[1])**2   # (y - a)**2 / 2
lossDash = lambda ya: ya[1] - ya[0]          # (a - y)

#       w11
# x1---o----a1
#       \  / w21
#        \/
#        /\
#       /  \ w12
# x2---o----a2
#       w22

inputs = [[0,0],[0,1],[1,0],[1,1]]
b = tf.Variable([-4.])

#               [[w11, w21], [w21, w22]]
w = tf.Variable([[4, 4], [5, 5]], dtype=tf.float32)

x = tf.Variable(np.array(inputs), dtype=tf.float32)
y = tf.Variable([[AND(u,v), OR(u,v)] for u,v in (inputs)], dtype=tf.float32)

def feed(x1, x2, w, b):
    return [
        sigmoid(x1 * w[0][0] + x2 * w[0][1] + b[0]),
        sigmoid(x1 * w[1][0] + x2 * w[1][1] + b[0]),
    ]

def dot(a, b):
    return tf.tensordot(a, b, 1)

i = 0
alpha = 0.01
while True:
    z = dot(x, tf.transpose(w)) + b
    a = sigmoid(z)

    zippedYA = list(zip(y.numpy(), a))
    L = tf.Variable(list(map(loss, zippedYA)))
    C = tf.reduce_mean(L, (0,0))

    if i % 500 == 0:
        print(80 * '#')
        print("C:", C)
        print("W:", w)
        print("b:", b)
        print(80 * '-')
        for (x1, x2) in inputs:
            print("x: [%d, %d]" % (x1, x2))
            print("y: [%d, %d]" % (AND(x1, x2), OR(x1, x2)))
            print("a: %s" % feed(x1, x2, w, b))
        print()

    if max(C) < 0.000005:
        break

    i += 1

    dC_da = tf.Variable(list(map(lossDash, zippedYA)))
    da_dz = tf.map_fn(sigmoidDash, z)
    dz_dw = x[:]
    dC_dw = tf.reduce_mean(dC_da * da_dz * dz_dw, 0) / x.shape[0]

    breakpoint()

    dC_dw = tf.transpose(dC_dw * tf.ones([y.shape[1], 1]))
    w = w - alpha * dC_dw


    dz_db = [[ 1.0 ]] * len(inputs)
    dC_db = tf.reduce_mean(dC_da * da_dz * dz_db) / x.shape[0]
    b = b - alpha * dC_db
