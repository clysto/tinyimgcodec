#include "img.h"

#include <stdlib.h>
#include <string.h>

#include "bitbuf.h"

const uint8_t QUANT[64] = {16, 11, 10, 16, 24, 40, 51, 61, 12, 12, 14, 19, 26, 58, 60, 55,
                           14, 13, 16, 24, 40, 57, 69, 56, 14, 17, 22, 29, 51, 87, 80, 62,
                           18, 22, 37, 56, 68, 109, 103, 77, 24, 35, 55, 64, 81, 104, 113, 92,
                           49, 64, 78, 87, 103, 121, 120, 101, 72, 92, 95, 98, 112, 100, 103, 99};


void fdct(double *data) {
    double tmp0, tmp1, tmp2, tmp3, tmp4, tmp5, tmp6, tmp7;
    double tmp10, tmp11, tmp12, tmp13;
    double z1, z2, z3, z4, z5, z11, z13;
    double *dataptr;
    int ctr;
    dataptr = data;
    for (ctr = DCTSIZE - 1; ctr >= 0; ctr--) {
        tmp0 = dataptr[0] + dataptr[7];
        tmp7 = dataptr[0] - dataptr[7];
        tmp1 = dataptr[1] + dataptr[6];
        tmp6 = dataptr[1] - dataptr[6];
        tmp2 = dataptr[2] + dataptr[5];
        tmp5 = dataptr[2] - dataptr[5];
        tmp3 = dataptr[3] + dataptr[4];
        tmp4 = dataptr[3] - dataptr[4];
        tmp10 = tmp0 + tmp3;
        tmp13 = tmp0 - tmp3;
        tmp11 = tmp1 + tmp2;
        tmp12 = tmp1 - tmp2;
        dataptr[0] = tmp10 + tmp11;
        dataptr[4] = tmp10 - tmp11;
        z1 = (tmp12 + tmp13) * ((double) 0.707106781);
        dataptr[2] = tmp13 + z1;
        dataptr[6] = tmp13 - z1;
        tmp10 = tmp4 + tmp5;
        tmp11 = tmp5 + tmp6;
        tmp12 = tmp6 + tmp7;
        z5 = (tmp10 - tmp12) * ((double) 0.382683433);
        z2 = ((double) 0.541196100) * tmp10 + z5;
        z4 = ((double) 1.306562965) * tmp12 + z5;
        z3 = tmp11 * ((double) 0.707106781);
        z11 = tmp7 + z3;
        z13 = tmp7 - z3;
        dataptr[5] = z13 + z2;
        dataptr[3] = z13 - z2;
        dataptr[1] = z11 + z4;
        dataptr[7] = z11 - z4;
        dataptr += DCTSIZE;
    }

    dataptr = data;
    for (ctr = DCTSIZE - 1; ctr >= 0; ctr--) {
        tmp0 = dataptr[DCTSIZE * 0] + dataptr[DCTSIZE * 7];
        tmp7 = dataptr[DCTSIZE * 0] - dataptr[DCTSIZE * 7];
        tmp1 = dataptr[DCTSIZE * 1] + dataptr[DCTSIZE * 6];
        tmp6 = dataptr[DCTSIZE * 1] - dataptr[DCTSIZE * 6];
        tmp2 = dataptr[DCTSIZE * 2] + dataptr[DCTSIZE * 5];
        tmp5 = dataptr[DCTSIZE * 2] - dataptr[DCTSIZE * 5];
        tmp3 = dataptr[DCTSIZE * 3] + dataptr[DCTSIZE * 4];
        tmp4 = dataptr[DCTSIZE * 3] - dataptr[DCTSIZE * 4];
        tmp10 = tmp0 + tmp3;
        tmp13 = tmp0 - tmp3;
        tmp11 = tmp1 + tmp2;
        tmp12 = tmp1 - tmp2;
        dataptr[DCTSIZE * 0] = tmp10 + tmp11;
        dataptr[DCTSIZE * 4] = tmp10 - tmp11;
        z1 = (tmp12 + tmp13) * ((double) 0.707106781);
        dataptr[DCTSIZE * 2] = tmp13 + z1;
        dataptr[DCTSIZE * 6] = tmp13 - z1;
        tmp10 = tmp4 + tmp5;
        tmp11 = tmp5 + tmp6;
        tmp12 = tmp6 + tmp7;
        z5 = (tmp10 - tmp12) * ((double) 0.382683433);
        z2 = ((double) 0.541196100) * tmp10 + z5;
        z4 = ((double) 1.306562965) * tmp12 + z5;
        z3 = tmp11 * ((double) 0.707106781);
        z11 = tmp7 + z3;
        z13 = tmp7 - z3;
        dataptr[DCTSIZE * 5] = z13 + z2;
        dataptr[DCTSIZE * 3] = z13 - z2;
        dataptr[DCTSIZE * 1] = z11 + z4;
        dataptr[DCTSIZE * 7] = z11 - z4;
        dataptr++;
    }
}

void IMG_encodeHuffman(BitBuffer *bb, int *data, int size) {

}

Image *IMG_create(int width, int height) {
    Image *img = (Image *) malloc(sizeof(Image));
    img->out = malloc(width * height * 8);
    img->width = width;
    img->height = height;
    img->outSize = 0;
    img->buf = malloc(width * 8);
    img->blocksPerRow = width / 8;
    img->blocksPerCol = height / 8;
    img->bufSize = 0;
    img->bitBuffer.out = img->out;
    img->bitBuffer.putBits = 0;
    return img;
}

void IMG_push(Image *img, uint8_t *data, int size) {
    int copySize = size;
    if (size > img->width * 8 - img->bufSize) {
        copySize = img->width * 8 - img->bufSize;
    }
    memcpy(img->buf + img->bufSize, data, copySize);
    img->bufSize += copySize;
    if (img->bufSize == img->width * 8) {
        for (int k = 0; k < img->blocksPerRow; k++) {
            double block[64];
            int i, j;
            for (i = 0; i < 8; i++) {
                for (j = 0; j < 8; j++) {
                    block[i * 8 + j] = (double) (img->buf[i * img->width + j + k * 8]) - 128;
                }
            }
            fdct(block);
            memcpy(img->out + img->outSize, block, 64 * sizeof(double));
            img->outSize += 64 * sizeof(double);
        }
        img->bufSize = 0;
    }
    if (copySize < size) {
        IMG_push(img, data + copySize, size - copySize);
    }
}

void IMG_destroy(Image *img) {
    free(img->out);
    free(img->buf);
    free(img);
}
