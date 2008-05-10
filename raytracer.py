import math
from vecmat import normalize, add, sub, cmul, neg, mul, dot, length, cross
from transform import Transform
from ppmwriter import write_ppm
import evaluator
from primitives import Sphere, Union, Intersect, Difference
from lights import Light, PointLight, SpotLight

def get_surface(obj):
    if evaluator.get_type(obj) == 'Sphere':
        return (0.0, 1.0, 1.0), 1.0, 0.0, 1

def get_light_intensity(light):
    return light[0]

def get_light_pos(light):
    return light[1]

def get_ambient(c, ia, kd):
    return mul(cmul(ia, c), kd)

def get_diffuse(ic, lightdir, sn):
    df = dot(sn, lightdir)
    if df > 0.0:
        return mul(ic, df)
    return (0.0, 0.0, 0.0)

def get_specular(ic, lightdir, sn, pos, raypos, n):
    halfway = add(normalize(lightdir), normalize(sub(raypos, pos)))
    sp = dot(sn, halfway)
    if sp > 0.0:
        return mul(ic, pow(sp, n))
    return (0.0, 0.0, 0.0)

def trace(amb, lights, scene, depth, raypos, raydir):
    if depth == 0:
        return (0.0, 0.0, 0.0)
    i = scene.intersect(raypos, raydir)
    if i:
        isect = i[0]
        sc, kd, ks, n = isect.primitive.get_surface(isect.opos)
        c = get_ambient(sc, amb, kd)
        diffuse = (0.0, 0.0, 0.0)
        specular = (0.0, 0.0, 0.0)
        pos = isect.wpos
        normal = isect.normal
        for light in lights:
            lightdir, lightdistance = light.get_direction(pos)
            i = scene.intersect(pos, lightdir)
            if not i or lightdistance < i[0].distance:
                ic = cmul(sc, light.get_intensity(pos))
                if kd > 0.0:
                    diffuse = add(diffuse, get_diffuse(ic, lightdir, normal))
                if ks > 0.0:
                    specular = add(specular, get_specular(ic, lightdir, normal, pos, raypos, n))
        c = add(c, add(mul(diffuse, kd), mul(specular, ks)))        
        refl_raydir = normalize(sub(raydir, mul(normal, 2 * dot(raydir, normal))))
        if ks > 0.0:
            return add(c, mul(cmul(trace(amb, lights, scene, depth - 1, pos, refl_raydir), sc), ks))
        else:
            return c
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

    def blue(face, u, v):
        return (0.1, 0.1, 1.0), 0.3, 0.2, 6
    
    def mirror(face, u, v):
        return (0.1, 0.1, 1.0), 0.2, 0.8, 2
    
    def red(face, u, v):
        return (1.0, 0.1, 0.1), 0.3, 0.2, 6
    
    def green(face, u, v):
        return (0.1, 1.0, 0.1), 0.3, 0.2, 6

    def wavy(face, u, v):
        return (0.1, v * math.cos(math.pi * 10 * u), math.sin(math.pi * 10 * v)), 0.3, 0.05, 4
    
    import sys
    num = 1
    if len(sys.argv) > 1:
        num = int(sys.argv[1])
    for i in range(num):
        obj1 = Sphere(blue)
        obj1.translate(0.5, 0.0, 0.0)
        obj2 = Sphere(wavy)
        obj2.translate(-0.5, 0.0, 0.0)
        obj3 = Union(obj1, obj2)
        obj3.translate(-1.2, -1.0, 5.0)
        obj4 = Sphere(green)
        obj4.translate(0.5, 0.0, 0.0)
        obj5 = Sphere(blue)
        obj5.translate(-0.5, 0.0, 0.0)
        obj6 = Intersect(obj4, obj5)
        obj6.translate(1.2, -1.0, 5.0)
        obj7 = Union(obj3, obj6)
        obj8 = Sphere(red)
        obj8.translate(0.5, 0.0, 0.0)
        obj9 = Sphere(blue)
        obj9.translate(-0.5, 0.0, 0.0)
        obj10 = Difference(obj8, obj9)
        obj10.rotatey(-25)
        obj10.translate(0.0, 1.0, 5.0)
        scene1 = Union(obj7, obj10)

        lights1 = [Light((0.0, -1.0, 0.0), (0.5, 1.0, 0.5)),
                   PointLight((0.0, 0.0, -5.0), (0.5, 0.5, 0.5)),
                   SpotLight((0.0, 0.0, -5.0), (0.0, 0.0, 5.0), (1.0, 1.0, 1.0), 45, 4),
                   PointLight((5.0, 5.0, -5.0), (0.2, 1.0, 0.2))]

        a = Sphere(mirror)
        a.uscale(4.0)        
        a.translate(0.5, 0.0, 14.0)        
        b = Sphere(wavy)
        b.translate(-1.2, 1.0, 6.0)

        scene2 = Union(a, b)
        lights2 = [Light((0.0, 0.0, 1.0), (1.0, 1.0, 1.0)),
                   PointLight((-1.0, 0.0, -1.0), (1.0, 1.0, 1.0)),
                   SpotLight((2.0, 5.0, -1.0), (0.5, 0.0, 14.0), (1.0, 0.1, 1.0), 8, 8)
                   ]
        
        
        render((0.1, 0.1, 0.1),
               lights2,
               scene2,
               5,
               50,
               128,
               128,
               "render_%04d.ppm"%i)
