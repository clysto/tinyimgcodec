#!/usr/bin/env python3

import sys

import matplotlib.pyplot as plt

sys.path.append("src")

from tinyimgcodec import decompress

with open(sys.argv[1], "rb") as f:
    im = decompress(f.read())
    plt.figure()
    plt.imshow(im, cmap="gray", vmin=0, vmax=255)
    plt.show()
