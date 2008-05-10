def write_ppm(pixels, w, h, filename):
    f = open(filename, 'wb')
    f.write("P6 %s %s 255\n"%(w, h))
    for r, g, b in pixels:
        f.write(chr(int(255.0 * min(max(r, 0.0), 1.0))))
        f.write(chr(int(255.0 * min(max(g, 0.0), 1.0))))
        f.write(chr(int(255.0 * min(max(b, 0.0), 1.0))))

if __name__=="__main__":
    pixels = []
    for y in range(256):
        for x in range(256):
            pixels.append((x/255.0, y/255.0, (x+y)/(2.0*255.0)))
    write_ppm(pixels, 256, 256, "test.ppm")
