import math

import tensorboardX as tX

if __name__ == '__main__':
    writer = tX.SummaryWriter()
    funcs = { 'sin': math.sin, 'cos': math.cos, 'tan': math.tan }

    for theta in range(-360, 360):
        radians = theta * math.pi / 180
        for name, fn in funcs.items():
            val = fn(radians)
            writer.add_scalar(name, val, theta)

    writer.close()
