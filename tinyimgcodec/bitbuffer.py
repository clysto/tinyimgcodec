from bitarray import bitarray
from bitarray.util import ba2int, int2ba


class BitBuffer:
    def __init__(self):
        self.__bitarray: bitarray = bitarray(endian="big")
        self.__pos = 0

    @classmethod
    def from_bytes(cls, a: bytes):
        ret = cls()
        ret.__bitarray.frombytes(a)
        ret.__pos = 0
        return ret

    def to_bytes(self):
        return self.__bitarray.tobytes()

    def read(self, n: int):
        ret = self.__bitarray[self.__pos : self.__pos + n]
        self.__pos += n
        return ret.to01()

    def write(self, x):
        self.__bitarray.extend(x)
        self.__pos = len(self.__bitarray)

    def write_bytes(self, bytes):
        self.__bitarray.frombytes(bytes)
        self.__pos = len(self.__bitarray)

    def read_bytes(self, size):
        ret = self.__bitarray[self.__pos : self.__pos + size * 8].tobytes()
        self.__pos += size * 8
        return ret

    def write_uint(self, n, size):
        self.__bitarray.extend(int2ba(int(n), size))
        self.__pos = len(self.__bitarray)

    def read_uint(self, size):
        ret = ba2int(self.__bitarray[self.__pos : self.__pos + size])
        self.__pos += size
        return ret

    def write_int(self, n):
        if n == 0:
            return
        x = int2ba(int(abs(n)))
        if n < 0:
            x.invert()
        self.__bitarray.extend(x)
        self.__pos = len(self.__bitarray)

    def read_int(self, size):
        if size == 0:
            return 0
        ret = self.__bitarray[self.__pos : self.__pos + size]
        self.__pos += size
        if ret[0] == 0:
            ret.invert()
            ret = ba2int(ret) * -1
        else:
            ret = ba2int(ret)
        return ret

    def align(self):
        self.__pos = (self.__pos + 7) // 8 * 8

    def seek(self, pos):
        self.__pos = pos

    def tell(self):
        return self.__pos


import io


class BitBuffer2:
    def __init__(self):
        self.buf = io.BytesIO()
        self.cache = ""

    @classmethod
    def from_bytes(cls, a: bytes):
        ret = cls()
        ret.buf.write(a)
        ret.buf.seek(0)
        return ret

    def read_bytes(self, size):
        return self.buf.read(size)

    def read(self, n):
        while len(self.cache) < n:
            b = self.buf.read(1)[0]
            if b == 0xFF:
                nb = self.buf.read(1)[0]
                if nb == 0x00:
                    pass
                else:
                    # raise Exception("rst error")
                    b = self.buf.read(1)[0]
            self.cache += format(b, "08b")
        r = self.cache[:n]
        self.cache = self.cache[n:]
        return r

    def sync_rst(self):
        self.cache = ""
        b = bytearray([0, 0])
        while not (b[0] != 0 and b[1] == 0xFF):
            b[1] = b[0]
            b[0] = self.buf.read(1)[0]
        return b[0] - 1

    def consume_rst(self):
        i = self.buf.tell()
        b = self.buf.read(2)
        if b != b"\xff\xd0":
            self.buf.seek(i)

    def read_uint(self, size):
        r = self.read(size)
        return int(r, 2)

    def read_int(self, size):
        if size == 0:
            return 0
        ret = self.read(size)
        if ret[0] == "0":
            ret = "".join(map(lambda x: "1" if x == "0" else "0", ret))
            ret = int(ret, 2) * -1
        else:
            ret = int(ret, 2)
        return ret

    def align(self):
        self.cache = ""
