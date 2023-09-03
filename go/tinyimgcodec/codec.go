package tinyimgcodec

import (
	"encoding/binary"
	"errors"
	"io"
	"math"
)

type BitReader struct {
	PutBuffer uint32
	PutBits   int
}

type ImageInfo struct {
	Height  uint32
	Width   uint32
	Quality uint32
	Flag    uint32
}

func (bb *BitReader) FlushBits() {
	for bb.PutBits&7 != 0 {
		bb.PutBits--
		bb.PutBuffer <<= 1
	}
}

func (bb *BitReader) Read(buf io.Reader, size int) uint32 {
	x := make([]byte, 1)
	for bb.PutBits < size {
		buf.Read(x)
		if x[0] == 0xff {
			buf.Read(x)
			if x[0] == 0x00 {
				x[0] = 0xff
			} else {
				buf.Read(x)
			}
		}
		bb.PutBuffer |= (uint32(x[0]) << (24 - bb.PutBits))
		bb.PutBits += 8
	}
	ret := bb.PutBuffer >> (32 - size)
	bb.PutBits -= size
	bb.PutBuffer <<= size
	return ret
}

func SyncRst(buf io.Reader) (int32, error) {
	b := make([]uint8, 1)
	var y uint8
	for !((b[0] != 0) && (y == 0xff)) {
		y = b[0]
		_, err := buf.Read(b)
		if err != nil {
			return 0, err
		}
	}
	return int32(b[0]) - 1, nil
}

func (bb *BitReader) ReadInt(buf io.Reader, size int) int32 {
	if size == 0 {
		return 0
	}
	value := bb.Read(buf, size)
	if value>>(size-1) == 0 {
		return -(int32(^value & ((1 << size) - 1)))
	}
	return int32(value)
}

func ReadHuffmanCode[T any](bb *BitReader, buf io.Reader, table map[[2]uint32]T) (T, error) {
	var code [2]uint32
	for {
		code[1]++
		code[0] = code[0]<<1 | bb.Read(buf, 1)
		val, ok := table[code]
		if ok {
			return val, nil
		}
		if code[1] > 16 {
			return val, errors.New("invalid huffman code")
		}
	}
}

func ParseHeader(buf io.Reader) ImageInfo {
	var info ImageInfo
	header := make([]byte, 16)
	buf.Read(header)
	info.Height = binary.LittleEndian.Uint32(header[0:4])
	info.Width = binary.LittleEndian.Uint32(header[4:8])
	info.Quality = binary.LittleEndian.Uint32(header[8:12])
	info.Flag = binary.LittleEndian.Uint32(header[12:16])
	return info
}

func Quantize(coeffs *[64]int32, quality int32, table []float64) {
	for i := 0; i < 64; i++ {
		coeffs[i] = int32(math.Round(float64(coeffs[i]) * table[i]))
	}
}

func CalcQuantTable(quality int32, flag uint32) []float64 {
	table := make([]float64, 64)
	if flag == 1<<30 {
		for i := 0; i < 64; i++ {
			table[i] = float64(uint32(QUANT[i])<<11<<quality) / float64(ANNSCALES[i])
		}
	} else {
		var factor float64
		if quality < 50 {
			factor = 5000 / float64(quality)
		} else {
			factor = 200 - 2*float64(quality)
		}
		for i := 0; i < 64; i++ {
			table[i] = float64(QUANT[i]) * factor / 100
		}
	}
	return table
}

func Decompress(buf io.Reader) ([]uint8, *ImageInfo) {
	var bb BitReader
	var blockIndex uint32
	var prevDC int32
	var prevRstIndex int32 = -1
	info := ParseHeader(buf)

	if info.Width > 4096 {
		info.Width = 4096
	}

	if info.Height > 4096 {
		info.Height = 4096
	}

	quantTable := CalcQuantTable(int32(info.Quality), info.Flag)
	img := make([]uint8, info.Height*info.Width)
	blockCount := (info.Height / 8) * (info.Width / 8)
	blocksPerLine := info.Width / 8

	for blockIndex < blockCount {
		var block [64]int32
		category, _ := ReadHuffmanCode[uint8](&bb, buf, DC_HUFF_TABLE_R)
		block[0] = bb.ReadInt(buf, int(category)) + prevDC
		prevDC = block[0]
		var j uint
		for j < 64 {
			j++
			symbol, _ := ReadHuffmanCode[[2]uint8](&bb, buf, AC_HUFF_TABLE_R)
			runlength := symbol[0]
			category = symbol[1]
			// meet EOB Marker
			if runlength == 0 && category == 0 {
				break
			}
			j += uint(runlength)
			if j > 63 {
				bb.ReadInt(buf, int(category))
				break
			}
			block[ZIGZAG[j]] = bb.ReadInt(buf, int(category))
		}
		bb.FlushBits()

		Quantize(&block, int32(info.Quality), quantTable)
		IDCT(&block)

		col := (blockIndex % blocksPerLine) * 8
		row := (blockIndex / blocksPerLine) * 8
		index := 0

		for x := row; x < row+8; x++ {
			for y := col; y < col+8; y++ {
				pixel := block[index] + 128
				if pixel < 0 {
					pixel = 0
				}
				if pixel > 255 {
					pixel = 255
				}
				if int(x*info.Width+y) >= len(img) {
					goto stop
				}
				img[x*info.Width+y] = uint8(pixel)
				index++
			}
		}

		if blockIndex&3 == 3 {
			prevDC = 0
			rstIndex, err := SyncRst(buf)
			if err != nil || rstIndex > 253 {
				blockIndex += 1
				continue
			}
			if rstIndex < prevRstIndex {
				rstIndex += 254
			}
			if (rstIndex - prevRstIndex) > 10 {
				continue
			}
			blockIndex += uint32((rstIndex - prevRstIndex - 1) * 4)
			prevRstIndex = rstIndex % 254
		}
		blockIndex++
	}
stop:
	return img, &info
}
