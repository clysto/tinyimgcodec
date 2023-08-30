#!/usr/bin/env python3

import sys
import random

PROTECT_HEADER_BYTES = 32


def main():
    if len(sys.argv) != 2:
        print("Usage: adderr.py <ber>")
        sys.exit(1)
    ber = sys.argv[1]
    data = sys.stdin.buffer.read()
    data = bytearray(data)
    for i in range(len(data)):
        if i < PROTECT_HEADER_BYTES:
            continue
        for j in range(8):
            if random.random() < float(ber):
                data[i] ^= 1 << j
    sys.stdout.buffer.write(data)


if __name__ == "__main__":
    main()
