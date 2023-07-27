import math

import numpy as np
from scipy.fftpack import dct, idct

from .constants import LUMINANCE_QUANTIZATION_TABLE


def bits_required(x):
    return np.ceil(np.log2(np.abs(x) + 1)).astype(np.int32)


def block_slice(image: np.ndarray, kernel_size: tuple):
    img_height, img_width = image.shape
    tile_height, tile_width = kernel_size
    tiled_array = image.reshape(
        img_height // tile_height, tile_height, img_width // tile_width, tile_width
    )
    tiled_array = tiled_array.swapaxes(1, 2)
    return tiled_array


def block_combine(tiled_array: np.ndarray):
    h, w, tile_height, tile_width = tiled_array.shape
    height = h * tile_height
    width = w * tile_width
    tiled_array = tiled_array.swapaxes(1, 2)
    image = tiled_array.reshape(height, width)
    return image


def block_dct(image: np.ndarray):
    return dct(
        dct(image, norm="ortho", axis=-2),
        axis=-1,
        norm="ortho",
    )


def block_idct(image: np.ndarray):
    return idct(
        idct(image, norm="ortho", axis=-2),
        axis=-1,
        norm="ortho",
    )


def block_quantize(coeffs: np.ndarray, quality=50, inverse=False):
    quantization_table = LUMINANCE_QUANTIZATION_TABLE
    factor = 5000 / quality if quality < 50 else 200 - 2 * quality
    if inverse:
        return coeffs * (quantization_table * factor / 100)
    return np.round(coeffs / (quantization_table * factor / 100)).astype(np.int32)


def pad_image(im: np.ndarray):
    height, width = im.shape
    height = math.ceil(height / 8) * 8
    width = math.ceil(width / 8) * 8
    im = np.pad(im, ((0, height - im.shape[0]), (0, width - im.shape[1])), "reflect")
    return im
