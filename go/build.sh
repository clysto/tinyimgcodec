#!/usr/bin/env bash

OS=(windows darwin linux)
ARCH=(amd64)

for os in ${OS[@]}; do
    for arch in ${ARCH[@]}; do
        mkdir -p release/tinyimgcodec_${os}_${arch}
        output=release/tinyimgcodec_${os}_${arch}/tinyimgcodec
        if [[ "$os" == "windows" ]]; then
            output=$output.exe
        fi
        env GOOS=$os GOARCH=$arch go build -o $output tinyimgcodec/decoder
        (cd release && zip -r tinyimgcodec_${os}_${arch}.zip tinyimgcodec_${os}_${arch})
        rm -rf release/tinyimgcodec_${os}_${arch}
    done
done
