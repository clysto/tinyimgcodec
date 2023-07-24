import numpy as np
import cv2
import io
from huffman import HuffmanTree

QUANT = np.array(
    [
        [16, 11, 10, 16, 24, 40, 51, 61],
        [12, 12, 14, 19, 26, 58, 60, 55],
        [14, 13, 16, 24, 40, 57, 69, 56],
        [14, 17, 22, 29, 51, 87, 80, 62],
        [18, 22, 37, 56, 68, 109, 103, 77],
        [24, 35, 55, 64, 81, 104, 113, 92],
        [49, 64, 78, 87, 103, 121, 120, 101],
        [72, 92, 95, 98, 112, 100, 103, 99],
    ]
)

# fmt:off
ZZ8X8 = np.array(
    [
        0, 1, 8, 16, 9, 2, 3, 10,
        17, 24, 32, 25, 18, 11, 4, 5,
        12, 19, 26, 33, 40, 48, 41, 34,
        27, 20, 13, 6, 7, 14, 21, 28,
        35, 42, 49, 56, 57, 50, 43, 36,
        29, 22, 15, 23, 30, 37, 44, 51,
        58, 59, 52, 45, 38, 31, 39, 46,
        53, 60, 61, 54, 47, 55, 62, 63,
    ]
)
# fmt:on

IMG_SIZE_BITS = 16
TABLE_SIZE_BITS = 16
DC_CODE_LENGTH_BITS = 4
CATEGORY_BITS = 4
AC_CODE_LENGTH_BITS = 8
RUN_LENGTH_BITS = 4
SIZE_BITS = 4


def bits_required(n):
    n = abs(n)
    result = 0
    while n > 0:
        n >>= 1
        result += 1
    return result


def binstr_flip(binstr):
    return "".join(map(lambda c: "0" if c == "1" else "1", binstr))


def uint_to_binstr(number, size):
    return bin(number)[2:][-size:].zfill(size)


def int_to_binstr(n):
    if n == 0:
        return ""

    binstr = bin(abs(n))[2:]

    # change every 0 to 1 and vice verse when n is negative
    return binstr if n > 0 else binstr_flip(binstr)


def flatten(lst):
    return [item for sublist in lst for item in sublist]


def block_to_zigzag(block):
    return block.reshape(-1)[ZZ8X8]


def zigzag_to_block(zigzag):
    block = np.empty(64, np.int32)
    block[ZZ8X8] = zigzag
    return block.reshape((8, 8))


def quantize(block):
    return (block / QUANT).round().astype(np.int32)


def dequantize(block):
    return block * QUANT


def run_length_encode(arr):
    # determine where the sequence is ending prematurely
    last_nonzero = -1
    for i, elem in enumerate(arr):
        if elem != 0:
            last_nonzero = i
    # each symbol is a (RUNLENGTH, SIZE) tuple
    symbols = []
    # values are binary representations of array elements using SIZE bits
    values = []
    run_length = 0
    for i, elem in enumerate(arr):
        if i > last_nonzero:
            symbols.append((0, 0))
            values.append(int_to_binstr(0))
            break
        elif elem == 0 and run_length < 15:
            run_length += 1
        else:
            size = bits_required(elem)
            symbols.append((run_length, size))
            values.append(int_to_binstr(elem))
            run_length = 0
    return symbols, values

def fill_image(im):
    width, height = im.shape[1], im.shape[0]
    if width % 8 != 0:
        im = np.hstack((im, np.zeros((height, 8 - width % 8), dtype=np.uint8)))
    width, height = im.shape[1], im.shape[0]
    if height % 8 != 0:
        im = np.vstack((im, np.zeros((8 - height % 8, width), dtype=np.uint8)))
    return im

