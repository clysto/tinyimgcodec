#include "img.h"

#include <math.h>
#include <stdlib.h>
#include <string.h>

#include "bitbuf.h"
#include "huff.h"

const uint8_t QUANT[64] = {16, 11, 10, 16, 24,  40,  51,  61,  12, 12, 14, 19, 26,  58,  60,  55,
                           14, 13, 16, 24, 40,  57,  69,  56,  14, 17, 22, 29, 51,  87,  80,  62,
                           18, 22, 37, 56, 68,  109, 103, 77,  24, 35, 55, 64, 81,  104, 113, 92,
                           49, 64, 78, 87, 103, 121, 120, 101, 72, 92, 95, 98, 112, 100, 103, 99};
const uint8_t ZIGZAG[64] = {0,  1,  8,  16, 9,  2,  3,  10, 17, 24, 32, 25, 18, 11, 4,  5,  12, 19, 26, 33, 40, 48,
                            41, 34, 27, 20, 13, 6,  7,  14, 21, 28, 35, 42, 49, 56, 57, 50, 43, 36, 29, 22, 15, 23,
                            30, 37, 44, 51, 58, 59, 52, 45, 38, 31, 39, 46, 53, 60, 61, 54, 47, 55, 62, 63};

void IMG_fdct(double *data) {
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
        z1 = (tmp12 + tmp13) * ((double)0.707106781);
        dataptr[2] = tmp13 + z1;
        dataptr[6] = tmp13 - z1;
        tmp10 = tmp4 + tmp5;
        tmp11 = tmp5 + tmp6;
        tmp12 = tmp6 + tmp7;
        z5 = (tmp10 - tmp12) * ((double)0.382683433);
        z2 = ((double)0.541196100) * tmp10 + z5;
        z4 = ((double)1.306562965) * tmp12 + z5;
        z3 = tmp11 * ((double)0.707106781);
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
        z1 = (tmp12 + tmp13) * ((double)0.707106781);
        dataptr[DCTSIZE * 2] = tmp13 + z1;
        dataptr[DCTSIZE * 6] = tmp13 - z1;
        tmp10 = tmp4 + tmp5;
        tmp11 = tmp5 + tmp6;
        tmp12 = tmp6 + tmp7;
        z5 = (tmp10 - tmp12) * ((double)0.382683433);
        z2 = ((double)0.541196100) * tmp10 + z5;
        z4 = ((double)1.306562965) * tmp12 + z5;
        z3 = tmp11 * ((double)0.707106781);
        z11 = tmp7 + z3;
        z13 = tmp7 - z3;
        dataptr[DCTSIZE * 5] = z13 + z2;
        dataptr[DCTSIZE * 3] = z13 - z2;
        dataptr[DCTSIZE * 1] = z11 + z4;
        dataptr[DCTSIZE * 7] = z11 - z4;
        dataptr++;
    }
}

int IMG_encodeRunlength(int data, int zeroCnt, int *runlength, int *value) {
    if (data == 0) {
        zeroCnt++;
        if (zeroCnt >= 16) {
            *runlength = 15;
            *value = 0;
            return 0;
        }
        return zeroCnt;
    } else {
        *runlength = zeroCnt;
        *value = data;
        return 0;
    }
}

void IMG_dcEncodeHuffman(BitBuffer *bb, int data) {
    uint32_t value = data > 0 ? data : -data;
    int bits = data != 0 ? 32 - __builtin_clz(value) : 0;
    BB_emitBits(bb, DC_HUFF_TABLE[bits], DC_HUFF_TABLE_CODELEN[bits]);
    if (data == 0) {
        return;
    }
    if (data < 0) {
        BB_emitBits(bb, ~value, bits);
    } else {
        BB_emitBits(bb, value, bits);
    }
}

void IMG_acEncodeHuffman(BitBuffer *bb, int runlength, int data) {
    uint32_t value = data > 0 ? data : -data;
    int bits = data != 0 ? 32 - __builtin_clz(value) : 0;
    uint32_t category = AC_HUFF_TABLE[runlength][bits];
    int codeLen = AC_HUFF_TABLE_CODELEN[runlength][bits];
    BB_emitBits(bb, category, codeLen);
    if (data == 0) {
        return;
    }
    if (data < 0) {
        BB_emitBits(bb, ~value, bits);
    } else {
        BB_emitBits(bb, value, bits);
    }
}

Image *IMG_create(int width, int height) {
    Image *img = (Image *)malloc(sizeof(Image));
    img->out = malloc(width * height * 8);
    img->width = width;
    img->height = height;
    img->prevDC = 0;
    img->buf = malloc(width * 8);
    img->blocksPerLine = width / 8;
    img->bufSize = 0;
    img->bitBuffer.out = img->out;
    img->bitBuffer.putBits = 0;
    int quality = 50;
    uint32_t flag = 1 << 30;
    memcpy(img->out, &height, 4);
    memcpy(img->out + 4, &width, 4);
    memcpy(img->out + 8, &quality, 4);
    memcpy(img->out + 12, &flag, 4);
    img->bitBuffer.size = 16;
    return img;
}

void IMG_push(Image *img, uint8_t *data, size_t size) {
    size_t copySize = size;
    if (size > img->width * 8 - img->bufSize) {
        copySize = img->width * 8 - img->bufSize;
    }
    memcpy(img->buf + img->bufSize, data, copySize);
    img->bufSize += copySize;
    if (img->bufSize == img->width * 8) {
        for (int k = 0; k < img->blocksPerLine; k++) {
            double block[64];
            int i, j;
            for (i = 0; i < 8; i++) {
                for (j = 0; j < 8; j++) {
                    block[i * 8 + j] = (double)(img->buf[i * img->width + j + k * 8]) - 128;
                }
            }
            IMG_fdct(block);
            // write DC value
            int dc = (int)round(block[0] / QUANT[0] / 8);
            IMG_dcEncodeHuffman(&img->bitBuffer, dc - img->prevDC);
            img->prevDC = dc;
            int zeroCnt = 0, runlength, value, zrlCnt = 0;
            for (i = 1; i < 63; i++) {
                zeroCnt = IMG_encodeRunlength((int)round(block[ZIGZAG[i]] / QUANT[ZIGZAG[i]] / 8), zeroCnt, &runlength,
                                              &value);
                if (zeroCnt == 0) {
                    if (runlength == 15 && value == 0) {
                        zrlCnt++;
                    } else {
                        // write AC value
                        while (zrlCnt > 0) {
                            IMG_acEncodeHuffman(&img->bitBuffer, 15, 0);
                            zrlCnt--;
                        }
                        IMG_acEncodeHuffman(&img->bitBuffer, runlength, value);
                    }
                }
            }
            // write EOB
            IMG_acEncodeHuffman(&img->bitBuffer, 0, 0);
        }
        img->bufSize = 0;
        img->outSize = img->bitBuffer.size;
    }
    if (copySize < size) {
        IMG_push(img, data + copySize, size - copySize);
    }
}

void IMG_complete(Image *img) {
    BB_flushBits(&img->bitBuffer);
    img->outSize = img->bitBuffer.size;
}

void IMG_destroy(Image *img) {
    free(img->out);
    free(img->buf);
    free(img);
}
