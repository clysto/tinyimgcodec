#include "img.h"

#include "fifo.h"

const uint32_t DC_HUFF_TABLE[12] = {0x0000, 0x0002, 0x0003, 0x0004, 0x0005, 0x0006,
                                    0x000e, 0x001e, 0x003e, 0x007e, 0x00fe, 0x01fe};

const uint8_t DC_HUFF_TABLE_CODELEN[12] = {2, 3, 3, 3, 3, 3, 4, 5, 6, 7, 8, 9};

const uint32_t AC_HUFF_TABLE[16][11] = {
    {0x000a, 0x0000, 0x0001, 0x0004, 0x000b, 0x001a, 0x0078, 0x00f8, 0x03f6, 0xff82, 0xff83},
    {0x0000, 0x000c, 0x001b, 0x0079, 0x01f6, 0x07f6, 0xff84, 0xff85, 0xff86, 0xff87, 0xff88},
    {0x0000, 0x001c, 0x00f9, 0x03f7, 0x0ff4, 0xff89, 0xff8a, 0xff8b, 0xff8c, 0xff8d, 0xff8e},
    {0x0000, 0x003a, 0x01f7, 0x0ff5, 0xff8f, 0xff90, 0xff91, 0xff92, 0xff93, 0xff94, 0xff95},
    {0x0000, 0x003b, 0x03f8, 0xff96, 0xff97, 0xff98, 0xff99, 0xff9a, 0xff9b, 0xff9c, 0xff9d},
    {0x0000, 0x007a, 0x07f7, 0xff9e, 0xff9f, 0xffa0, 0xffa1, 0xffa2, 0xffa3, 0xffa4, 0xffa5},
    {0x0000, 0x007b, 0x0ff6, 0xffa6, 0xffa7, 0xffa8, 0xffa9, 0xffaa, 0xffab, 0xffac, 0xffad},
    {0x0000, 0x00fa, 0x0ff7, 0xffae, 0xffaf, 0xffb0, 0xffb1, 0xffb2, 0xffb3, 0xffb4, 0xffb5},
    {0x0000, 0x01f8, 0x7fc0, 0xffb6, 0xffb7, 0xffb8, 0xffb9, 0xffba, 0xffbb, 0xffbc, 0xffbd},
    {0x0000, 0x01f9, 0xffbe, 0xffbf, 0xffc0, 0xffc1, 0xffc2, 0xffc3, 0xffc4, 0xffc5, 0xffc6},
    {0x0000, 0x01fa, 0xffc7, 0xffc8, 0xffc9, 0xffca, 0xffcb, 0xffcc, 0xffcd, 0xffce, 0xffcf},
    {0x0000, 0x03f9, 0xffd0, 0xffd1, 0xffd2, 0xffd3, 0xffd4, 0xffd5, 0xffd6, 0xffd7, 0xffd8},
    {0x0000, 0x03fa, 0xffd9, 0xffda, 0xffdb, 0xffdc, 0xffdd, 0xffde, 0xffdf, 0xffe0, 0xffe1},
    {0x0000, 0x07f8, 0xffe2, 0xffe3, 0xffe4, 0xffe5, 0xffe6, 0xffe7, 0xffe8, 0xffe9, 0xffea},
    {0x0000, 0xffeb, 0xffec, 0xffed, 0xffee, 0xffef, 0xfff0, 0xfff1, 0xfff2, 0xfff3, 0xfff4},
    {0x07f9, 0xfff5, 0xfff6, 0xfff7, 0xfff8, 0xfff9, 0xfffa, 0xfffb, 0xfffc, 0xfffd, 0xfffe}};

const uint8_t AC_HUFF_TABLE_CODELEN[16][11] = {
    {4, 2, 2, 3, 4, 5, 7, 8, 10, 16, 16},        {0, 4, 5, 7, 9, 11, 16, 16, 16, 16, 16},
    {0, 5, 8, 10, 12, 16, 16, 16, 16, 16, 16},   {0, 6, 9, 12, 16, 16, 16, 16, 16, 16, 16},
    {0, 6, 10, 16, 16, 16, 16, 16, 16, 16, 16},  {0, 7, 11, 16, 16, 16, 16, 16, 16, 16, 16},
    {0, 7, 12, 16, 16, 16, 16, 16, 16, 16, 16},  {0, 8, 12, 16, 16, 16, 16, 16, 16, 16, 16},
    {0, 9, 15, 16, 16, 16, 16, 16, 16, 16, 16},  {0, 9, 16, 16, 16, 16, 16, 16, 16, 16, 16},
    {0, 9, 16, 16, 16, 16, 16, 16, 16, 16, 16},  {0, 10, 16, 16, 16, 16, 16, 16, 16, 16, 16},
    {0, 10, 16, 16, 16, 16, 16, 16, 16, 16, 16}, {0, 11, 16, 16, 16, 16, 16, 16, 16, 16, 16},
    {0, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16}, {11, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16}};

