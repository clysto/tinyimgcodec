#ifndef BITBUF_H
#define BITBUF_H

#include <stddef.h>
#include <stdint.h>

#include "fifo.h"

typedef struct {
    uint32_t putBuffer;
    int putBits;
} BitWriter;

void BB_emitBits(BitWriter *writer, FIFO *fifo, uint32_t code, int size);
void BB_flushBits(BitWriter *writer, FIFO *fifo);

#endif