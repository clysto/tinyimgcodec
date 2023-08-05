#ifndef BITBUF_H
#define BITBUF_H

#include <stdint.h>

#define BB_ONE 0x80000000
#define BB_ZERO 0x00000000

typedef struct {
  uint32_t putBuffer;
  int putBits;
  uint8_t *out;
} BitBuffer;

void BB_emitBits(BitBuffer *bb, uint32_t code, int size);
void BB_emitByte(BitBuffer *bb, uint8_t byte);
void BB_flushBits(BitBuffer *bb);

#endif