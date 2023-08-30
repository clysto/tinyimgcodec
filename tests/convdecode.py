#!/usr/bin/env python3


import sys

import numpy as np
from viterbi import Viterbi

codec = Viterbi(
    7, [0o133, 0o171], [1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1]
)

data = np.frombuffer(sys.stdin.buffer.read(), dtype=np.uint8)

data = codec.decode(np.unpackbits(data))

sys.stdout.buffer.write(np.packbits(data))