const uint8_t QUANT[64] = {16, 11, 10, 16, 24,  40,  51,  61,  12, 12, 14, 19, 26,  58,  60,  55,
                           14, 13, 16, 24, 40,  57,  69,  56,  14, 17, 22, 29, 51,  87,  80,  62,
                           18, 22, 37, 56, 68,  109, 103, 77,  24, 35, 55, 64, 81,  104, 113, 92,
                           49, 64, 78, 87, 103, 121, 120, 101, 72, 92, 95, 98, 112, 100, 103, 99};

const uint8_t ZIGZAG[64] = {0,  1,  8,  16, 9,  2,  3,  10, 17, 24, 32, 25, 18, 11, 4,  5,  12, 19, 26, 33, 40, 48,
                            41, 34, 27, 20, 13, 6,  7,  14, 21, 28, 35, 42, 49, 56, 57, 50, 43, 36, 29, 22, 15, 23,
                            30, 37, 44, 51, 58, 59, 52, 45, 38, 31, 39, 46, 53, 60, 61, 54, 47, 55, 62, 63};

void IMG_fdct(int8_t *src, int16_t *dest) {
    int col;
    int row;
    signed int tmp0, tmp1, tmp2, tmp3, tmp4, tmp5, tmp6, tmp7, tmp10, tmp11, tmp12, tmp13;
    signed int z1, z2, z3, z4, z5, z11, z13;
    int8_t *s = src;
    int16_t *d = dest;
    // do rows first
    for (row = 0; row < 64; row += 8, s += 8, d += 8) {
        tmp0 = s[0] + s[7];
        tmp7 = s[0] - s[7];
        tmp1 = s[1] + s[6];
        tmp6 = s[1] - s[6];
        tmp2 = s[2] + s[5];
        tmp5 = s[2] - s[5];
        tmp3 = s[3] + s[4];
        tmp4 = s[3] - s[4];
        // even part
        tmp10 = tmp0 + tmp3;
        tmp13 = tmp0 - tmp3;
        tmp11 = tmp1 + tmp2;
        tmp12 = tmp1 - tmp2;
        d[0] = (int16_t)(tmp10 + tmp11);
        d[4] = (int16_t)(tmp10 - tmp11);
        z1 = (((tmp12 + tmp13) * 181) >> 8);  // 181 >> 8 = 0.7071
        d[2] = (int16_t)(tmp13 + z1);
        d[6] = (int16_t)(tmp13 - z1);
        // odd part
        tmp10 = tmp4 + tmp5;
        tmp11 = tmp5 + tmp6;
        tmp12 = tmp6 + tmp7;
        z5 = ((tmp10 - tmp12) * 98);     // 98 >> 8 = 0.3826
        z2 = ((z5 + tmp10 * 139) >> 8);  // 139 >> 8 = 0.541196
        z4 = ((z5 + tmp12 * 334) >> 8);  // 334 >> 8 = 1.3065
        z3 = ((tmp11 * 181) >> 8);
        z11 = tmp7 + z3;
        z13 = tmp7 - z3;
        d[5] = (int16_t)(z13 + z2);
        d[3] = (int16_t)(z13 - z2);
        d[1] = (int16_t)(z11 + z4);
        d[7] = (int16_t)(z11 - z4);
    }  // for each row
    // now do the columns
    d = dest;
    for (col = 0; col < 8; col++, d++) {
        tmp0 = d[0 * 8] + d[7 * 8];
        tmp7 = d[0 * 8] - d[7 * 8];
        tmp1 = d[1 * 8] + d[6 * 8];
        tmp6 = d[1 * 8] - d[6 * 8];
        tmp2 = d[2 * 8] + d[5 * 8];
        tmp5 = d[2 * 8] - d[5 * 8];
        tmp3 = d[3 * 8] + d[4 * 8];
        tmp4 = d[3 * 8] - d[4 * 8];
        // even part
        tmp10 = tmp0 + tmp3;
        tmp13 = tmp0 - tmp3;
        tmp11 = tmp1 + tmp2;
        tmp12 = tmp1 - tmp2;
        d[0] = (int16_t)(tmp10 + tmp11);
        d[4 * 8] = (int16_t)(tmp10 - tmp11);
        z1 = (((tmp12 + tmp13) * 181) >> 8);
        d[2 * 8] = (int16_t)(tmp13 + z1);
        d[6 * 8] = (int16_t)(tmp13 - z1);
        // odd part
        tmp10 = tmp4 + tmp5;
        tmp11 = tmp5 + tmp6;
        tmp12 = tmp6 + tmp7;
        z5 = ((tmp10 - tmp12) * 98);
        z2 = ((z5 + tmp10 * 139) >> 8);
        z4 = ((z5 + tmp12 * 334) >> 8);
        z3 = (tmp11 * 181) >> 8;
        z11 = tmp7 + z3;
        z13 = tmp7 - z3;
        d[5 * 8] = (int16_t)(z13 + z2);
        d[3 * 8] = (int16_t)(z13 - z2);
        d[1 * 8] = (int16_t)(z11 + z4);
        d[7 * 8] = (int16_t)(z11 - z4);
    }  // for each column
}

