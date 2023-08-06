#!/usr/bin/env python3

import sys

import numpy as np
from PIL import Image


im = Image.open(sys.argv[1]).convert("L")

np.asarray(im).tofile(sys.argv[2])
