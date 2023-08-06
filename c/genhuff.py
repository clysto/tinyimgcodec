from tinyimgcodec import constants

print("#include <stdint.h>")

print("uint32_t DC_HUFF_TABLE[12] = {")
print(
    ",".join(
        "0x{:04x}".format(int(v, 2))
        for v in constants.HUFFMAN_CATEGORY_CODEWORD["DC"].values()
    )
)
print("};")

print("uint8_t DC_HUFF_TABLE_CODELEN[12] = {")
print(",".join(str(len(v)) for v in constants.HUFFMAN_CATEGORY_CODEWORD["DC"].values()))
print("};")

T1 = [["0x0000"] * 11 for _ in range(16)]
T2 = [[0] * 11 for _ in range(16)]
for k, v in constants.HUFFMAN_CATEGORY_CODEWORD["AC"].items():
    T1[k[0]][k[1]] = "0x{:04x}".format(int(v, 2))
    T2[k[0]][k[1]] = len(v)


print("uint32_t AC_HUFF_TABLE[16][11] = {")
for i in range(16):
    print("{")
    for j in range(11):
        print(T1[i][j])
        if j != 10:
            print(",")
    print("}")
    if i != 15:
        print(",")
print("};")

print("uint8_t AC_HUFF_TABLE_CODELEN[16][11] = {")
for i in range(16):
    print("{")
    for j in range(11):
        print(str(T2[i][j]))
        if j != 10:
            print(",")
    print("}")
    if i != 15:
        print(",")
print("};")
