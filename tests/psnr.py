import numpy as np
import math


def psnr(data1, data2, max_pixel=255):
    mse = np.mean((data1 - data2) ** 2)
    if mse:
        return 20 * math.log10(max_pixel / mse**0.5)
    return math.inf
