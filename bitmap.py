import struct

# refer : http://en.wikipedia.org/wiki/BMP_file_format
# DIB header : OS/2 BITMAPCOREHEADER

class Bitmap:
    def __init__(self, name, width, height, bcolor = (255,255,255)):
        self.name = name
        self.width = width
        self.height = height
        self.bcolor = bcolor

        self.data   = []
        for _ in range(self.height):
            line = []
            for _ in range(self.width):
                line.append(bcolor)
            self.data.append(line)

    def setpixel(self, x, y, lcolor):
        assert x>=0 and x < self.width, "pass the x border"
        assert y>=0 and y < self.height, "pass the y border"
        self.data[y][x] = lcolor

    def save(self):
        bmp       = 14
        dib       = 12
        offset    = bmp + dib
        padding   = (4 - (self.width*3) % 4) & 3

        f = open(self.name, "wb")
        f.write("BM")
        f.write(struct.pack("<I", offset + (self.width * 3 + padding) * self.height))
        f.write("DREW")
        f.write(struct.pack("<I", offset))
        f.write(struct.pack("<IHHHH", dib, self.width, self.height, 1, 24))
        for y in range(self.height):
            line = self.data[y]
            for x in range(self.width):
                r,g,b = line[x]
                f.write(struct.pack("BBB", b,g,r))
            f.write(padding * "\0")
        f.close()

def drawCircle():
    x = 150
    y = 100
    center_x = (x-1)/2
    center_y = (y-1)/2
    radius = 20

    bcolor = (100, 100,100)
    lcolor = (0, 0, 255)

    is_circle = lambda x,y: abs(pow(pow(x-center_x,2) + pow(y-center_y,2), 0.5)-radius)<0.4 and True or False

    m = Bitmap("circle.bmp", x, y, bcolor)
    for i in range(x):
        for j in range(y):
            if is_circle(i,j):
                m.setpixel(i,j,lcolor)
    m.save()
    pass

def drawMandelbrot():
    xa = -3.0
    xb = 1.5
    ya = -1.5
    yb = 1.5
    maxit = 255

    imgx = 1500
    imgy = 1000

    m = Bitmap("mandelbrot.bmp", imgx, imgy)
    for y in range(imgy):
        cy = y * (yb - ya) / (imgy - 1) + ya
        for x in range(imgx):
            cx = x * (xb - xa) / (imgx - 1) + xa
            c = cx + cy * 1j
            z = c
            for i in range(maxit):
                if abs(z) > 6: break
                z = z*z + c

            if i == maxit - 1:
                m.setpixel(x,y, (0,0,0))
            else:
                v = abs(z)/(i**2)
                r = 50
                g = 60
                b = v*255/10
                assert(b<255)
                m.setpixel(x,y,(r,g,b))
    m.save()

if __name__ == "__main__":
    drawCircle()
    drawMandelbrot()

