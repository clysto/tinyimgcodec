#include <stdio.h>
#include <stdlib.h>

#include "fifo.h"
#include "img.h"

void process(FIFO *fifo, char *base, int frameSize) {
    static int frameIndex = 0;
    char filename[32];
    FILE *fp;
    while (FIFO_size(fifo) >= frameSize) {
        sprintf(filename, "%s_%d.img", base, frameIndex++);
        fp = fopen(filename, "wb");
        FIFO_pipeOut(fifo, fp, frameSize);
        fclose(fp);
    }
}

void process2(FIFO *fifo, FILE *fp, int frameSize) {
    while (FIFO_size(fifo) >= frameSize) {
        FIFO_pipeOut(fifo, fp, frameSize);
    }
}

int main(int argc, char **argv) {
    if (argc != 5) {
        printf("Usage: encode [width] [height] [input] [output]\n");
        return 1;
    }
    int width = (int)strtol(argv[1], NULL, 10);
    int height = (int)strtol(argv[2], NULL, 10);
    if (width % 8 != 0 || height % 8 != 0) {
        printf("Width and height must be multiples of 8\n");
        return 1;
    }
    Image img;
    IMG_init(&img, width, height);
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
        process2(fifo, out, 1024);
    }
    IMG_encodeComplete(&img, fifo);
    process2(fifo, out, FIFO_size(fifo));
    fclose(out);
    FIFO_free(fifo);
    fclose(in);
    return 0;
}