class ImageEncoder:
    def __init__(self) -> None:
        pass


    def encode(self, im):
        buf = io.StringIO()
        # write width and hight
        buf.write(uint_to_binstr(im.shape[1], IMG_SIZE_BITS))
        buf.write(uint_to_binstr(im.shape[0], IMG_SIZE_BITS))
        im = fill_image(im)
        width, height = im.shape[1], im.shape[0]
        blocks_count = width // 8 * height // 8
        # dc is the top-left cell of the block, ac are all the other cells
        dc = np.empty((blocks_count), dtype=np.int32)
        ac = np.empty((blocks_count, 63), dtype=np.int32)
        block_index = 0
        for i in range(0, height, 8):
            for j in range(0, width, 8):
                # split 8x8 block and center the data range on zero
                # [0, 255] --> [-128, 127]
                block = np.float32(im[i : i + 8, j : j + 8]) - 128
                dct_matrix = cv2.dct(block)
                quant_matrix = quantize(dct_matrix)
                zz = block_to_zigzag(quant_matrix)
                dc[block_index] = zz[0]
                ac[block_index, :] = zz[1:]
                block_index += 1
        dc[1:] = np.diff(dc)
        ht_dc = HuffmanTree(np.vectorize(bits_required)(dc))
        ht_ac = HuffmanTree(
            flatten(run_length_encode(ac[i])[0] for i in range(blocks_count))
        )

        dc_table = ht_dc.value_to_bitstring_table()
        ac_table = ht_ac.value_to_bitstring_table()

        # write dc table
        buf.write(uint_to_binstr(len(dc_table), TABLE_SIZE_BITS))
        for key, value in dc_table.items():
            buf.write(uint_to_binstr(key, CATEGORY_BITS))
            buf.write(uint_to_binstr(len(value), DC_CODE_LENGTH_BITS))
            buf.write(value)
        # write ac table
        buf.write(uint_to_binstr(len(ac_table), TABLE_SIZE_BITS))
        for key, value in ac_table.items():
            buf.write(uint_to_binstr(key[0], RUN_LENGTH_BITS))
            buf.write(uint_to_binstr(key[1], SIZE_BITS))
            buf.write(uint_to_binstr(len(value), AC_CODE_LENGTH_BITS))
            buf.write(value)

        for b in range(blocks_count):
            category = bits_required(dc[b])
            symbols, values = run_length_encode(ac[b])

            buf.write(dc_table[category])
            buf.write(int_to_binstr(dc[b]))

            for i in range(len(symbols)):
                buf.write(ac_table[tuple(symbols[i])])
                buf.write(values[i])

        return np.packbits(
            list(map(lambda x: int(x), buf.getvalue())), bitorder="little"
        ).tobytes()


class ImageDecoder:
    def __init__(self, data):
        bits = np.unpackbits(np.frombuffer(data, dtype=np.uint8), bitorder="little")
        bits = "".join(map(lambda x: str(x), bits))
        self.__buf = io.StringIO(bits)

    def read_dc_table(self):
        table = dict()
        table_size = self.read_uint(TABLE_SIZE_BITS)
        for _ in range(table_size):
            category = self.read_uint(CATEGORY_BITS)
            code_length = self.read_uint(DC_CODE_LENGTH_BITS)
            code = self.__buf.read(code_length)
            table[code] = category
        return table

    def read_ac_table(self):
        table = dict()
        table_size = self.read_uint(TABLE_SIZE_BITS)
        for _ in range(table_size):
            run_length = self.read_uint(RUN_LENGTH_BITS)
            size = self.read_uint(SIZE_BITS)
            code_length = self.read_uint(AC_CODE_LENGTH_BITS)
            code = self.__buf.read(code_length)
            table[code] = (run_length, size)
        return table

    def decode(self):
        width = self.read_uint(IMG_SIZE_BITS)
        height = self.read_uint(IMG_SIZE_BITS)
        blocks_count = int(np.ceil(width / 8) * np.ceil(height / 8))
        blocks_per_line = int(np.ceil(width / 8))

        dc = np.empty((blocks_count), dtype=np.int32)
        ac = np.empty((blocks_count, 63), dtype=np.int32)

        dc_table = self.read_dc_table()
        ac_table = self.read_ac_table()

        im = np.zeros((height, width), dtype=np.uint8)
        im = fill_image(im)

        dc_prev = 0
        for block_index in range(blocks_count):
            size = self.read_huffman_code(dc_table)
            dc[block_index] = self.read_int(size) + dc_prev
            dc_prev = dc[block_index]
            cells_count = 0
            while cells_count < 63:
                run_length, size = self.read_huffman_code(ac_table)
                if (run_length, size) == (0, 0):
                    while cells_count < 63:
                        ac[block_index, cells_count] = 0
                        cells_count += 1
                else:
                    for i in range(run_length):
                        ac[block_index, cells_count] = 0
                        cells_count += 1
                    if size == 0:
                        ac[block_index, cells_count] = 0
                    else:
                        value = self.read_int(size)
                        ac[block_index, cells_count] = value
                    cells_count += 1

            zigzag = np.hstack((dc[block_index], ac[block_index]))
            quant_matrix = zigzag_to_block(zigzag)
            dct_matrix = dequantize(quant_matrix)
            block = cv2.idct(np.float32(dct_matrix))
            i = int(block_index // blocks_per_line * 8)
            j = int(block_index % blocks_per_line * 8)
            block += 128
            block[block > 255] = 255
            block[block < 0] = 0
            im[i : i + 8, j : j + 8] = block
        return im[:height, :width]

    def read_huffman_code(self, table):
        prefix = ""
        while prefix not in table:
            prefix += self.__buf.read(1)
        return table[prefix]

    def read_uint(self, size):
        return int(self.__buf.read(size), 2)

    def read_int(self, size):
        if size == 0:
            return 0

        # the most significant bit indicates the sign of the number
        bin_num = self.__buf.read(size)
        if bin_num[0] == "1":
            return int(bin_num, 2)
        else:
            return int(binstr_flip(bin_num), 2) * -1
