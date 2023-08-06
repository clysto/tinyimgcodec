#ifndef IMG_H
#define IMG_H

#include <stdint.h>

#include "bitbuf.h"

#define DCTSIZE 8

typedef struct {
    uint8_t *out;
    uint8_t *buf;
    size_t outSize;
    size_t bufSize;
    int width;
    int height;
    int blocksPerLine;
    int prevDC;
    BitBuffer bitBuffer;
} Image;

Image *IMG_create(int width, int height);

void IMG_push(Image *img, uint8_t *data, size_t size);

void IMG_destroy(Image *img);

void IMG_complete(Image *img);

void IMG_dcEncodeHuffman(BitBuffer *bb, int data);

int IMG_encodeRunlength(int data, int zeroCnt, int *runlength, int *value);

#endif
