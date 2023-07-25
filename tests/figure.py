import math
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

from tinyimgcodec import compress, decompress


def psnr(data1, data2, max_pixel=255):
    mse = np.mean((data1 - data2) ** 2)
    if mse:
        return 20 * math.log10(max_pixel / mse**0.5)
    return math.inf


image_name = ["Lenna", "Babara", "Baboon"]
image_path = ["data/lenna.gif", "data/1.gif", "data/47.gif"]

results = []
for name, path in zip(image_name, image_path):
    for q in (90, 80, 50, 20, 10, 5):
        img1 = Image.open(path).convert("L")
        img1 = np.asarray(img1)
        start = time.time()
        out = compress(img1, quality=q)
        end = time.time()
        compress_time = end - start
        start = time.time()
        img2 = decompress(out)
        end = time.time()
        decompress_time = end - start
        cr = img1.shape[0] * img1.shape[1] / len(out)
        p = psnr(img1, img2)
        results.append((name, q, cr, p, compress_time, decompress_time))

df = pd.DataFrame(
    results,
    columns=[
        "Image",
        "Quality",
        "Compression Ratio",
        "PSNR",
        "Compress Time",
        "Decompress Time",
    ],
)

metrics = ["Compression Ratio", "PSNR", "Compress Time", "Decompress Time"]

fig, ax = plt.subplots(2, 2, figsize=(10, 6), layout="constrained")
ax = ax.reshape(-1)

for j, metric in enumerate(metrics):
    x = np.arange(6)
    width = 0.25

    plt.subplot(2, 2, j + 1)
    for i, name in enumerate(image_name):
        offset = width * i
        df2 = df[df["Image"] == name]
        ax[j].bar(x + offset, df2[metric], width, label=name, zorder=3)

    plt.xticks(x + width, [str(q) for q in (90, 80, 50, 20, 10, 5)])
    plt.legend(ncols=3)
    plt.xlabel("Quality")
    plt.ylabel(metric)
    plt.grid(color="#e0e0e0", zorder=0)
plt.show()
