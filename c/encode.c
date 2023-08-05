#include <stdio.h>

#include "img.h"

int main() {
    Image *img = IMG_create(512, 512);
    FILE *fp = fopen("/Users/maoyachen/Code/tinyimgcodec/c/lenna.dat", "rb");
    while (!feof(fp)) {
        uint8_t buf[1024];
        int size = fread(buf, 1, 100, fp);
        IMG_push(img, buf, size);
    }
    fclose(fp);
    fp = fopen("/Users/maoyachen/Code/tinyimgcodec/c/lenna_dct.dat", "wb");
    fwrite(img->out, 1, img->outSize, fp);
    fclose(fp);
    IMG_destroy(img);
    return 0;
}
