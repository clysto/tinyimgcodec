#include "bitwriter.h"

void BB_emitBits(BitWriter *writer, FIFO *fifo, uint32_t code, int size) {
    code &= (1 << size) - 1;
    writer->putBuffer |= (code << (32 - size - writer->putBits));
    writer->putBits += size;
    while (writer->putBits >= 8) {
        uint8_t byte = writer->putBuffer >> 24;
        FIFO_writeByte(fifo, byte);
        writer->putBuffer <<= 8;
        writer->putBits -= 8;
    }
}

void BB_flushBits(BitWriter *writer, FIFO *fifo) {
    uint8_t byte = writer->putBuffer >> 24;
    FIFO_writeByte(fifo, byte);
    writer->putBits = 0;
}
