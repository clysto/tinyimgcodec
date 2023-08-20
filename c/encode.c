#include <stdio.h>
#include <stdlib.h>

#include "fifo.h"
#include "img.h"

void write_all(FIFO *fifo, FILE *fp, int frameSize) {
    while (FIFO_size(fifo) >= frameSize) {
        FIFO_pipeOut(fifo, fp, frameSize);
    }
}

int main(int argc, char **argv) {
    uint8_t qfactor;
    if (argc < 5) {
        printf("Usage: encode <width> <height> <input> <output> [qfactor]\n");
        return 1;
    }
    if (argc == 6) {
        if (strcmp(argv[5], "best") == 0) {
            qfactor = IMG_Q_BEST;
        } else if (strcmp(argv[5], "high") == 0) {
            qfactor = IMG_Q_HIGH;
        } else if (strcmp(argv[5], "med") == 0) {
            qfactor = IMG_Q_MED;
        } else if (strcmp(argv[5], "low") == 0) {
            qfactor = IMG_Q_LOW;
        } else {
            printf("Invalid quality factor\n");
            return 1;
        }
    } else {
        qfactor = IMG_Q_MED;
    }
    int width = (int)strtol(argv[1], NULL, 10);
    int height = (int)strtol(argv[2], NULL, 10);
    if (width % 8 != 0 || height % 8 != 0) {
        printf("Width and height must be multiples of 8\n");
        return 1;
    }
    Image img;
    IMG_init(&img, width, height, qfactor);
    FILE *in = fopen(argv[3], "rb");
    FILE *out = fopen(argv[4], "wb");
    FIFO *fifo = FIFO_new(1024 * 8);
    IMG_encodeHeader(&img, fifo);
    while (!feof(in)) {
        uint8_t buf[width * 8];
        fread(buf, 1, width * 8, in);
        for (int k = 0; k < width / 8; k++) {
            uint8_t data[64];
            for (int i = 0; i < 8; i++) {
                for (int j = 0; j < 8; j++) {
                    data[i * 8 + j] = buf[i * width + j + k * 8];
                }
            }
            IMG_encodeBlock(&img, data, fifo);
        }
        write_all(fifo, out, 1024);
    }
    IMG_encodeComplete(&img, fifo);
    write_all(fifo, out, FIFO_size(fifo));
    fclose(out);
    FIFO_free(fifo);
    fclose(in);
    return 0;
}