static inline void IMG_dcEncodeHuffman(BitWriter *writer, FIFO *fifo, int32_t data) {
    uint32_t value = data > 0 ? data : -data;
    int bits = data != 0 ? 32 - __builtin_clz(value) : 0;
    BB_emitBits(writer, fifo, DC_HUFF_TABLE[bits], DC_HUFF_TABLE_CODELEN[bits]);
    if (data == 0) {
        return;
    }
    if (data < 0) {
        BB_emitBits(writer, fifo, ~value, bits);
    } else {
        BB_emitBits(writer, fifo, value, bits);
    }
}

static inline void IMG_acEncodeHuffman(BitWriter *writer, FIFO *fifo, int runlength, int32_t data) {
    uint32_t value = data > 0 ? data : -data;
    int bits = data != 0 ? 32 - __builtin_clz(value) : 0;
    uint32_t category = AC_HUFF_TABLE[runlength][bits];
    uint8_t codeLen = AC_HUFF_TABLE_CODELEN[runlength][bits];
    BB_emitBits(writer, fifo, category, codeLen);
    if (data == 0) {
        return;
    }
    if (data < 0) {
        BB_emitBits(writer, fifo, ~value, bits);
    } else {
        BB_emitBits(writer, fifo, value, bits);
    }
}

void IMG_init(Image *img, int width, int height) {
    img->width = width;
    img->height = height;
    img->prevDC = 0;
    img->bitWriter.putBits = 0;
    img->bitWriter.putBuffer = 0;
    for (int i = 0; i < 64; i++) {
        img->scaledQuant[i] = 65536 / QUANT[i];
    }
}

void IMG_encodeHeader(Image *img, FIFO *fifo) {
    uint32_t quality = 50;
    uint32_t flag = (uint32_t)1 << 30;
    uint32_t height = img->height;
    uint32_t width = img->width;
    FIFO_copyIn(fifo, (uint8_t *)&height, 4);
    FIFO_copyIn(fifo, (uint8_t *)&width, 4);
    FIFO_copyIn(fifo, (uint8_t *)&quality, 4);
    FIFO_copyIn(fifo, (uint8_t *)&flag, 4);
}

void IMG_quantize(Image *img, int16_t block[64]) {
    int d, q;
    for (int i = 0; i < 64; i++) {
        d = block[i];
        q = QUANT[i] >> 1;
        if (d < 0) {
            block[i] = (int16_t)(-(((q - d) * img->scaledQuant[i]) >> 19));
        } else {
            block[i] = (int16_t)(((q + d) * img->scaledQuant[i]) >> 19);
        }
    }
}

void IMG_encodeBlock(Image *img, const uint8_t data[64], FIFO *fifo) {
    int8_t block[64];
    int16_t coeffs[64];
    int32_t dc, ac, value;
    int zeroCnt = 0, runlength = 0, end;
    for (int i = 0; i < 64; i++) {
        block[i] = (int8_t)(data[i] ^ 0x80);
    }
    IMG_fdct(block, coeffs);
    IMG_quantize(img, coeffs);
    dc = coeffs[0];
    // write DC
    IMG_dcEncodeHuffman(&img->bitWriter, fifo, dc - img->prevDC);
    img->prevDC = dc;
    for (end = 63; end >= 0; end--) {
        if (coeffs[ZIGZAG[end]] != 0) {
            break;
        }
    }
    for (int i = 1; i <= end; i++) {
        ac = coeffs[ZIGZAG[i]];

        if (ac == 0) {
            zeroCnt++;
            if (zeroCnt >= 16) {
                runlength = 15;
                value = 0;
                zeroCnt = 0;
            }
        } else {
            runlength = zeroCnt;
            value = ac;
            zeroCnt = 0;
        }

        if (zeroCnt == 0) {
            // write AC
            IMG_acEncodeHuffman(&img->bitWriter, fifo, runlength, value);
        }
    }
    // write EOB
    IMG_acEncodeHuffman(&img->bitWriter, fifo, 0, 0);
}

void IMG_encodeComplete(Image *img, FIFO *fifo) {
    BB_flushBits(&img->bitWriter, fifo);
}
