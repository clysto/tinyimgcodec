#include "fifo.h"

FIFO *FIFO_new(unsigned size) {
    assert((size & (size - 1)) == 0);
    FIFO *fifo = (FIFO *)malloc(sizeof(FIFO));
    fifo->front = 0;
    fifo->rear = 0;
    fifo->mask = size - 1;
    fifo->buf = (uint8_t *)malloc(size);
    return fifo;
}

void FIFO_init(FIFO *fifo, uint8_t *buf, unsigned size) {
    assert((size & (size - 1)) == 0);
    fifo->front = 0;
    fifo->rear = 0;
    fifo->mask = size - 1;
    fifo->buf = buf;
}

void FIFO_free(FIFO *fifo) {
    free(fifo->buf);
    free(fifo);
}

void FIFO_copyOut(FIFO *fifo, uint8_t *dst, unsigned len) {
    unsigned off = fifo->rear & fifo->mask;
    unsigned l = fifo->mask + 1 - off;
    l = l > len ? len : l;
    memcpy(dst, fifo->buf + off, l);
    memcpy(dst + l, fifo->buf, len - l);
    fifo->rear += len;
}

void FIFO_copyIn(FIFO *fifo, uint8_t *src, unsigned len) {
    unsigned off = fifo->front & fifo->mask;
    unsigned l = fifo->mask + 1 - off;
    l = l > len ? len : l;
    memcpy(fifo->buf + off, src, l);
    memcpy(fifo->buf, src + l, len - l);
    fifo->front += len;
}

void FIFO_pipeOut(FIFO *fifo, FILE *fp, unsigned len) {
    len = len > FIFO_size(fifo) ? FIFO_size(fifo) : len;
    unsigned off = fifo->rear & fifo->mask;
    unsigned l = fifo->mask + 1 - off;
    l = l > len ? len : l;
    fwrite(fifo->buf + off, 1, l, fp);
    fwrite(fifo->buf, 1, len - l, fp);
    fifo->rear += len;
}

void FIFO_pipeIn(FIFO *fifo, FILE *fp, unsigned len) {
    unsigned n;
    unsigned off = fifo->front & fifo->mask;
    unsigned l = fifo->mask + 1 - off;
    l = l > len ? len : l;
    if ((n = fread(fifo->buf + off, 1, l, fp)) < l) {
        fifo->front += n;
        return;
    }
    if ((n = fread(fifo->buf, 1, len - l, fp)) < len - l) {
        fifo->front += l + n;
        return;
    }
    fifo->front += len;
}