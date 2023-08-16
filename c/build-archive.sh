#!/bin/bash

tar czf tinyimgcodec.tar.gz img.c img.h fifo.c fifo.h
echo -n "DATA=\"" > tinyimgcodec.sh
cat tinyimgcodec.tar.gz | base64 | tr -d '\n\r' >> tinyimgcodec.sh
echo "\"" >> tinyimgcodec.sh
echo "echo \"\$DATA\" | base64 --decode | tar zx" >> tinyimgcodec.sh
rm tinyimgcodec.tar.gz
