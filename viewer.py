#!/usr/bin/env python3

import sys
from tinyimgcodec import ImageDecoder
import matplotlib.pyplot as plt

with open(sys.argv[1], "rb") as f:
    decoder = ImageDecoder(f.read())
    im = decoder.decode()
    plt.figure()
    plt.imshow(im, cmap="gray", vmin=0, vmax=255)
    plt.show()
