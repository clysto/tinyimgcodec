#include <stdio.h>
#include <stdlib.h>

#include "fifo.h"
#include "img.h"

#define BUFSIZE 512

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
    Image *img = IMG_create(width, height);
    FILE *in = fopen(argv[3], "rb");
    FIFO *fifo = FIFO_new(1024 * 8);
    size_t size;
    IMG_compressStart(img, fifo);
    while (!feof(in)) {
        uint8_t buf[BUFSIZE];
        size = fread(buf, 1, BUFSIZE, in);
        IMG_compressPush(img, buf, size, fifo);
        // Split to frames, each frame contains 1024 bytes
        process(fifo, argv[4], 1024);
    }
    IMG_compressComplete(img, fifo);
    process(fifo, argv[4], FIFO_size(fifo));
    FIFO_free(fifo);
    IMG_destroy(img);
    fclose(in);
    return 0;
}
