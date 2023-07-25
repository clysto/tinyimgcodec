import io
import math
from struct import pack, unpack

import numpy as np
from bitarray import bitarray

from .constants import AC, DC, ZIGZAG_ORDER
from .huffman import (
    decode_huffman,
    decode_run_length,
    encode_huffman,
    encode_run_length,
)
from .utils import (
    block_combine,
    block_dct,
    block_idct,
    block_quantize,
    block_slice,
    pad_image,
)


def encode(image: np.ndarray, quality=50):
    height, width = image.shape
    image = pad_image(image)
    image = block_slice(image.astype(np.int32) - 128, (8, 8))
    coeffs = block_dct(image)
    coeffs = block_quantize(coeffs, quality)
    coeffs = coeffs.reshape(coeffs.shape[0], coeffs.shape[1], 64)
    coeffs = coeffs[:, :, ZIGZAG_ORDER]
    dc = coeffs[:, :, 0].reshape(-1)
    dc[1:] = np.diff(dc)
    ac = coeffs[:, :, 1:].reshape(-1, 63)
    return {
        "height": height,
        "width": width,
        "quality": quality,
        "dc": dc,
        "ac": ac,
    }


def decode(data: np.ndarray):
    height = data["height"]
    width = data["width"]
    quality = data["quality"]
    blocks_per_row = math.ceil(width / 8)
    blocks_per_col = math.ceil(height / 8)
    dc = np.cumsum(data["dc"])
    ac = data["ac"]
    coeffs = np.zeros((dc.shape[0], 64), dtype=np.int32)
    coeffs[:, 0] = dc
    coeffs[:, 1:] = ac
    coeffs[:, ZIGZAG_ORDER] = coeffs.copy()
    coeffs = coeffs.reshape(blocks_per_col, blocks_per_row, 8, 8)
    coeffs = block_quantize(coeffs, quality, inverse=True)
    coeffs = block_idct(coeffs)
    coeffs = block_combine(coeffs)
    coeffs = np.clip(coeffs + 128, 0, 255)
    coeffs = coeffs[:height, :width]
    return coeffs.astype(np.uint8)


def make_header(image_info):
    return pack("III", image_info["height"], image_info["width"], image_info["quality"])


def compress(image: np.ndarray, quality=50):
    info = encode(image, quality)
    header = make_header(info)
    dc = info["dc"]
    ac = info["ac"]
    buf = io.StringIO()
    encode_huffman(buf, dc, dc_ac=DC)
    for i in range(ac.shape[0]):
        encode_huffman(buf, encode_run_length(ac[i]), dc_ac=AC)

    return header + bitarray(buf.getvalue()).tobytes()


def decompress(data: bytes):
    info = {}
    info["height"], info["width"], info["quality"] = unpack("III", data[:12])
    block_count = math.ceil(info["height"] / 8) * math.ceil(info["width"] / 8)
    buf = bitarray()
    buf.frombytes(data[12:])
    buf = io.StringIO(buf.to01())
    dc = decode_huffman(buf, block_count, DC)
    ac = np.zeros((block_count, 63), dtype=np.int32)
    for i in range(block_count):
        ac_block = decode_run_length(decode_huffman(buf, dc_ac=AC))
        ac[i, : len(ac_block)] = ac_block
    info["dc"] = np.array(dc)
    info["ac"] = ac
    return decode(info)
