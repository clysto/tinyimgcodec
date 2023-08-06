#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#include "img.h"

#define BUFSIZE 512

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
    FILE *fp = fopen(argv[3], "rb");
    size_t size;
    while (!feof(fp)) {
        uint8_t buf[BUFSIZE];
        size = fread(buf, 1, BUFSIZE, fp);
        IMG_push(img, buf, size);
    }
    IMG_complete(img);
    fclose(fp);
    fp = fopen(argv[4], "wb");
    fwrite(img->out, 1, img->outSize, fp);
    fclose(fp);
    IMG_destroy(img);
    return 0;
}
