import math
import evaluator

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

def cmul(v1, v2):
    x1, y1, z1 = v1
    x2, y2, z2 = v2
    return (x1 * x2, y1 * y2, z1 * z2)

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

def length(v):
    return math.sqrt(dot(v, v))

def cross(v1, v2):
    x1, y1, z1 = v1
    x2, y2, z2 = v2
    return (y1 * z2 - z1 * y2,
            z1 * x2 - x1 * z2,
            x1 * y2 - y1 * x2)

def mvmul(m, v):
    m1, m2, m3, m4 = m
    m11, m12, m13, m14 = m1
    m21, m22, m23, m24 = m2
    m31, m32, m33, m34 = m3
    m41, m42, m43, m44 = m4
    v1, v2, v3, v4 = v
    return (m11 * v1 + m12 * v2 + m13 * v3 + m14 * v4,
            m21 * v1 + m22 * v2 + m23 * v3 + m24 * v4,
            m31 * v1 + m32 * v2 + m33 * v3 + m34 * v4,
            m41 * v1 + m42 * v2 + m43 * v3 + m44 * v4)
    
def mmmul(ma, mb):
    ma1, ma2, ma3, ma4 = ma
    ma11, ma12, ma13, ma14 = ma1
    ma21, ma22, ma23, ma24 = ma2
    ma31, ma32, ma33, ma34 = ma3
    ma41, ma42, ma43, ma44 = ma4
    mb1, mb2, mb3, mb4 = mb
    mb11, mb12, mb13, mb14 = mb1
    mb21, mb22, mb23, mb24 = mb2
    mb31, mb32, mb33, mb34 = mb3
    mb41, mb42, mb43, mb44 = mb4
    return ((ma11 * mb11 + ma12 * mb21 + ma13 * mb31 + ma14 * mb41,
             ma11 * mb12 + ma12 * mb22 + ma13 * mb32 + ma14 * mb42,
             ma11 * mb13 + ma12 * mb23 + ma13 * mb33 + ma14 * mb43,
             ma11 * mb14 + ma12 * mb24 + ma13 * mb34 + ma14 * mb44),
            (ma21 * mb11 + ma22 * mb21 + ma23 * mb31 + ma24 * mb41,
             ma21 * mb12 + ma22 * mb22 + ma23 * mb32 + ma24 * mb42,
             ma21 * mb13 + ma22 * mb23 + ma23 * mb33 + ma24 * mb43,
             ma21 * mb14 + ma22 * mb24 + ma23 * mb34 + ma24 * mb44),
            (ma31 * mb11 + ma32 * mb21 + ma33 * mb31 + ma34 * mb41,
             ma31 * mb12 + ma32 * mb22 + ma33 * mb32 + ma34 * mb42,
             ma31 * mb13 + ma32 * mb23 + ma33 * mb33 + ma34 * mb43,
             ma31 * mb14 + ma32 * mb24 + ma33 * mb34 + ma34 * mb44),
            (ma41 * mb11 + ma42 * mb21 + ma43 * mb31 + ma44 * mb41,
             ma41 * mb12 + ma42 * mb22 + ma43 * mb32 + ma44 * mb42,
             ma41 * mb13 + ma42 * mb23 + ma43 * mb33 + ma44 * mb43,
             ma41 * mb14 + ma42 * mb24 + ma43 * mb34 + ma44 * mb44))

def transform_vector(m, v):
    x, y, z = v
    return mvmul(m, (x, y, z, 0.0))[:-1]

def transform_point(m, p):
    x, y, z = p
    return mvmul(m, (x, y, z, 1.0))[:-1]

def get_surface(obj):
    if evaluator.get_type(obj) == 'Sphere':
        return (0.0, 1.0, 1.0), 1.0, 0.0, 1

def get_light_intensity(light):
    return light[0]

def get_light_pos(light):
    return light[1]

def get_transform(obj):
    return ((1.0, 0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0, 0.0),
            (0.0, 0.0, 1.0, 0.0),
            (0.0, 0.0, 0.0, 1.0))

def get_intensity(c, ia, kd, pos, sn, lights, ks, raypos, n):
    ambient = mul(cmul(ia, c), kd)
    diffuse = (0.0, 0.0, 0.0)
    specular = (0.0, 0.0, 0.0)
    for light in lights:
        i = get_light_intensity(light)
        lp = get_light_pos(light)
        lightdir = sub(lp, pos)
        dsq = dot(lightdir, lightdir)
        i = mul(i, 100.0 / (99.0 + dsq))
        df = max(dot(sn, lightdir), 0.0)
        ic = cmul(i, c)
        diffuse = add(diffuse, mul(ic, kd * df))
        halfway = add(normalize(lightdir), normalize(sub(raypos, pos)))
        sp = max(dot(sn, halfway), 0.0)
        specular = add(specular, mul(ic, ks * pow(sp, n)))
    return add(ambient, add(diffuse, specular))

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


def trace(amb, lights, obj, depth, raypos, raydir):
    t = get_transform(obj)
    o_raydir = transform_vector(t, raydir)
    o_raypos = transform_point(t, raypos)
    i = []
    if evaluator.get_type(obj) == 'Sphere':                
        i.append(intersect_ray_sphere(o_raypos, o_raydir))
    i.sort()
    if len(i[0]) > 0:
        pos = i[0][0][1] # todo: inverse transform
        sn = pos
        c = get_intensity((0.2, 0.3, 1.0), amb, 0.4, pos, sn, lights, 0.05, raypos, 6)
        return c # + recursive trace
    else:
        return (0.0, 0.0, 0.0)

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
            pixels.append(trace(amb, lights, obj, depth, raypos, raydir))            
    write_ppm(pixels, w, h, filename)


if __name__=="__main__":
    pixels = []
    for y in range(256):
        for x in range(256):
            pixels.append((x/255.0, y/255.0, (x+y)/(2.0*255.0)))
    write_ppm(pixels, 256, 256, "test.ppm")
    render((0.1, 0.1, 0.1),
           [((1.0, 1.0, 1.0), (1.0, 2.0, -1.0)),
            ((1.0, 0.1, 0.1), (-1.0, -1.0, -1.0)),
            ((0.1, 1.0, 0.1), (1.0, -1.0, -1.0))
            ],
           ('Sphere', (0)),
           3,
           120,
           640,
           480,
           "render.ppm")
