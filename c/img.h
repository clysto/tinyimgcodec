#ifndef IMG_H
#define IMG_H

#include <stdint.h>

#include "bitwriter.h"
#include "fifo.h"

#define DCTSIZE 8

typedef struct {
    uint8_t *buf;
    size_t bufSize;
    int width;
    int height;
    int blocksPerLine;
    int prevDC;
    BitWriter bitWriter;
} Image;

Image *IMG_create(int width, int height);
void IMG_destroy(Image *img);
void IMG_compressStart(Image *img, FIFO *fifo);
void IMG_compressPush(Image *img, uint8_t *data, size_t size, FIFO *fifo);
void IMG_compressComplete(Image *img, FIFO *fifo);

#endif
