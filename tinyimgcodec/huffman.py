import itertools
from queue import PriorityQueue

import numpy as np
from bidict import bidict

from .bitbuffer import BitBuffer
from .constants import AC, DC, EOB, HUFFMAN_CATEGORY_CODEWORD, ZRL
from .utils import bits_required


def encode_run_length(seq):
    groups = [(len(tuple(group)), key) for key, group in itertools.groupby(seq)]
    ret = []
    borrow = False  # Borrow one pair in the next group whose key is nonzero.
    if groups[-1][1] == 0:
        del groups[-1]
    for idx, (length, key) in enumerate(groups):
        if borrow:
            length -= 1
            borrow = False
        if length == 0:
            continue
        if key == 0:
            # Deal with the case run (0s) more than 16 --> ZRL.
            while length >= 16:
                ret.append(ZRL)
                length -= 16
            ret.append((length, groups[idx + 1][1]))
            borrow = True
        else:
            ret.extend(((0, key),) * length)
    return ret + [EOB]


def decode_run_length(seq):
    # Remove the last element as the last created by EOB would always be a `0`.
    return tuple(item for l, k in seq for item in [0] * l + [k])[:-1]


def encode_huffman(
    buf: BitBuffer,
    symbols,
    dc_ac=DC,
    category_codeword=HUFFMAN_CATEGORY_CODEWORD,
):
    if dc_ac == DC:
        values = symbols
        categories = bits_required(symbols)
        values_length = categories
    elif dc_ac == AC:
        symbols = np.array(symbols)
        values = symbols[:, 1].copy()
        symbols[:, 1] = bits_required(symbols[:, 1])
        categories = map(tuple, symbols)
        values_length = symbols[:, 1]
    else:
        raise ValueError("dc_ac should be either DC or AC.")
    values_str = np.unpackbits(np.abs(values).astype(">u2").view(np.uint8))
    values_str = values_str.reshape(-1, 16) ^ (values < 0).reshape((-1, 1))
    for category, value, l in zip(categories, values_str, values_length):
        buf.write(category_codeword[dc_ac][category])
        buf.write(value[16 - l :])


def read_huffman_code(buf: BitBuffer, table: bidict):
    prefix = ""
    i = 0
    while prefix not in table and i <= 16:
        prefix += buf.read(1).to01()
        i += 1
    if i > 16:
        raise ValueError("Invalid Huffman code.")
    return table[prefix]


def decode_huffman(
    buf: BitBuffer,
    length: int = 0,
    dc_ac=DC,
    category_codeword=HUFFMAN_CATEGORY_CODEWORD,
):
    table = category_codeword[dc_ac].inverse
    symbols = []
    if dc_ac == DC:
        for _ in range(length):
            category = read_huffman_code(buf, table)
            value = buf.read_int(category)
            symbols.append(value)
    elif dc_ac == AC:
        while True:
            category = read_huffman_code(buf, table)
            run_length, size = category
            value = buf.read_int(size)
            symbols.append((run_length, value))
            if category == EOB:
                break
    return symbols


def calc_huffman_table(dc, ac):
    ac = np.array(ac)
    ac[:, 1] = bits_required(ac[:, 1])
    category_ac = map(tuple, ac)
    category_dc = bits_required(dc)
    return {
        DC: HuffmanTree(category_dc).value_to_bitstring_table(),
        AC: HuffmanTree(category_ac).value_to_bitstring_table(),
    }


class HuffmanTree:
    class __Node:
        def __init__(self, value, freq, left_child, right_child):
            self.value = value
            self.freq = freq
            self.left_child = left_child
            self.right_child = right_child

        @classmethod
        def init_leaf(cls, value, freq):
            return cls(value, freq, None, None)

        @classmethod
        def init_node(cls, left_child, right_child):
            freq = left_child.freq + right_child.freq
            return cls(None, freq, left_child, right_child)

        def is_leaf(self):
            return self.value is not None

        def __eq__(self, other):
            stup = self.value, self.freq, self.left_child, self.right_child
            otup = other.value, other.freq, other.left_child, other.right_child
            return stup == otup

        def __nq__(self, other):
            return not (self == other)

        def __lt__(self, other):
            return self.freq < other.freq

        def __le__(self, other):
            return self.freq < other.freq or self.freq == other.freq

        def __gt__(self, other):
            return not (self <= other)

        def __ge__(self, other):
            return not (self < other)

    def __init__(self, arr):
        q = PriorityQueue()

        # calculate frequencies and insert them into a priority queue
        for val, freq in self.__calc_freq(arr).items():
            q.put(self.__Node.init_leaf(val, freq))

        while q.qsize() >= 2:
            u = q.get()
            v = q.get()

            q.put(self.__Node.init_node(u, v))

        self.__root = q.get()

        # dictionaries to store huffman table
        self.__value_to_bitstring = bidict()

    def value_to_bitstring_table(self):
        if len(self.__value_to_bitstring.keys()) == 0:
            self.__create_huffman_table()
        return self.__value_to_bitstring

    def __create_huffman_table(self):
        def tree_traverse(current_node, bitstring=""):
            if current_node is None:
                return
            if current_node.is_leaf():
                self.__value_to_bitstring[current_node.value] = bitstring
                return
            tree_traverse(current_node.left_child, bitstring + "0")
            tree_traverse(current_node.right_child, bitstring + "1")

        tree_traverse(self.__root)

    def __calc_freq(self, arr):
        freq_dict = dict()
        for elem in arr:
            if elem in freq_dict:
                freq_dict[elem] += 1
            else:
                freq_dict[elem] = 1
        return freq_dict
