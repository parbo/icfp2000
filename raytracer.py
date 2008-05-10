import math
from vecmat import normalize, add, sub, cmul, neg, mul, dot, length, cross
from transform import Transform
from ppmwriter import write_ppm
import evaluator
from primitives import Sphere, Union, Intersect, Difference

def get_surface(obj):
    if evaluator.get_type(obj) == 'Sphere':
        return (0.0, 1.0, 1.0), 1.0, 0.0, 1

def get_light_intensity(light):
    return light[0]

def get_light_pos(light):
    return light[1]

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
        isect = i[0]
        obj = isect.primitive
        pos = isect.pos
        sn = isect.normal
        # TODO: call surface function
        kd = 0.3
        ks = 0.05
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
        #return add(c, trace(amb, lights, scene, depth - 1, refl_raypos, refl_raydir))
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
        obj1 = Sphere(None)
        obj1.translate(0.5, 0.0, 0.0)
        obj2 = Sphere(None)
        obj2.translate(-0.5, 0.0, 0.0)
        obj3 = Union(obj1, obj2)
        obj3.translate(-1.2, -1.0, 5.0)
        obj4 = Sphere(None)
        obj4.translate(0.5, 0.0, 0.0)
        obj5 = Sphere(None)
        obj5.translate(-0.5, 0.0, 0.0)
        obj6 = Intersect(obj4, obj5)
        obj6.translate(1.2, -1.0, 5.0)
        obj7 = Union(obj3, obj6)
        obj8 = Sphere(None)
        obj8.translate(0.5, 0.0, 0.0)
        obj9 = Sphere(None)
        obj9.translate(-0.5, 0.0, 0.0)
        obj10 = Difference(obj8, obj9)
        obj10.rotatey(-25)
        obj10.translate(0.0, 1.0, 5.0)
        obj = Union(obj7, obj10)
        render((0.2, 0.2, 0.2),
               [((0.5, 0.5, 0.5), (0.0, 0.0, -5.0)),
                ((1.0, 0.2, 0.2), (-5.0, 5.0, -5.0)),
                ((0.2, 1.0, 0.2), (5.0, 5.0, -5.0))],
               obj,
               3,
               50,
               512,
               512,
               "render_%04d.ppm"%i)
