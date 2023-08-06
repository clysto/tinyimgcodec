#include "bitbuf.h"

void BB_emitBits(BitBuffer *bb, uint32_t code, int size) {
    code &= (1 << size) - 1;
    bb->putBuffer |= (code << (32 - size - bb->putBits));
    bb->putBits += size;
    while (bb->putBits >= 8) {
        uint8_t b = bb->putBuffer >> 24;
        BB_emitByte(bb, b);
        bb->putBuffer <<= 8;
        bb->putBits -= 8;
    }
}

void BB_emitByte(BitBuffer *bb, uint8_t byte) {
    bb->out[bb->size++] = byte;
}

void BB_flushBits(BitBuffer *bb) {
    uint8_t b = bb->putBuffer >> 24;
    BB_emitByte(bb, b);
    bb->putBits = 0;
}
