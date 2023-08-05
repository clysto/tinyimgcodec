# %%
import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import dct, idct


data = np.fromfile(
    "/Users/maoyachen/Code/tinyimgcodec/c/lenna_dct.dat", dtype=np.float64
)


data = data.reshape(-1, 64)


# plt.figure()
# plt.imshow(data[0].reshape(8, 8), cmap="gray")
# plt.show()


# %%
def block_combine(tiled_array: np.ndarray):
    h, w, tile_height, tile_width = tiled_array.shape
    height = h * tile_height
    width = w * tile_width
    tiled_array = tiled_array.swapaxes(1, 2)
    image = tiled_array.reshape(height, width)
    return image


def block_slice(image: np.ndarray, kernel_size: tuple):
    img_height, img_width = image.shape
    tile_height, tile_width = kernel_size
    tiled_array = image.reshape(
        img_height // tile_height, tile_height, img_width // tile_width, tile_width
    )
    tiled_array = tiled_array.swapaxes(1, 2)
    return tiled_array


def block_idct(image: np.ndarray):
    return idct(
        idct(image, norm="ortho", axis=-2),
        axis=-1,
        norm="ortho",
    )


def block_dct(image: np.ndarray):
    return dct(
        dct(image, norm="ortho", axis=-2),
        axis=-1,
        norm="ortho",
    )


annscales = np.array(
    [
        16384,
        22725,
        21407,
        19266,
        16384,
        12873,
        8867,
        4520,
        22725,
        31521,
        29692,
        26722,
        22725,
        17855,
        12299,
        6270,
        21407,
        29692,
        27969,
        25172,
        21407,
        16819,
        11585,
        5906,
        19266,
        26722,
        25172,
        22654,
        19266,
        15137,
        10426,
        5315,
        16384,
        22725,
        21407,
        19266,
        16384,
        12873,
        8867,
        4520,
        12873,
        17855,
        16819,
        15137,
        12873,
        10114,
        6967,
        3552,
        8867,
        12299,
        11585,
        10426,
        8867,
        6967,
        4799,
        2446,
        4520,
        6270,
        5906,
        5315,
        4520,
        3552,
        2446,
        1247,
    ]
) / 2048

# %%
oo = np.fromfile(
    "/Users/maoyachen/Code/tinyimgcodec/c/lenna.dat", dtype=np.uint8
).reshape(512, 512)
ii = block_dct(block_slice(oo - 128, (8, 8))).reshape(-1, 8, 8)


im = (data / annscales).reshape(64, 64, 8, 8) 
im = block_idct(im)
im = block_combine(im) + 128

plt.figure()
plt.imshow(im, cmap="gray", vmin=0, vmax=255)
plt.show(block=False)

plt.figure()
plt.imshow(oo, cmap="gray", vmin=0, vmax=255)
plt.show()
# %%
