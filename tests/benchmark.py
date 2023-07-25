import math
import time

import numpy as np
import pandas as pd
from PIL import Image
from tqdm import tqdm

from tinyimgcodec import compress, decompress


def psnr(data1, data2, max_pixel=255):
    mse = np.mean((data1 - data2) ** 2)
    if mse:
        return 20 * math.log10(max_pixel / mse**0.5)
    return math.inf


results = []
for i in tqdm(range(49)):
    for q in (90, 80, 50, 20, 10, 5):
        img1 = Image.open(f"data/{i + 1}.gif").convert("L")
        img1 = np.asarray(img1)
        start = time.time()
        out = compress(img1, quality=q)
        end = time.time()
        img2 = decompress(out)
        cr = img1.shape[0] * img1.shape[1] / len(out)
        p = psnr(img1, img2)
        results.append((i + 1, q, cr, p, end - start))

df = pd.DataFrame(
    results, columns=["Image", "Quality", "Compression Ratio", "PSNR", "Time"]
)
print(df)
df.to_csv("benchmark.csv", index=False)
