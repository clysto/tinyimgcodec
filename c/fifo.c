#include "fifo.h"

FIFO *FIFO_new(unsigned size) {
    assert((size & (size - 1)) == 0);
    FIFO *fifo = (FIFO *)malloc(sizeof(FIFO));
    fifo->front = 0;
    fifo->rear = 0;
    fifo->mask = size - 1;
    fifo->buff = (uint8_t *)malloc(size);
    return fifo;
}

void FIFO_free(FIFO *fifo) {
    free(fifo->buff);
    free(fifo);
}

void FIFO_copyOut(FIFO *fifo, uint8_t *dst, unsigned len) {
    unsigned off = fifo->rear & fifo->mask;
    unsigned l = fifo->mask + 1 - off;
    l = l > len ? len : l;
    memcpy(dst, fifo->buff + off, l);
    memcpy(dst + l, fifo->buff, len - l);
    fifo->rear += len;
}

void FIFO_copyIn(FIFO *fifo, uint8_t *src, unsigned len) {
    unsigned off = fifo->front & fifo->mask;
    unsigned l = fifo->mask + 1 - off;
    l = l > len ? len : l;
    memcpy(fifo->buff + off, src, l);
    memcpy(fifo->buff, src + l, len - l);
    fifo->front += len;
}

void FIFO_pipeOut(FIFO *fifo, FILE *fp, unsigned len) {
    len = len > FIFO_size(fifo) ? FIFO_size(fifo) : len;
    unsigned off = fifo->rear & fifo->mask;
    unsigned l = fifo->mask + 1 - off;
    l = l > len ? len : l;
    fwrite(fifo->buff + off, 1, l, fp);
    fwrite(fifo->buff, 1, len - l, fp);
    fifo->rear += len;
}

void FIFO_pipeIn(FIFO *fifo, FILE *fp, unsigned len) {
    unsigned n;
    unsigned off = fifo->front & fifo->mask;
    unsigned l = fifo->mask + 1 - off;
    l = l > len ? len : l;
    if ((n = fread(fifo->buff + off, 1, l, fp)) < l) {
        fifo->front += n;
        return;
    }
    if ((n = fread(fifo->buff, 1, len - l, fp)) < len - l) {
        fifo->front += l + n;
        return;
    }
    fifo->front += len;
}