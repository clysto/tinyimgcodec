import io
import itertools

import numpy as np
from bidict import bidict

from .constants import AC, DC, EOB, HUFFMAN_CATEGORY_CODEWORD, ZRL
from .utils import binstr_to_int, bits_required, int_to_binstr


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


def encode_huffman(buf: io.StringIO, symbols, dc_ac=DC):
    if dc_ac == DC:
        values = map(int_to_binstr, symbols)
        categories = bits_required(symbols)
    elif dc_ac == AC:
        symbols = np.array(symbols)
        values = map(int_to_binstr, symbols[:, 1].copy())
        symbols[:, 1] = bits_required(symbols[:, 1])
        categories = map(tuple, symbols)
    else:
        raise ValueError("dc_ac should be either DC or AC.")
    for category, value in zip(categories, values):
        buf.write(HUFFMAN_CATEGORY_CODEWORD[dc_ac][category])
        buf.write(value)


def read_huffman_code(buf: io.StringIO, table: bidict):
    prefix = ""
    while prefix not in table:
        prefix += buf.read(1)
    return table[prefix]


def decode_huffman(buf: io.StringIO, length: int = 0, dc_ac=DC):
    table = HUFFMAN_CATEGORY_CODEWORD[dc_ac].inverse
    symbols = []
    if dc_ac == DC:
        for _ in range(length):
            category = read_huffman_code(buf, table)
            value = binstr_to_int(buf.read(category)) if category > 0 else 0
            symbols.append(value)
    elif dc_ac == AC:
        while True:
            category = read_huffman_code(buf, table)
            run_length, size = category
            value = binstr_to_int(buf.read(size)) if size > 0 else 0
            symbols.append((run_length, value))
            if category == EOB:
                break
    return symbols
