#!/usr/bin/env python3

import sys
import random

PROTECT_HEADER_BYTES = 16


def main():
    if len(sys.argv) != 4:
        print("Usage: adderr.py <file> <out> <ber>")
        sys.exit(1)
    filename = sys.argv[1]
    ber = sys.argv[3]
    with open(filename, "rb") as f:
        data = f.read()

    data = bytearray(data)

    for i in range(len(data)):
        if i < PROTECT_HEADER_BYTES:
            continue
        for j in range(8):
            if random.random() < float(ber):
                data[i] ^= 1 << j

    with open(sys.argv[2], "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
