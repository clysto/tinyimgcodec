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
        return ret

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

    def seek(self, pos):
        self.__pos = pos

    def tell(self):
        return self.__pos
