package main

var DC_HUFF_TABLE_R = map[[2]uint32]uint8{
	{0x0000, 2}: 0,
	{0x0002, 3}: 1,
	{0x0003, 3}: 2,
	{0x0004, 3}: 3,
	{0x0005, 3}: 4,
	{0x0006, 3}: 5,
	{0x000e, 4}: 6,
	{0x001e, 5}: 7,
	{0x003e, 6}: 8,
	{0x007e, 7}: 9,
	{0x00fe, 8}: 10,
	{0x01fe, 9}: 11,
}

var AC_HUFF_TABLE_R = map[[2]uint32][2]uint8{
	{0x000a, 4}: {0, 0}, {0x07f9, 11}: {15, 0}, {0x0000, 2}: {0, 1}, {0x0001, 2}: {0, 2},
	{0x0004, 3}: {0, 3}, {0x000b, 4}: {0, 4}, {0x001a, 5}: {0, 5}, {0x0078, 7}: {0, 6},
	{0x00f8, 8}: {0, 7}, {0x03f6, 10}: {0, 8}, {0xff82, 16}: {0, 9}, {0xff83, 16}: {0, 10},
	{0x000c, 4}: {1, 1}, {0x001b, 5}: {1, 2}, {0x0079, 7}: {1, 3}, {0x01f6, 9}: {1, 4},
	{0x07f6, 11}: {1, 5}, {0xff84, 16}: {1, 6}, {0xff85, 16}: {1, 7}, {0xff86, 16}: {1, 8},
	{0xff87, 16}: {1, 9}, {0xff88, 16}: {1, 10}, {0x001c, 5}: {2, 1}, {0x00f9, 8}: {2, 2},
	{0x03f7, 10}: {2, 3}, {0x0ff4, 12}: {2, 4}, {0xff89, 16}: {2, 5}, {0xff8a, 16}: {2, 6},
	{0xff8b, 16}: {2, 7}, {0xff8c, 16}: {2, 8}, {0xff8d, 16}: {2, 9}, {0xff8e, 16}: {2, 10},
	{0x003a, 6}: {3, 1}, {0x01f7, 9}: {3, 2}, {0x0ff5, 12}: {3, 3}, {0xff8f, 16}: {3, 4},
	{0xff90, 16}: {3, 5}, {0xff91, 16}: {3, 6}, {0xff92, 16}: {3, 7}, {0xff93, 16}: {3, 8},
	{0xff94, 16}: {3, 9}, {0xff95, 16}: {3, 10}, {0x003b, 6}: {4, 1}, {0x03f8, 10}: {4, 2},
	{0xff96, 16}: {4, 3}, {0xff97, 16}: {4, 4}, {0xff98, 16}: {4, 5}, {0xff99, 16}: {4, 6},
	{0xff9a, 16}: {4, 7}, {0xff9b, 16}: {4, 8}, {0xff9c, 16}: {4, 9}, {0xff9d, 16}: {4, 10},
	{0x007a, 7}: {5, 1}, {0x07f7, 11}: {5, 2}, {0xff9e, 16}: {5, 3}, {0xff9f, 16}: {5, 4},
	{0xffa0, 16}: {5, 5}, {0xffa1, 16}: {5, 6}, {0xffa2, 16}: {5, 7}, {0xffa3, 16}: {5, 8},
	{0xffa4, 16}: {5, 9}, {0xffa5, 16}: {5, 10}, {0x007b, 7}: {6, 1}, {0x0ff6, 12}: {6, 2},
	{0xffa6, 16}: {6, 3}, {0xffa7, 16}: {6, 4}, {0xffa8, 16}: {6, 5}, {0xffa9, 16}: {6, 6},
	{0xffaa, 16}: {6, 7}, {0xffab, 16}: {6, 8}, {0xffac, 16}: {6, 9}, {0xffad, 16}: {6, 10},
	{0x00fa, 8}: {7, 1}, {0x0ff7, 12}: {7, 2}, {0xffae, 16}: {7, 3}, {0xffaf, 16}: {7, 4},
	{0xffb0, 16}: {7, 5}, {0xffb1, 16}: {7, 6}, {0xffb2, 16}: {7, 7}, {0xffb3, 16}: {7, 8},
	{0xffb4, 16}: {7, 9}, {0xffb5, 16}: {7, 10}, {0x01f8, 9}: {8, 1}, {0x7fc0, 15}: {8, 2},
	{0xffb6, 16}: {8, 3}, {0xffb7, 16}: {8, 4}, {0xffb8, 16}: {8, 5}, {0xffb9, 16}: {8, 6},
	{0xffba, 16}: {8, 7}, {0xffbb, 16}: {8, 8}, {0xffbc, 16}: {8, 9}, {0xffbd, 16}: {8, 10},
	{0x01f9, 9}: {9, 1}, {0xffbe, 16}: {9, 2}, {0xffbf, 16}: {9, 3}, {0xffc0, 16}: {9, 4},
	{0xffc1, 16}: {9, 5}, {0xffc2, 16}: {9, 6}, {0xffc3, 16}: {9, 7}, {0xffc4, 16}: {9, 8},
	{0xffc5, 16}: {9, 9}, {0xffc6, 16}: {9, 10}, {0x01fa, 9}: {10, 1}, {0xffc7, 16}: {10, 2},
	{0xffc8, 16}: {10, 3}, {0xffc9, 16}: {10, 4}, {0xffca, 16}: {10, 5}, {0xffcb, 16}: {10, 6},
	{0xffcc, 16}: {10, 7}, {0xffcd, 16}: {10, 8}, {0xffce, 16}: {10, 9}, {0xffcf, 16}: {10, 10},
	{0x03f9, 10}: {11, 1}, {0xffd0, 16}: {11, 2}, {0xffd1, 16}: {11, 3}, {0xffd2, 16}: {11, 4},
	{0xffd3, 16}: {11, 5}, {0xffd4, 16}: {11, 6}, {0xffd5, 16}: {11, 7}, {0xffd6, 16}: {11, 8},
	{0xffd7, 16}: {11, 9}, {0xffd8, 16}: {11, 10}, {0x03fa, 10}: {12, 1}, {0xffd9, 16}: {12, 2},
	{0xffda, 16}: {12, 3}, {0xffdb, 16}: {12, 4}, {0xffdc, 16}: {12, 5}, {0xffdd, 16}: {12, 6},
	{0xffde, 16}: {12, 7}, {0xffdf, 16}: {12, 8}, {0xffe0, 16}: {12, 9}, {0xffe1, 16}: {12, 10},
	{0x07f8, 11}: {13, 1}, {0xffe2, 16}: {13, 2}, {0xffe3, 16}: {13, 3}, {0xffe4, 16}: {13, 4},
	{0xffe5, 16}: {13, 5}, {0xffe6, 16}: {13, 6}, {0xffe7, 16}: {13, 7}, {0xffe8, 16}: {13, 8},
	{0xffe9, 16}: {13, 9}, {0xffea, 16}: {13, 10}, {0xffeb, 16}: {14, 1}, {0xffec, 16}: {14, 2},
	{0xffed, 16}: {14, 3}, {0xffee, 16}: {14, 4}, {0xffef, 16}: {14, 5}, {0xfff0, 16}: {14, 6},
	{0xfff1, 16}: {14, 7}, {0xfff2, 16}: {14, 8}, {0xfff3, 16}: {14, 9}, {0xfff4, 16}: {14, 10},
	{0xfff5, 16}: {15, 1}, {0xfff6, 16}: {15, 2}, {0xfff7, 16}: {15, 3}, {0xfff8, 16}: {15, 4},
	{0xfff9, 16}: {15, 5}, {0xfffa, 16}: {15, 6}, {0xfffb, 16}: {15, 7}, {0xfffc, 16}: {15, 8},
	{0xfffd, 16}: {15, 9}, {0xfffe, 16}: {15, 10},
}

