import io
import math
from struct import pack, unpack

import numpy as np
from bitarray import bitarray

from .bitbuffer import BitBuffer
from .constants import AC, DC, HUFFMAN_CATEGORY_CODEWORD, ZIGZAG_ORDER
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
    uint_to_binstr,
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


def make_header(buf:BitBuffer, image_info, category_codeword=None):
    if category_codeword is not None:
        table = bitarray()
        for dc_ac in [DC, AC]:
            table.extend(uint_to_binstr(len(category_codeword[dc_ac]), 16))
            for category, codeword in category_codeword[dc_ac].items():
                if dc_ac == DC:
                    table.extend(uint_to_binstr(category, 4))
                    table.extend(uint_to_binstr(len(codeword), 4))
                else:
                    table.extend(uint_to_binstr(category[0], 4))
                    table.extend(uint_to_binstr(category[1], 4))
                    table.extend(uint_to_binstr(len(codeword), 8))
                table.extend(codeword)
        flag = 1 << 15
        table_length = len(table)
    else:
        flag = 0
        table_length = 0
    header = pack(
        "IIIHH",
        image_info["height"],
        image_info["width"],
        image_info["quality"],
        flag,
        table_length,
    )
    buf.write_bytes(header)
    if category_codeword is not None:
        buf.write(table)
    return header


def parse_header(header):
    height, width, quality, flag, table_length = unpack("IIIHH", header[:16])
    if flag & (1 << 15):
        table_bits = bitarray()
        table_bits.frombytes(header[16 : 16 + table_length])
        table_bits = io.StringIO(table_bits.to01())
        table = {}
        # for dc_ac in [DC, AC]:
        #     table.extend(uint_to_binstr(len(category_codeword[dc_ac]), 16))
        #     for category, codeword in category_codeword[dc_ac].items():
        #         if dc_ac == DC:
        #             table.extend(uint_to_binstr(category, 4))
        #             table.extend(uint_to_binstr(len(codeword), 4))
        #         else:
        #             table.extend(uint_to_binstr(category[0], 4))
        #             table.extend(uint_to_binstr(category[1], 4))
        #             table.extend(uint_to_binstr(len(codeword), 8))
        #         table.extend(codeword)

    else:
        table = None
    return height, width, quality, table


def compress(image: np.ndarray, quality=50, auto_generate_huffman_table=False):
    info = encode(image, quality)
    dc = info["dc"]
    ac = info["ac"]
    # buf = io.StringIO()
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

    encode_huffman(buf, dc, dc_ac=DC, category_codeword=category_codeword)
    for i in range(ac.shape[0]):
        encode_huffman(
            buf,
            ac_rle[ac_rle_eob_index[i] : ac_rle_eob_index[i + 1]],
            dc_ac=AC,
            category_codeword=category_codeword,
        )

    return buf.to_bytes()


def decompress(data: bytes):
    info = {}
    (
        info["height"],
        info["width"],
        info["quality"],
        category_codeword,
    ) = parse_header(data[:16])
    if category_codeword is None:
        category_codeword = HUFFMAN_CATEGORY_CODEWORD
    block_count = math.ceil(info["height"] / 8) * math.ceil(info["width"] / 8)
    buf = BitBuffer.from_bytes(data[16:])
    dc = decode_huffman(buf, block_count, DC, category_codeword)
    ac = np.zeros((block_count, 63), dtype=np.int32)
    for i in range(block_count):
        ac_block = decode_run_length(
            decode_huffman(buf, dc_ac=AC, category_codeword=category_codeword)
        )
        ac[i, : len(ac_block)] = ac_block
    info["dc"] = np.array(dc)
    info["ac"] = ac
    return decode(info)
