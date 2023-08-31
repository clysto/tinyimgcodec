import sys
from pathlib import Path

import numpy as np
from PIL import Image
from skimage.metrics import peak_signal_noise_ratio

from tinyimgcodec import decompress


def psnr(data1, data2):
    return peak_signal_noise_ratio(data1, data2)


if __name__ == "__main__":

    def open_file(filename):
        s = str.lower(Path(filename).suffix)
        if s == ".img":
            f = open(filename, "rb")
            return decompress(f.read())
        else:
            return np.asarray(Image.open(filename).convert("L"), dtype=np.uint8)

    f1 = sys.argv[1]
    f2 = sys.argv[2]
    im1 = open_file(f1)
    im2 = open_file(f2)
    print(psnr(im1, im2))
