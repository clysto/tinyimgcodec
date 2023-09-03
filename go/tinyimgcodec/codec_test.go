package tinyimgcodec

import (
	"bytes"
	"os"
	"testing"
)

func BenchmarkDecompressc(b *testing.B) {
	data, _ := os.ReadFile("/Users/maoyachen/Code/tinyimgcodec/1.img")
	buf := bytes.NewReader(data)
	Decompress(buf)
}
