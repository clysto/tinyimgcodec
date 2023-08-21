import sys
import time
from subprocess import PIPE, Popen

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

from tests.psnr import psnr
from tinyimgcodec import decompress

encoder = sys.argv[1]

image_name = ["Lenna", "Babara", "Baboon"]
image_path = ["data/lenna.gif", "data/1.gif", "data/47.gif"]

results = []

for i in range(3):
    img1 = Image.open(image_path[i]).convert("L")
    img1 = np.asarray(img1)
    for q in ("best", "high", "med", "low"):
        process = Popen([encoder, "512", "512", q], stdin=PIPE, stdout=PIPE)
        start = time.time()
        out = process.communicate(input=img1.tobytes())[0]
        end = time.time()
        img2 = decompress(out)
        p = psnr(img1, img2)
        cr = img1.shape[0] * img1.shape[1] / len(out)
        results.append((image_name[i], q, cr, p, end - start))


df = pd.DataFrame(
    results,
    columns=[
        "Image",
        "Quality",
        "Compression Ratio",
        "PSNR",
        "Compress Time",
    ],
)

metrics = ["Compression Ratio", "PSNR", "Compress Time"]

fig, ax = plt.subplots(1, 3, figsize=(15, 3), layout="constrained")
ax = ax.reshape(-1)

for j, metric in enumerate(metrics):
    x = np.arange(4)
    width = 0.25

    plt.subplot(1, 3, j + 1)
    for i, name in enumerate(image_name):
        offset = width * i
        df2 = df[df["Image"] == name]
        ax[j].bar(x + offset, df2[metric], width, label=name, zorder=3)

    plt.xticks(x + width, [str(q) for q in ("best", "high", "med", "low")])
    plt.legend(ncols=3)
    plt.xlabel("Quality")
    plt.ylabel(metric)
    plt.grid(color="#e0e0e0", zorder=0)

plt.savefig("tests/result_c.png", dpi=300)
plt.show()
