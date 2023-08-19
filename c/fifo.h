#ifndef FIFO_H
#define FIFO_H

#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define FIFO_writeByte(fifo, byte) (fifo)->buf[(fifo)->front++ & (fifo)->mask] = byte
#define FIFO_readByte(fifo)        (fifo)->buf[(fifo)->rear++ & (fifo)->mask]
#define FIFO_size(fifo)            ((fifo)->front - (fifo)->rear)

typedef struct {
    unsigned front;
    unsigned rear;
    unsigned mask;
    uint8_t *buf;
} FIFO;

void FIFO_init(FIFO *fifo, uint8_t *buf, unsigned size);
FIFO *FIFO_new(unsigned size);
void FIFO_free(FIFO *fifo);
void FIFO_copyOut(FIFO *fifo, uint8_t *dst, unsigned len);
void FIFO_copyIn(FIFO *fifo, uint8_t *src, unsigned len);
void FIFO_pipeOut(FIFO *fifo, FILE *fp, unsigned len);
void FIFO_pipeIn(FIFO *fifo, FILE *fp, unsigned len);

#endif
