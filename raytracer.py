import math
from vecmat import normalize, add, sub, cmul, neg, mul, dot, length, cross
from transform import Transform
from ppmwriter import write_ppm
import evaluator
from primitives import Sphere, Plane, Cube, Cylinder, Union, Intersect, Difference
from lights import Light, PointLight, SpotLight

def get_ambient(c, ia, kd):
    return mul(cmul(ia, c), kd)

def get_specular(ic, lightdir, sn, pos, raypos, n):
    halfway = normalize(add(lightdir, normalize(sub(raypos, pos))))
    sp = dot(sn, halfway)
    if sp > 0.0:
        return mul(ic, pow(sp, n))
    return (0.0, 0.0, 0.0)

def trace(amb, lights, scene, depth, raypos, raydir):
    i = scene.intersect(raypos, raydir)
    if i:
        isect = i[0]
        sc, kd, ks, n = isect.primitive.get_surface(isect)
        c = get_ambient(sc, amb, kd)
        diffuse = (0.0, 0.0, 0.0)
        specular = (0.0, 0.0, 0.0)
        pos = isect.wpos
        normal = isect.normal
        for light in lights:
            lightdir, lightdistance = light.get_direction(pos)
            df = dot(normal, lightdir)
            if df > 0.0:
                poseps = add(pos, mul(lightdir, 1e-7))
                i = scene.intersect(poseps, lightdir)
                if not i or (lightdistance and (lightdistance < i[0].distance)):
                    ic = cmul(sc, light.get_intensity(pos))
                    if kd > 0.0:
                        diffuse = add(diffuse, mul(ic, df))
                    if ks > 0.0:
                        specular = add(specular, get_specular(ic, lightdir, normal, pos, raypos, n))
        c = add(c, add(mul(diffuse, kd), mul(specular, ks)))
        if ks > 0.0 and depth > 0:
            refl_raydir = normalize(sub(raydir, mul(normal, 2 * dot(raydir, normal))))
            poseps = add(pos, mul(refl_raydir, 1e-7))
            rc = trace(amb, lights, scene, depth - 1, poseps, refl_raydir)
            return add(c, mul(cmul(rc, sc), ks))
        else:
            return c
    else:
        return (0.0, 0.0, 0.0)

def render(amb, lights, obj, depth, fov, w, h, filename):
    print "Rendering", filename
    pixels = []
    raypos = (0.0, 0.0, -1.0)
    w_world = 2.0 * math.tan(0.5 * math.radians(fov))    
    h_world = h * w_world / w
    c_x = -0.5 * w_world 
    c_y = 0.5 * h_world
    pw = w_world/w
    for y in range(h):
        for x in range(w):
            raydir = normalize((c_x + (x + 0.5) * pw, c_y - (y + 0.5) * pw, -raypos[2]))
            p = trace(amb, lights, obj, depth, raypos, raydir)
            pixels.append(p)
    print "Writing", filename
    write_ppm(pixels, w, h, filename)

if __name__=="__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "-p":
        try:
            import psyco
            psyco.full()
            print "Using psyco"
        except ImportError:
            print "psyco not installed"
            pass

    def blue(face, u, v):
        return (0.1, 0.1, 1.0), 0.3, 0.2, 6
    
    def amb(face, u, v):
        return (1.0, 1.0, 1.0), 1.0, 0.0, 0
    
    def mirror(face, u, v):
        return (1.0, 1.0, 1.0), 0.1, 1.0, 128
    
    def redfcn(face, u, v):
        return (1.0, 0.1, 0.1), 0.3, 0.2, 6
    
    def green(face, u, v):
        return (0.1, 1.0, 0.1), 0.3, 0.2, 6

    def cface(face, u, v):
        if face == 0:
            return (1.0, 0.0, 0.0), 0.3, 0.2, 6
        elif face == 1:
            return (0.0, 1.0, 0.0), 0.3, 0.2, 6
        elif face == 2:
            return (0.0, 0.0, 1.0), 0.3, 0.2, 6
        elif face == 3:
            return (1.0, 1.0, 0.0), 0.3, 0.2, 6
        elif face == 4:
            return (1.0, 0.0, 1.0), 0.3, 0.2, 6
        elif face == 5:
            return (0.0, 1.0, 1.0), 0.3, 0.2, 6

    def wavy(face, u, v):
        return (0.1, v * math.cos(math.pi * 10 * u), math.sin(math.pi * 10 * v)), 0.3, 0.05, 4
    
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
    obj8 = Sphere(redfcn)
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
    a.translate(0.5, 0.0, 3.0)        
    b = Sphere(redfcn)
    b.translate(-1.2, 1.0, -3.0)
    scene2 = Union(a, b)
    scene2.rotatey(20)
    scene2.translate(0.0, 0.0, 10.0)
    lights2 = [Light((0.0, -1.0, 0.0), (1.0, 1.0, 1.0)),
               PointLight((0.0, 0.0, -1.0), (1.0, 1.0, 1.0))
               ]

    p = Plane(redfcn)
    p.translate(0.0, -2.0, 0.0)
#    p.rotatez(-30)

    c = Cube(cface)
    c.translate(-0.5, -0.5, -0.5)
    c.uscale(2.0)
    c.rotatex(60)
    c.rotatey(-30)
    c.rotatez(45)
    c.translate(0.0, 0.0, 10.0)
    d = Sphere(redfcn)
    d.translate(-1.2, -1.3, 10.0)

    f = Union(c, d)
    s = Union(p, f)

    l = [Light((1.0, -1.0, 1.0), (1.0, 1.0, 1.0))]
    l2 = [PointLight((-3.0, -1.0, -5.0), (1.0, 1.0, 1.0))]

    black = (0.0,  0.0,  0.0)
    white = (1.0,  1.0,  1.0)
    red = (1.0,  0.0,  0.0)
    green = (0.0,  1.0,  0.0)
    blue = (0.0,  0.0,  1.0)
    magenta = (1.0,  0.0,  1.0)
    yellow = (1.0,  1.0,  0.0)
    cyan = (0.0,  1.0,  1.0)

    texture = ((blue,  white, blue),
               (white, blue,  white),
               (blue,  white, blue))

    def cubefcn(face, u, v):
        #print face, u, v
        def toIntCoord(f):
            i = int(math.floor(f * 3.0))
            if i == 3:
                return 2
            else:
                return i
        color = texture[toIntCoord(u)][toIntCoord(v)]
        kd = 0.3
        ks = 0.4
        n = 8.0
        return color, kd, ks, n

    ss = Sphere(redfcn)
    ss.uscale(1.1)
    
    cc = Cube(cubefcn)
    cc.translate(-0.5, -0.5, -0.5) 
    cc.uscale(1.5)
    cc.rotatex(-25.0)
    cc.rotatey(25.0)
    cc.rotatez(180)

    sc = Intersect(ss, cc)
    sc.translate(0.0, 0.0, 3.0)

    c1 = Sphere(redfcn)
#    c1.translate(0.0, -0.5, 0.0)
    c2 = Cylinder(redfcn)
    c2.translate(0.0, -0.5, 0.0)
    c2.scale(0.5, 2.0, 0.5)
    cyl = Difference(c1, c2)
    cyl.scale(2.0, 2.0, 2.0)
    cyl.rotatex(80.0)
#    cyl.rotatey(20)
    cyl.translate(0.0, 0.0, 5.0)

    c3 = Sphere(redfcn)
    c3.translate(-2.0, 2.0, 3)
    sc5 = Union(cyl, c3)

    render((1.0, 1.0, 1.0),
           l,
           sc5,
           0,
           90,
           256,
           256,
           "render.ppm")
