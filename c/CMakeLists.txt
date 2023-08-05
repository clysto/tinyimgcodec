cmake_minimum_required(VERSION 3.25)
project(encode C)

set(CMAKE_C_STANDARD 11)

include_directories(.)

add_executable(encode
        bitbuf.c
        bitbuf.h
        encode.c
        img.c
        img.h)
