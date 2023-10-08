package main

import (
	"bufio"
	"fmt"
	"os"
	"tinyimgcodec/tinyimgcodec"
)

func main() {
	buf := bufio.NewReader(os.Stdin)
	img, info := tinyimgcodec.Decompress(buf)
	os.Stdout.WriteString(fmt.Sprintf("P5\n%d %d\n255\n", info.Width, info.Height))
	os.Stdout.Write(img)
}
