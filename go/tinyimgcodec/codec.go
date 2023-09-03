package tinyimgcodec

import (
	"encoding/binary"
	"errors"
	"io"
	"math"
)

var ErrInvalidHuffmanCode = errors.New("invalid huffman code")

type ByteReader interface {
	ReadByte() (byte, error)
	Read(p []byte) (n int, err error)
}

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

func (bb *BitReader) Read(buf ByteReader, size int) (uint32, error) {
	for bb.PutBits < size {
		b, err := buf.ReadByte()
		if err != nil {
			return 0, err
		}
		if b == 0xff {
			b, err = buf.ReadByte()
			if err != nil {
				return 0, err
			}
			if b == 0x00 {
				b = 0xff
			} else {
				b, err = buf.ReadByte()
				if err != nil {
					return 0, err
				}
			}
		}
		bb.PutBuffer |= (uint32(b) << (24 - bb.PutBits))
		bb.PutBits += 8
	}
	ret := bb.PutBuffer >> (32 - size)
	bb.PutBits -= size
	bb.PutBuffer <<= size
	return ret, nil
}

func SyncRst(buf ByteReader) (int32, error) {
	var x uint8
	var y uint8
	var err error
	for !((x != 0) && (y == 0xff)) {
		y = x
		x, err = buf.ReadByte()
		if err != nil {
			return 0, err
		}
	}
	return int32(x) - 1, nil
}

func (bb *BitReader) ReadInt(buf ByteReader, size int) (int32, error) {
	if size == 0 {
		return 0, nil
	}
	value, err := bb.Read(buf, size)
	if err != nil {
		return 0, err
	}
	if value>>(size-1) == 0 {
		return -(int32(^value & ((1 << size) - 1))), nil
	}
	return int32(value), nil
}

func ReadHuffmanCode[T any](bb *BitReader, buf ByteReader, table map[[2]uint32]T) (T, error) {
	var code [2]uint32
	for {
		code[1]++
		b, err := bb.Read(buf, 1)
		if err != nil {
			var ret T
			return ret, err
		}
		code[0] = code[0]<<1 | b
		val, ok := table[code]
		if ok {
			return val, nil
		}
		if code[1] > 16 {
			return val, ErrInvalidHuffmanCode
		}
	}
}

func ParseHeader(buf ByteReader) ImageInfo {
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

func Decompress(buf ByteReader) ([]uint8, *ImageInfo) {
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
		category, err := ReadHuffmanCode[uint8](&bb, buf, DC_HUFF_TABLE_R)
		if errors.Is(err, io.EOF) {
			goto stop
		}
		dc, err := bb.ReadInt(buf, int(category))
		if errors.Is(err, io.EOF) {
			goto stop
		}
		block[0] = dc + prevDC
		prevDC = block[0]
		var j uint
		for j < 64 {
			j++
			symbol, err := ReadHuffmanCode[[2]uint8](&bb, buf, AC_HUFF_TABLE_R)
			if errors.Is(err, io.EOF) {
				goto stop
			}
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
			block[ZIGZAG[j]], _ = bb.ReadInt(buf, int(category))
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
