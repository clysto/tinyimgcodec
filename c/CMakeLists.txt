cmake_minimum_required(VERSION 3.25)
project(encode C)

set(CMAKE_C_STANDARD 11)

include_directories(.)

add_executable(encode bitwriter.c bitwriter.h encode.c img.c img.h huff.c huff.h fifo.c fifo.h)
