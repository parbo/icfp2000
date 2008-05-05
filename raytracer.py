import math

def normalize(v):
    m = math.sqrt(dot(v, v))
    x, y, z = v
    return (x / m, y / m, z / m)    

def add(v1, v2):
    x1, y1, z1 = v1
    x2, y2, z2 = v2
    return (x1 + x2, y1 + y2, z1 + z2)

def sub(v1, v2):
    x1, y1, z1 = v1
    x2, y2, z2 = v2
    return (x1 - x2, y1 - y2, z1 - z2)

def neg(v):
    x, y, z = v
    return (-x, -y, -z)

def mul(v, s):
    x, y, z = v
    return (s * x, s * y, s * z)    

def dot(v1, v2):
    x1, y1, z1 = v1
    x2, y2, z2 = v2
    return x1 * x2 + y1 * y2 + z1 * z2

def cross(v1, v2):
    x1, y1, z1 = v1
    x2, y2, z2 = v2
    return (y1 * z2 - z1 * y2,
            z1 * x2 - x1 * z2,
            x1 * y2 - y1 * x2)

def intersect_ray_sphere(raypos, raydir):
    # According to Akenine-Moller
    s = dot(neg(raypos), raydir)
    #print s
    lsq = dot(raypos, raypos)
    if s < 0.0 and lsq > 1.0:
        return ()
    msq = lsq - s * s
    if msq > 1.0:
        return ()    
    q = math.sqrt(1.0 - msq)
    t1 = s + q
    t2 = s - q
    if lsq > 1.0:
        t1, t2 = t2, t1
    return ((t1, add(raypos, mul(raydir, t1))),
            (t2, add(raypos, mul(raydir, t2))))

def write_ppm(pixels, w, h, filename):
    f = open(filename, 'wb')
    f.write("P6 %s %s 255\n"%(w, h))
    for r, g, b in pixels:
        f.write(chr(int(255.0 * min(max(r, 0.0), 1.0))))
        f.write(chr(int(255.0 * min(max(g, 0.0), 1.0))))
        f.write(chr(int(255.0 * min(max(b, 0.0), 1.0))))


def render(amb, lights, obj, depth, fov, w, h, filename):
    pixels = []
    raypos = (0.0, 0.0, -1000.1)
    w_world = 2.0 * math.tan(0.5 * math.radians(fov))    
    h_world = h * w_world / w
    print w_world, h_world
    c_x = -0.5 * w_world 
    c_y = 0.5 * h_world
    pw = w_world/w
    print c_x, c_y, pw
    for y in range(h):
        for x in range(w):
            raydir = normalize((c_x + (x + 0.5) * pw, c_y - (y + 0.5) * pw, -raypos[2]))
            #print raydir
            intersections = intersect_ray_sphere(raypos, raydir)
            if len(intersections) > 0:
                i = dot(intersections[0][1], (1.0, 1.0, -1.0))
                pixels.append((0.25 + i * 0.5, 0.25 + i * 0.5, 0.25 + i * 0.5))
            else:
                pixels.append((0.0, 0.0, 0.0))
    write_ppm(pixels, w, h, filename)


if __name__=="__main__":
    pixels = []
    for y in range(256):
        for x in range(256):
            pixels.append((x/255.0, y/255.0, (x+y)/(2.0*255.0)))
    write_ppm(pixels, 256, 256, "test.ppm")
    render(0, [], None, 3, 120, 640, 480, "render.ppm")
