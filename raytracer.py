import math
from vecmat import normalize, add, sub, cmul, neg, mul, dot, length, cross
from transform import Transform
from ppmwriter import write_ppm
import evaluator
from primitives import Sphere, Plane, Cube, Cylinder, Cone, Union, Intersect, Difference, Intersection
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
        #for ic in i:
        #    print ic
        #print
        isect = i[0]
        if isect.t == Intersection.EXIT:
            return (0.0, 0.0, 0.0)
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

    def scene_sphere():
        def blue(face, u, v):
            return (0.1, 0.1, 1.0), 0.3, 0.2, 6
        l = [Light((1.0, -1.0, 1.0), (1.0, 1.0, 1.0))]
        s = Sphere(blue)
        return s, l

    def scene_plane():
        def yellow(face, u, v):
            return (0.1, 1.0, 1.0), 0.3, 0.2, 6
        l = [Light((1.0, -1.0, 1.0), (1.0, 1.0, 1.0))]
        p = Plane(yellow)
        p.translate(0.0, -4.0, 0.0)
        return p, l

    def scene_cube():
        def red(face, u, v):
            return (1.0, 0.1, 0.1), 0.3, 0.2, 6
        l = [Light((1.0, -1.0, 1.0), (1.0, 1.0, 1.0))]
        c = Cube(red)
        c.translate(-0.5, -0.5, -0.5)
        c.rotatex(10.0)
        c.rotatey(20.0)
        c.rotatez(30.0)
        return c, l

    def scene_cylinder():
        def green(face, u, v):
            return (0.1, 1.0, 0.1), 0.3, 0.2, 6
        l = [Light((1.0, -1.0, 1.0), (1.0, 1.0, 1.0))]
        c = Cylinder(green)
        c.translate(0.0, -0.5, 0.0)
        c.rotatex(60.0)
        c.rotatey(20.0)
        c.rotatez(40.0)
        return c, l

    def scene_cone():
        def green(face, u, v):
            return (0.1, 1.0, 0.1), 0.3, 0.2, 6
        l = [Light((1.0, -1.0, 1.0), (1.0, 1.0, 1.0))]
        c = Cone(green)
        c.translate(0.0, -0.5, 0.0)
        c.scale(2.0, 4.0, 2.0)
        #c.rotatex(90.0)
        return c, l

    def scene_texsphere():
        def pattern(face, u, v):
            up = int(u * 24) % 2
            vp = int(v * 12) % 2
            r, g, b = 0.0, 0.1, 0.0
            if up == 0:
                r = u
            if vp == 0:
                b = v
            return (r, g, b), 0.3, 0.2, 6
        l = [Light((1.0, -1.0, 1.0), (1.0, 1.0, 1.0))]
        s = Sphere(pattern)
        return s, l
                
    def scene_texcylinder():
        def pattern(face, u, v):
            up = int(u * 24) % 2
            vp = int(v * 12) % 2
            r, g, b = 0.0, 0.1, 0.0
            if up == 0:
                r = u
            if vp == 0:
                b = v
            return (r, g, b), 0.3, 0.2, 6
        l = [Light((1.0, -1.0, 1.0), (1.0, 1.0, 1.0))]
        c = Cylinder(pattern)
        c.translate(0.0, -0.5, 0.0)
        c.rotatex(60.0)
        c.rotatey(20.0)
        c.rotatez(40.0)
        return c, l

    def scene_texcylinder2():
        def test(face, u, v):
            if face == 0:
                return (0.1, 1.0, 0.1), 0.3, 0.2, 6
            u = u - 0.5
            v = v - 0.5
            b = u / (math.sqrt(u*u+v*v))
            if 0.0 < v:
                c = math.degrees(math.asin(b))
            else:
                c = 360 - math.degrees(math.asin(b))
            c = c + 180.8
            c = c / 30.0
            c = math.floor(c)
            c = evaluator.modi(c, 2)
            if c == 1:
                return (1.0, 0.1, 0.1), 0.3, 0.2, 6
            else:
                return (0.1, 0.1, 1.0), 0.3, 0.2, 6
        l = [Light((1.0, -1.0, 1.0), (1.0, 1.0, 1.0))]
        c = Cylinder(test)
        c.translate(0.0, -0.5, 0.0)
        c.rotatex(60.0)
        c.rotatey(20.0)
        c.rotatez(40.0)
        return c, l

    def scene_texcone():
        def pattern(face, u, v):
            up = int(u * 24) % 2
            vp = int(v * 12) % 2
            r, g, b = 0.0, 0.1, 0.0
            if up == 0:
                r = u
            if vp == 0:
                b = v
            return (r, g, b), 0.3, 0.2, 6
        l = [Light((1.0, -1.0, 1.0), (1.0, 1.0, 1.0))]
        c = Cone(pattern)
        c.translate(0.0, -0.5, 0.0)
        c.scale(2.0, 4.0, 2.0)
        #c.rotatex(90.0)
        return c, l

    def scene_texplane():
        def pattern(face, u, v):
            up = int(u * 6) % 2
            vp = int(v * 6) % 2
            r, g, b = 0.0, 0.1, 0.0
            if up == 0:
                r = (u % 1.0)
            if vp == 0:
                b = (v % 1.0)
            return (r, g, b), 0.3, 0.2, 6
        l = [Light((1.0, -1.0, 1.0), (1.0, 1.0, 1.0))]
        p = Plane(pattern)
        p.translate(0.0, -4.0, 0.0)
        return p, l

    def scene_texcube():
        def pattern(face, u, v):
            up = int(u * 6) % 2
            vp = int(v * 6) % 2
            r, g, b = 0.0, 0.1, 0.0
            if up == 0:
                r = (u % 1.0)
            if vp == 0:
                b = (v % 1.0)
            return (r, g, b), 0.3, 0.2, 6
        l = [Light((1.0, -1.0, 1.0), (1.0, 1.0, 1.0))]
        c = Cube(pattern)
        c.translate(-0.5, -0.5, -0.5)
        c.rotatex(10.0)
        c.rotatey(20.0)
        c.rotatez(30.0)
        return c, l

    def scene_union():
        def blue(face, u, v):
            return (0.1, 0.1, 1.0), 0.3, 0.2, 6
        def red(face, u, v):
            return (1.0, 0.1, 0.1), 0.3, 0.2, 6
        l = [Light((1.0, -1.0, 1.0), (1.0, 1.0, 1.0))]
        s1 = Sphere(blue)
        s1.translate(-0.6, 0.0, 0.0)
        s2 = Sphere(red)
        s2.translate(0.6, 0.0, 0.0)
        u = Union(s1, s2)
        return u, l

    def scene_intersect():
        def blue(face, u, v):
            return (0.1, 0.1, 1.0), 0.3, 0.2, 6
        def red(face, u, v):
            return (1.0, 0.1, 0.1), 0.3, 0.2, 6
        l = [Light((1.0, -1.0, 1.0), (1.0, 1.0, 1.0))]
        s1 = Sphere(blue)
        s1.translate(-0.6, 0.0, 0.0)
        s2 = Sphere(red)
        s2.translate(0.6, 0.0, 0.0)
        i = Intersect(s1, s2)
        return i, l

    def scene_difference():
        def blue(face, u, v):
            return (0.1, 0.1, 1.0), 0.3, 0.2, 6
        def red(face, u, v):
            return (1.0, 0.1, 0.1), 0.3, 0.2, 6
        l = [Light((1.0, -1.0, 1.0), (1.0, 1.0, 1.0))]
        c1 = Cylinder(blue)
        c1.translate(0.0, -0.5, 0.0)
        c2 = Cylinder(red)
        c2.translate(0.0, -0.5, 0.0)
        c2.scale(0.8, 1.2, 0.8)
        d = Difference(c1, c2)
        d.rotatex(60.0)
        d.rotatey(20.0)
        d.rotatez(40.0)
        return d, l

    def scene_difference2():
        def blue(face, u, v):
            return (0.1, 0.1, 1.0), 0.3, 0.2, 6
        def red(face, u, v):
            return (1.0, 0.1, 0.1), 0.3, 0.2, 6
        l = [Light((1.0, -1.0, 1.0), (1.0, 1.0, 1.0))]
        c1 = Sphere(blue)
        c2 = Cylinder(red)
        c2.translate(0.0, -0.5, 0.0)
        c2.scale(0.4, 2.0, 0.4)
        d = Difference(c1, c2)
        d.rotatex(85.0)
        d.rotatey(20.0)
        d.rotatez(40.0)
        return d, l

    def scene_difference3():
        def blue(face, u, v):
            return (0.1, 0.1, 1.0), 0.3, 0.2, 6
        def red(face, u, v):
            return (1.0, 0.1, 0.1), 0.3, 0.2, 6
        l = [Light((1.0, -1.0, 1.0), (1.0, 1.0, 1.0))]
        c1 = Cone(blue)
        c1.translate(0.0, -0.5, 0.0)
        c1.scale(1.0, 3.0, 1.0)
        c2 = Cube(red)
        c2.translate(-0.5, 1.0, -0.5)
        c3 = Cube(red)
        c3.translate(-0.5, -1.5, -0.5)
        u = Union(c2, c3)
        d = Difference(c1, u)
        d.rotatex(85.0)
        d.rotatey(20.0)
        d.rotatez(40.0)
        return d, l

    def scene_planes():
        def blue(face, u, v):
            return (0.1, 0.1, 1.0), 0.3, 0.2, 6
        def red(face, u, v):
            return (1.0, 0.1, 0.1), 0.3, 0.2, 6
        l = [PointLight((1.0, 1.0, -1.0), (1.0, 1.0, 1.0))]
        p1 = Plane(blue)
        p1.rotatez(30)
        p1.translate(0.0, -2.0, 0.0)
        p2 = Plane(blue)
        p2.rotatez(-30)
        p2.translate(0.0, -2.0, 0.0)
        p3 = Plane(red)
        p3.rotatex(-90)
        p3.translate(0.0, 0.0, -1.0)
        p4 = Plane(blue)
        p4.rotatez(180)
        p4.translate(0.0, -4.0, 0.0)
        p5 = Plane(red)
        p5.rotatex(90)
        p5.translate(0.0, 0.0, 1.0)
        obj = Intersect(Intersect(Intersect(p1, p2), Intersect(p3, p4)), p5)
        obj.translate(0.0, 3.0, 0.0)
        obj.rotatex(50)
        obj.rotatey(20)
        obj.rotatez(30)
        obj.translate(0.0, 0.0, 3.0)
        return obj, l
        p6 = Plane(blue)
        p6.translate(0.0, 0.0, 0.0)
        p6.rotatex(270)
        i1 = Intersect(p1, p2)
        i2 = Intersect(p3, p4)
        i3 = Intersect(p5, p6)
        i4 = Intersect(i1, i2)
        i5 = Intersect(i3, i4)
        sc = i5