var QUANT = [64]uint8{16, 11, 10, 16, 24, 40, 51, 61, 12, 12, 14, 19, 26, 58, 60, 55,
	14, 13, 16, 24, 40, 57, 69, 56, 14, 17, 22, 29, 51, 87, 80, 62,
	18, 22, 37, 56, 68, 109, 103, 77, 24, 35, 55, 64, 81, 104, 113, 92,
	49, 64, 78, 87, 103, 121, 120, 101, 72, 92, 95, 98, 112, 100, 103, 99}

var ZIGZAG = [64]uint8{0, 1, 8, 16, 9, 2, 3, 10, 17, 24, 32, 25, 18, 11, 4, 5, 12, 19, 26, 33, 40, 48,
	41, 34, 27, 20, 13, 6, 7, 14, 21, 28, 35, 42, 49, 56, 57, 50, 43, 36, 29, 22, 15, 23,
	30, 37, 44, 51, 58, 59, 52, 45, 38, 31, 39, 46, 53, 60, 61, 54, 47, 55, 62, 63}

var ANNSCALES = [64]int32{
	16384, 22725, 21407, 19266, 16384, 12873, 8867, 4520,
	22725, 31521, 29692, 26722, 22725, 17855, 12299, 6270,
	21407, 29692, 27969, 25172, 21407, 16819, 11585, 5906,
	19266, 26722, 25172, 22654, 19266, 15137, 10426, 5315,
	16384, 22725, 21407, 19266, 16384, 12873, 8867, 4520,
	12873, 17855, 16819, 15137, 12873, 10114, 6967, 3552,
	8867, 12299, 11585, 10426, 8867, 6967, 4799, 2446,
	4520, 6270, 5906, 5315, 4520, 3552, 2446, 1247,
}