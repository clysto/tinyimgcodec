#ifndef IMG_H
#define IMG_H

#include <stdint.h>

#include "fifo.h"

typedef struct {
    uint32_t putBuffer;
    int putBits;
} BitWriter;

typedef struct {
    int width;
    int height;
    int prevDC;
    int blockCount;
    int rstIndex;
    uint8_t qfactor;
    uint16_t scaledQuant[64];
    BitWriter bitWriter;
} Image;

enum { IMG_Q_BEST = 0, IMG_Q_HIGH, IMG_Q_MED, IMG_Q_LOW };

#define BB_emitBits(writer, fifo, code, size)                                                       \
    do {                                                                                            \
        (writer)->putBuffer |= ((code & ((1 << (size)) - 1)) << (32 - (size) - (writer)->putBits)); \
        (writer)->putBits += (size);                                                                \
        while ((writer)->putBits >= 8) {                                                            \
            uint8_t byte = (writer)->putBuffer >> 24;                                               \
            FIFO_writeEscapeByte(fifo, byte);                                                       \
            (writer)->putBuffer <<= 8;                                                              \
            (writer)->putBits -= 8;                                                                 \
        }                                                                                           \
    } while (0)

#define BB_flushBits(writer, fifo) BB_emitBits(writer, fifo, 0, (8 - ((writer)->putBits)) & 7);

void IMG_init(Image *img, int width, int height, uint8_t qfactor);
void IMG_encodeHeader(Image *img, FIFO *fifo);
void IMG_encodeComplete(Image *img, FIFO *fifo);
void IMG_encodeBlock(Image *img, const uint8_t data[64], FIFO *fifo);

#endif
