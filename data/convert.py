import numpy as np
from PIL import Image
import sys

im = Image.open(sys.argv[1]).convert("L")
im = im.resize((256, 256))
im = np.asarray(im)
im.tofile(sys.argv[2])

