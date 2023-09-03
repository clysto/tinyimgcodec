package main

import (
	"fmt"
	"os"
	"tinyimgcodec/tinyimgcodec"
)

func main() {
	img, info := tinyimgcodec.Decompress(os.Stdin)
	os.Stdout.WriteString(fmt.Sprintf("P5\n%d %d\n255\n", info.Width, info.Height))
	os.Stdout.Write(img)
}
