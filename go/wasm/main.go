package main

import (
	"bytes"
	"syscall/js"
	"tinyimgcodec/tinyimgcodec"
)

func imgDecompress(this js.Value, p []js.Value) interface{} {
	l := p[0].Get("length").Int()
	src := make([]byte, l)
	js.CopyBytesToGo(src, p[0])
	buf := bytes.NewBuffer(src)
	dst, info := tinyimgcodec.Decompress(buf)
	ret := js.Global().Get("Uint8Array").New(len(dst))
	js.CopyBytesToJS(ret, dst)
	return map[string]interface{}{
		"data":   ret,
		"width":  info.Width,
		"height": info.Height,
	}
}

func main() {
	c := make(chan bool)
	js.Global().Set("imgDecompress", js.FuncOf(imgDecompress))
	<-c
}
