#!/usr/bin/env python3

import pathlib
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from tinyimgcodec import decompress


def open_file(filename):
    s = str.lower(Path(filename).suffix)
    if s == ".img":
        f = open(filename, "rb")
        return decompress(f.read())
    else:
        return np.asarray(Image.open(filename).convert("L"), dtype=np.uint8)


nimg = len(sys.argv) - 1

if nimg == 0:
    print("Usage: python3 viewer.py image1 [image2 ...]")
    sys.exit(0)

if nimg == 1:
    ncol = 1
else:
    ncol = 2

nrow = (nimg + 1) // 2

fig, axs = plt.subplots(nrow, ncol)
fig.canvas.manager.set_window_title("Viewer")

if nimg == 1:
    axs = [axs]
else:
    axs = axs.flatten()

for i in range(nimg):
    im = open_file(sys.argv[i + 1])
    axs[i].imshow(im, cmap="gray", vmin=0, vmax=255)
    axs[i].set_title(pathlib.Path(sys.argv[i + 1]).name)
    axs[i].set_xticks([])
    axs[i].set_yticks([])

if nimg % 2 == 1:
    axs[-1].axis("off")

plt.show()
