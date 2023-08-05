#ifndef IMG_H
#define IMG_H

#include <stdint.h>
#include "bitbuf.h"

#define DCTSIZE 8

typedef struct {
    uint8_t *out;
    uint8_t *buf;
    int bufSize;
    int outSize;
    int width;
    int height;
    int blocksPerRow;
    int blocksPerCol;
    BitBuffer bitBuffer;
} Image;

Image *IMG_create(int width, int height);

void IMG_push(Image *img, uint8_t *data, int size);

void IMG_destroy(Image *img);

#endif
