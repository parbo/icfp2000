import math
from vecmat import normalize, add, sub, cmul, neg, mul, dot, length, cross
from transform import Transform
from ppmwriter import write_ppm
import evaluator
from primitives import Sphere

def get_surface(obj):
    if evaluator.get_type(obj) == 'Sphere':
        return (0.0, 1.0, 1.0), 1.0, 0.0, 1

def get_light_intensity(light):
    return light[0]

def get_light_pos(light):
    return light[1]

def get_transform(obj):
    return obj[1]

def get_ambient(c, ia, kd):
    return mul(cmul(ia, c), kd)

def get_diffuse_specular(light, pos, raypos, sc, sn, n):
    lp = get_light_pos(light)
    lightdir = sub(lp, pos)
    dsq = dot(lightdir, lightdir)
    df = dot(sn, lightdir)
    i = get_light_intensity(light)
    # Attenuate TODO: only for point lights!
    i = mul(i, 100.0 / (99.0 + dsq))
    ic = cmul(i, sc)
    diffuse = (0.0, 0.0, 0.0)
    if df > 0.0:
        diffuse = mul(ic, df)
    halfway = add(normalize(lightdir), normalize(sub(raypos, pos)))
    sp = dot(sn, halfway)
    specular = (0.0, 0.0, 0.0)
    if sp > 0.0:
        specular = mul(ic, pow(sp, n))
    return diffuse, specular

def trace(amb, lights, scene, depth, raypos, raydir):
    i = scene.intersect(raypos, raydir)
    if i:
        obj = i[0]
        p = i[1][0][1]
        pos = obj.transform.transform_point(p)
        sn = normalize(obj.transform.transform_normal(p))
        # TODO: call surface function
        kd = 0.4
        ks = 0.1
        n = 4
        sc = (0.2, 0.3, 1.0)
        c = get_ambient(sc, amb, kd)
        diffuse = (0.0, 0.0, 0.0)
        specular = (0.0, 0.0, 0.0)
        for light in lights:
            shadow = False # get_shadow
            if not shadow:
                d, s = get_diffuse_specular(light, pos, raypos, sc, sn, n)                
                diffuse = add(diffuse, d)
                specular = add(specular, s)
        c = add(c, add(mul(diffuse, kd), mul(specular, ks)))
        return c
        #return add(c, trace(amb, lights, obj, depth - 1, refl_raypos, refl_raydir))
    else:
        return (0.0, 0.0, 0.0)

def render(amb, lights, obj, depth, fov, w, h, filename):
    pixels = []
    raypos = (0.0, 0.0, -1.0)
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
    import sys
    num = 1
    if len(sys.argv) > 1:
        num = int(sys.argv[1])
    for i in range(num):
        obj = Sphere(None)
        obj.scale(2, 0.8, 0.8)
        obj.rotatex(10)
        obj.rotatey(i)
        obj.rotatez(i*2)
        obj.translate(0.0, 0.0, 5.0)
        render((0.1, 0.1, 0.1),
               [((1.0, 1.0, 1.0), (15.0, 15.0, -15.0)),
                ((1.0, 0.1, 0.1), (-5.0, -5.0, -5.0)),
                ((0.1, 1.0, 0.1), (5.0, -5.0, -5.0))
                ],
               obj,
               3,
               50,
               640,
               480,
               "render_%04d.ppm"%i)
