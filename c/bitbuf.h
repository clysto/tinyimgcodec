#ifndef BITBUF_H
#define BITBUF_H

#include <stddef.h>
#include <stdint.h>

typedef struct {
    uint32_t putBuffer;
    int putBits;
    size_t size;
    uint8_t *out;
} BitBuffer;

void BB_emitBits(BitBuffer *bb, uint32_t code, int size);
void BB_emitByte(BitBuffer *bb, uint8_t byte);
void BB_flushBits(BitBuffer *bb);

#endif