#        sc.rotatex(10)
#        sc.rotatey(20)
#        sc.rotatez(30)
        return Intersect(p4, Intersect(p2, p6)), l


    def scene_viewhole():
        def blue(face, u, v):
            return (0.1, 0.1, 1.0), 0.3, 0.2, 6
        def red(face, u, v):
            return (1.0, 0.1, 0.1), 0.3, 0.2, 6
        def green(face, u, v):
            return (0.1, 1.0, 0.1), 0.3, 0.2, 6
        def yellow(face, u, v):
            return (0.1, 1.0, 1.0), 0.3, 0.2, 6
        def cyan(face, u, v):
            return (1.0, 1.0, 0.1), 0.3, 0.2, 6
        def magenta(face, u, v):
            return (1.0, 0.1, 1.0), 0.3, 0.2, 6
        def white(face, u, v):
            return (1.0, 1.0, 1.0), 0.3, 0.2, 6
        def apex(rot):
            p1 = Plane(white)
            p1.rotatex(90)
            p2 = Plane(red)
            p2.rotatex(-90)
            p2.rotatey(30)
            i = Intersect(p1, p2)
            i.rotatey(rot)
            return i
        l = [Light((1.0, -1.0, 1.0), (1.0, 1.0, 1.0))]
        cyl3 = Cylinder(red)
        cyl3.scale(0.9999, 0.9999, 0.999)
        cyl3.translate(0.0, 3.0, 0.0)
        cyl4 = Cylinder(blue)
        cyl4.scale(0.7, 4.0, 0.7)
        a1 = apex(15)
        a2 = apex(75)
        a3 = apex(135)
        a4 = apex(195)
        a5 = apex(255)
        a6 = apex(315)
        u3 = Union(Union(Union(Union(Union(a1, a2), a3), a4), a5), a6)
        cyl5 = Cylinder(magenta)
        i2 = Intersect(u3, cyl5)
        u4 = Union(cyl4, i2)
        u4.translate(0.0, 3.5, 0.0)
        d = Difference(cyl3, u4)        
        d.translate(0.0, -4.0, 2.0)
        d.uscale(4.0)
        d.rotatex(-50)
        return d, l
        
        
        d1 = Difference(u2, u4)
        #d1.uscale(0.4)
        d1.translate(0.0, -3.0, 2.0)
        d1.rotatex(-50)
        return d1, l
        
    def render_scene(scene, lights, name):
        scene.translate(0.0, 0.0, 3.0)
        render((1.0, 1.0, 1.0),
               lights,
               scene,
               3,
               90,
               256,
               256,
               name)

    if len(sys.argv) > 2:
        s = "scene_"+sys.argv[2]
        v = locals()[s]
        scene, lights = v()
        render_scene(scene, lights, s + ".ppm")
    else:
        for k, v in locals().items():
            if k.startswith("scene_"):
                scene, lights = v()
                render_scene(scene, lights, k + ".ppm")
