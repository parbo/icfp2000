import math
from vecmat import normalize, add, sub, cmul, neg, mul, dot, length, cross
from transform import Transform
from ppmwriter import write_ppm
import evaluator
from primitives import Sphere, Plane, Cube, Cylinder, Cone, Union, Intersect, Difference
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
                #for ic in i: print ic
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
            up = int(u * 12) % 2
            vp = int(v * 12) % 2
            r, g, b = 0.0, 0.1, 0.0
            if up == 0:
                r = u
            if vp == 0:
                b = v
            print r, g, b
            return (r, g, b), 0.3, 0.2, 6
        l = [Light((1.0, -1.0, 1.0), (1.0, 1.0, 1.0))]
        s = Sphere(pattern)
        return s, l
                

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
