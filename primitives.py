import math
from transform import Transform
from vecmat import normalize, dot, neg, add, mul

class Primitive(object):
    def __init__(self, surface):
        self.surface = surface
        self.transform = Transform()

    def translate(self, tx, ty, tz):
        self.transform.translate(tx, ty, tz)

    def scale(self, sx, sy, sz):
        self.transform.scale(sx, sy, sz)

    def uscale(self, s):
        self.transform.isoscale(s)

    def rotatex(self, d):
        self.transform.rotatex(d)

    def rotatey(self, d):
        self.transform.rotatey(d)

    def rotatez(self, d):
        self.transform.rotatez(d)

class Union(Primitive):
    pass

class Intersection(Primitive):
    pass

class Difference(Primitive):
    pass

class Sphere(Primitive):
    def intersect(self, raypos, raydir):
        # According to Akenine-Moller
        # Transform to object space
        t = self.transform
        raydir = normalize(t.inv_transform_vector(raydir))
        raypos = t.inv_transform_point(raypos)
        s = dot(neg(raypos), raydir)
        lsq = dot(raypos, raypos)
        if s < 0.0 and lsq > 1.0:
            return None
        msq = lsq - s * s
        if msq > 1.0:
            return None  
        q = math.sqrt(1.0 - msq)
        t1 = s + q
        t2 = s - q
        if lsq > 1.0:
            t1, t2 = t2, t1
        return (self,
                ((t1, add(raypos, mul(raydir, t1))),
                 (t2, add(raypos, mul(raydir, t2)))))

class Cube(Primitive):
    pass

class Cylinder(Primitive):
    pass

class Cone(Primitive):
    pass

class Plane(Primitive):
    pass
