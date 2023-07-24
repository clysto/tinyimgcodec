#!/usr/bin/env python3

from tinyimgcodec import ImageEncoder
import sys
from PIL import Image
import numpy as np


im = Image.open(sys.argv[1])

encoder = ImageEncoder()
out = encoder.encode(np.asarray(im))

byte_size = len(out)
print(f"{byte_size} bytes")
print(f"Compression Ratio: {im.width * im.height / byte_size}:1")

with open(sys.argv[2], "wb") as f:
    f.write(out)
