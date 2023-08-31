#!/usr/bin/env python3

import sys

import numpy as np
from viterbi import Viterbi

codec = Viterbi(
    7, [0o133, 0o171], [1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1]
)

data = np.frombuffer(sys.stdin.buffer.read(), dtype=np.uint8)
data = np.unpackbits(data)

r = len(data) * 2 % 18
r = (18 - r) % 18
r = np.zeros(r // 2, dtype=np.uint8)

data = np.hstack((data, r))
data = codec.encode(data)

sys.stdout.buffer.write(np.packbits(data))
