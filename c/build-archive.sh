#!/bin/bash

tar czf tinyimgcodec.tar.gz img.c img.h fifo.c fifo.h
echo "sed '1,/^#EOF#$/d' \"\$0\" | tar zx; exit 0" > tinyimgcodec.sh
echo "#EOF#" >> tinyimgcodec.sh
cat tinyimgcodec.tar.gz >> tinyimgcodec.sh
rm tinyimgcodec.tar.gz
