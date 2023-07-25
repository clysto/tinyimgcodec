#!/usr/bin/env python3

import sys

import numpy as np
from PIL import Image

from tinyimgcodec import compress

im = Image.open(sys.argv[1]).convert("L")

out = compress(np.asarray(im))

byte_size = len(out)
print(f"{byte_size} bytes")
print(f"Compression Ratio: {im.width * im.height / byte_size}:1")

with open(sys.argv[2], "wb") as f:
    f.write(out)
