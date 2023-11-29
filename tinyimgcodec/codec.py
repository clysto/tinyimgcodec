import math
from struct import pack, unpack
from subprocess import Popen, PIPE

import numpy as np
from io import BytesIO
from bidict import bidict

from PIL import Image

from .bitbuffer import BitBuffer, BitBuffer2
from .constants import AC, ANNSCALES, DC, HUFFMAN_CATEGORY_CODEWORD, ZIGZAG_ORDER
from .huffman import (
    calc_huffman_table,
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
    # dc[1:] = np.diff(dc)
    ac = coeffs[:, :, 1:].reshape(-1, 63)
    return {
        "height": height,
        "width": width,
        "quality": quality,
        "dc": dc,
        "ac": ac,
    }


def decode(data):
    height = data["height"]
    width = data["width"]
    quality = data["quality"]
    scaled_dct = data["scaled_dct"]
    blocks_per_row = math.ceil(width / 8)
    blocks_per_col = math.ceil(height / 8)
    # dc = np.cumsum(data["dc"])
    dc = data["dc"]
    ac = data["ac"]
    coeffs = np.zeros((dc.shape[0], 64), dtype=np.int32)
    coeffs[:, 0] = dc
    coeffs[:, 1:] = ac
    coeffs[:, ZIGZAG_ORDER] = coeffs.copy()
    if scaled_dct:
        coeffs = coeffs.reshape(blocks_per_col, blocks_per_row, 8, 8) / ANNSCALES
        coeffs *= 2 ** (quality)
        quality = 50
    else:
        coeffs = coeffs.reshape(blocks_per_col, blocks_per_row, 8, 8)
    coeffs = block_quantize(coeffs, quality, inverse=True)
    coeffs = block_idct(coeffs)
    coeffs = block_combine(coeffs)
    coeffs = np.clip(coeffs + 128, 0, 255)
    coeffs = coeffs[:height, :width]
    return coeffs.astype(np.uint8)


def write_huffman_table(buf: BitBuffer, table: dict[str, bidict]):
    buf.write_uint(len(table[DC]), 16)
    for category, codeword in table[DC].items():
        buf.write_uint(category, 4)
        buf.write_uint(len(codeword), 4)
        buf.write(codeword)
    buf.write_uint(len(table[AC]), 16)
    for category, codeword in table[AC].items():
        buf.write_uint(category[0], 4)
        buf.write_uint(category[1], 4)
        buf.write_uint(len(codeword), 8)
        buf.write(codeword)


def read_huffman_table(buf: BitBuffer):
    table = {DC: bidict(), AC: bidict()}
    for _ in range(buf.read_uint(16)):
        category = buf.read_uint(4)
        size = buf.read_uint(4)
        codeword = buf.read(size)
        table[DC][category] = codeword
    for _ in range(buf.read_uint(16)):
        category = (buf.read_uint(4), buf.read_uint(4))
        size = buf.read_uint(8)
        codeword = buf.read(size)
        table[AC][category] = codeword
    return table


def make_header(buf: BitBuffer, image_info, category_codeword=None):
    header = pack(
        "III",
        image_info["height"],
        image_info["width"],
        image_info["quality"],
    )
    buf.write_bytes(header)
    if category_codeword is not None:
        buf.write_uint(1 << 31, 32)
        write_huffman_table(buf, category_codeword)
    else:
        buf.write_uint(0, 32)


def parse_header(buf: BitBuffer, info: dict):
    header = buf.read_bytes(16)
    height, width, quality, flag = unpack("IIII", header)
    info["height"] = height
    info["width"] = width
    info["quality"] = quality
    info["scaled_dct"] = False
    if flag & (1 << 31):
        table = read_huffman_table(buf)
        info["category_codeword"] = table
    elif flag & (1 << 30):
        info["scaled_dct"] = True
    else:
        table = None


def compress(image: np.ndarray, quality=50, auto_generate_huffman_table=False):
    info = encode(image, quality)
    dc = info["dc"]
    ac = info["ac"]
    buf = BitBuffer()

    ac_rle = []
    ac_rle_eob_index = [0]
    # run-length encode ac coeffs
    for i in range(ac.shape[0]):
        ac_rle.extend(encode_run_length(ac[i]))
        ac_rle_eob_index.append(len(ac_rle))

    if auto_generate_huffman_table:
        category_codeword = calc_huffman_table(dc, ac_rle)
        make_header(buf, info, category_codeword)
    else:
        category_codeword = HUFFMAN_CATEGORY_CODEWORD
        make_header(buf, info)

    prev_dc = 0
    rst_index = 0
    for i in range(ac.shape[0]):
        block_buf = BitBuffer()
        # encode single block (MCU)
        encode_huffman(
            block_buf,
            dc[i : i + 1] - prev_dc,
            dc_ac=DC,
            category_codeword=category_codeword,
        )
        prev_dc = dc[i : i + 1]
        encode_huffman(
            block_buf,
            ac_rle[ac_rle_eob_index[i] : ac_rle_eob_index[i + 1]],
            dc_ac=AC,
            category_codeword=category_codeword,
        )
        buf.write_bytes(block_buf.to_bytes().replace(b"\xff", b"\xff\x00"))
        if i % 4 == 3:
            # write RST marker
            prev_dc = 0
            buf.write_bytes(bytearray([0xFF, rst_index + 1]))
            rst_index = (rst_index + 1) % 254

    return buf.to_bytes()


def decompress_fast(data: bytes, exe_path: str):
    process = Popen([exe_path], stdout=PIPE, stdin=PIPE)
    out, _ = process.communicate(data)
    buf = BytesIO(out)
    im = Image.open(buf)
    return np.asarray(im)


def decompress(data: bytes):
    info = {}
    buf = BitBuffer2.from_bytes(data)
    parse_header(buf, info)
    if "category_codeword" in info:
        category_codeword = info["category_codeword"]
    else:
        category_codeword = HUFFMAN_CATEGORY_CODEWORD
    block_count = math.ceil(info["height"] / 8) * math.ceil(info["width"] / 8)
    dc = np.zeros(block_count, dtype=np.int32)
    ac = np.zeros((block_count, 63), dtype=np.int32)

    prev_dc = 0
    prev_rst_index = -1
    i = 0
    r = 0
    while i < block_count:
        try:
            dc[i] = prev_dc = prev_dc + decode_huffman(buf, 1, DC, category_codeword)[0]
            ac_block = decode_run_length(
                decode_huffman(buf, dc_ac=AC, category_codeword=category_codeword)
            )
            ac[i, : len(ac_block)] = ac_block
            buf.align()
        except Exception:
            pass
        if i % 4 == 3:
            prev_dc = 0
            try:
                rst_index = buf.sync_rst()
                if rst_index > 253 or rst_index < 0:
                    i += 1
                    continue
                if rst_index < prev_rst_index:
                    rst_index += 254
                    r += 1
                if (rst_index - prev_rst_index) > 10:
                    continue
                i += (rst_index - prev_rst_index - 1) * 4
                prev_rst_index = rst_index % 254
            except Exception:
                pass
        i += 1

    info["dc"] = np.array(dc)
    info["ac"] = ac
    return decode(info)
