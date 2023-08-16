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
    uint16_t scaledQuant[64];
    BitWriter bitWriter;
} Image;

#define BB_emitBits(writer, fifo, code, size)                                                   \
    do {                                                                                        \
        (writer)->putBuffer |= ((code & ((1 << size) - 1)) << (32 - size - (writer)->putBits)); \
        (writer)->putBits += size;                                                              \
        while ((writer)->putBits >= 8) {                                                        \
            uint8_t byte = (writer)->putBuffer >> 24;                                           \
            FIFO_writeByte(fifo, byte);                                                         \
            (writer)->putBuffer <<= 8;                                                          \
            (writer)->putBits -= 8;                                                             \
        }                                                                                       \
    } while (0)

#define BB_flushBits(writer, fifo)                       \
    do {                                                 \
        FIFO_writeByte(fifo, (writer)->putBuffer >> 24); \
        (writer)->putBits = 0;                           \
    } while (0)

void IMG_init(Image *img, int width, int height);
void IMG_encodeHeader(Image *img, FIFO *fifo);
void IMG_encodeComplete(Image *img, FIFO *fifo);
void IMG_encodeBlock(Image *img, const uint8_t data[64], FIFO *fifo);

#endif
