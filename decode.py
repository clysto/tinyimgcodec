#!/usr/bin/env python3

import sys

from PIL import Image

from tinyimgcodec import decompress

f = open(sys.argv[1], "rb")

im = decompress(f.read())
im = Image.fromarray(im, mode="L")
im.save(sys.argv[2])
