#ifndef HUFF_H
#define HUFF_H

#include <stdint.h>

extern const uint32_t DC_HUFF_TABLE[12];
extern const uint8_t DC_HUFF_TABLE_CODELEN[12];
extern const uint32_t AC_HUFF_TABLE[16][11];
extern const uint8_t AC_HUFF_TABLE_CODELEN[16][11];

#endif