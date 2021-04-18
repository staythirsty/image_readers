import tkinter
import zlib
import numpy as np
from colormap import rgb2hex

root = tkinter.Tk()

idat = b''
height = 0
width = 0

# a = left, b = above, c = upper
def paeth_predictor(a, b, c):
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    elif pb <= pc:
        return b
    else:
        return c

def read_img_hdr(data):
    global height, width
    height = int.from_bytes(data[4:8], "big")
    width = int.from_bytes(data[0:4], "big")

    print("Width", int.from_bytes(data[0:4], "big"))
    print("Height", int.from_bytes(data[4:8], "big"))
    print("Bit depth", int.from_bytes(data[8:9], "big"))
    print("Color type", int.from_bytes(data[9:10], "big"))
    print("Compression method", int.from_bytes(data[10:11], "big"))
    print("Filter method", int.from_bytes(data[11:12], "big"))
    print("Interlace method", int.from_bytes(data[12:13], "big"))

def read_img_data(data, height, width):
    raw_data = zlib.decompress(data)
    len(list(raw_data))
    raw_array = np.array(list(raw_data), dtype=np.int16).reshape((height, width * 4 + 1))
    print(raw_array.dtype)

    type_one_filter = raw_array[0:] == 1
    type_ones = raw_array[type_one_filter]
    if len(type_ones) > 0:
        type_ones[:1]

    for i in range(0, height):

        if raw_array[i, 0] == 1:

            for j in range(1, width):
                raw_array[i, j * 4 + 1] = (raw_array[i, j * 4 + 1] + raw_array[i, (j - 1) * 4 + 1]) % 256
                raw_array[i, j * 4 + 2] = (raw_array[i, j * 4 + 2] + raw_array[i, (j - 1) * 4 + 2]) % 256
                raw_array[i, j * 4 + 3] = (raw_array[i, j * 4 + 3] + raw_array[i, (j - 1) * 4 + 3]) % 256
                raw_array[i, j * 4 + 4] = (raw_array[i, j * 4 + 4] + raw_array[i, (j - 1) * 4 + 4]) % 256

        if raw_array[i, 0] == 2:
            for j in range(0, width):
                raw_array[i, j * 4 + 1] = (raw_array[i, j * 4 + 1] + raw_array[(i - 1), j * 4 + 1]) % 256
                raw_array[i, j * 4 + 2] = (raw_array[i, j * 4 + 2] + raw_array[(i - 1), j * 4 + 2]) % 256
                raw_array[i, j * 4 + 3] = (raw_array[i, j * 4 + 3] + raw_array[(i - 1), j * 4 + 3]) % 256
                raw_array[i, j * 4 + 4] = (raw_array[i, j * 4 + 4] + raw_array[(i - 1), j * 4 + 4]) % 256

        if raw_array[i, 0] == 4:

            raw_array[i, 1] = (raw_array[i, 1] + paeth_predictor(0, raw_array[i - 1, 1], 0)) % 256
            raw_array[i, 2] = (raw_array[i, 2] + paeth_predictor(0, raw_array[i - 1, 2], 0)) % 256
            raw_array[i, 3] = (raw_array[i, 3] + paeth_predictor(0, raw_array[i - 1, 3], 0)) % 256
            raw_array[i, 4] = (raw_array[i, 4] + paeth_predictor(0, raw_array[i - 1, 4], 0)) % 256

            for j in range(1, width):
                raw_array[i, j * 4 + 1] = (raw_array[i, j * 4 + 1] + paeth_predictor(raw_array[i, (j - 1) * 4 + 1],
                                                                                     raw_array[(i - 1), j * 4 + 1],
                                                                                     raw_array[
                                                                                         i - 1, (j - 1) * 4 + 1])) % 256
                raw_array[i, j * 4 + 2] = (raw_array[i, j * 4 + 2] + paeth_predictor(raw_array[i, (j - 1) * 4 + 2],
                                                                                     raw_array[(i - 1), j * 4 + 2],
                                                                                     raw_array[
                                                                                         i - 1, (j - 1) * 4 + 2])) % 256
                raw_array[i, j * 4 + 3] = (raw_array[i, j * 4 + 3] + paeth_predictor(raw_array[i, (j - 1) * 4 + 3],
                                                                                     raw_array[(i - 1), j * 4 + 3],
                                                                                     raw_array[
                                                                                         i - 1, (j - 1) * 4 + 3])) % 256
                raw_array[i, j * 4 + 4] = (raw_array[i, j * 4 + 4] + paeth_predictor(raw_array[i, (j - 1) * 4 + 4],
                                                                                     raw_array[(i - 1), j * 4 + 4],
                                                                                     raw_array[
                                                                                         i - 1, (j - 1) * 4 + 4])) % 256

        for j in range(0, width):
            r = raw_array[i, j * 4 + 1]
            g = raw_array[i, j * 4 + 2]
            b = raw_array[i, j * 4 + 3]
            a = raw_array[i, j * 4 + 4]

            myCanvas.create_line(j, i, j + 1, i, fill=rgb2hex(r, g, b))

    myCanvas.pack()
    root.mainloop()

def read_chunk(rdr):
    global idat
    chunk_length = int.from_bytes(rdr.read(4), "big")
    chunk_type = rdr.read(4).decode()
    chunk_data = rdr.read(chunk_length)
    chunk_crc = rdr.read(4)
    print(chunk_length, chunk_type)
    if chunk_type == "IHDR":
        read_img_hdr(chunk_data)
    elif chunk_type == "IDAT":
        print('')
        idat = b''.join([idat, chunk_data])
    else:
        print("-->", chunk_crc)

with open('sample.png', 'rb') as reader:
    signature = reader.read(8)
    for i in range(1, 100):
        read_chunk(reader)

myCanvas = tkinter.Canvas(root, bg="red", height=height, width=width, bd=0, highlightthickness=0,)
read_img_data(idat, height, width)
