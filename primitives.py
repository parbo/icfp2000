import math
from transform import Transform
from vecmat import normalize, dot, neg, add, mul, length

class Intersection(object):
    ENTRY = 0
    EXIT = 1
    def __init__(self, distance, pos, normal, primitive, t):
        self.distance = distance
        self.pos = pos
        self.normal = normal
        self.primitive = primitive
        self.t = t

    def __cmp__(self, rhs):
        return cmp(self.distance, rhs.distance)

    def __str__(self):
        return "%s %s %s %s %s"%(self.distance, self.pos, self.normal, self.primitive, self.t)

class Node(object):
    def intersect(raypos, raydir):
        return []

class Operator(Node):
    def __init__(self, obj1, obj2):
        self.obj1 = obj1
        self.obj2 = obj2

    def translate(self, tx, ty, tz):
        self.obj1.translate(tx, ty, tz)
        self.obj2.translate(tx, ty, tz)

    def scale(self, sx, sy, sz):
        self.obj1.scale(sx, sy, sz)
        self.obj2.scale(sx, sy, sz)

    def uscale(self, s):
        self.obj1.isoscale(s)
        self.obj2.isoscale(s)

    def rotatex(self, d):
        self.obj1.rotatex(d)
        self.obj2.rotatex(d)

    def rotatey(self, d):
        self.obj1.rotatey(d)
        self.obj2.rotatey(d)

    def rotatez(self, d):
        self.obj1.rotatez(d)
        self.obj2.rotatez(d)        

class Union(Operator):
    def intersect(self, raypos, raydir):
        intersections = sorted(self.obj1.intersect(raypos, raydir) + self.obj2.intersect(raypos, raydir))
        res = []
        inside = 0
        for i in intersections:
            if i.t == Intersection.ENTRY:
                inside += 1
                if inside == 1:
                    res.append(i)
            elif i.t == Intersection.EXIT:
                inside -= 1
                if inside == 0:
                    res.append(i)
        return res

class Intersect(Operator):
    def intersect(self, raypos, raydir):
        intersections = sorted(self.obj1.intersect(raypos, raydir) + self.obj2.intersect(raypos, raydir))
        res = []
        inside = 0
        for i in intersections:
            if i.t == Intersection.ENTRY:
                inside += 1
                if inside == 2:
                    res.append(i)
            elif i.t == Intersection.EXIT:
                inside -= 1
                if inside == 1:
                    res.append(i)
        return res

class Difference(Operator):
    def intersect(self, raypos, raydir):
        intersections = sorted([(i, self.obj1) for i in self.obj1.intersect(raypos, raydir)] +
                               [(i, self.obj2) for i in self.obj2.intersect(raypos, raydir)])
        res = []
        inside = 0
        curprim = None
        for i, obj in intersections:
            if i.t == Intersection.ENTRY:
                if obj == self.obj1:
                    inside += 1
                    if inside == 1:
                        curprim = i.primitive
                        res.append(i)                        
                else:
                    inside -= 1
                    if inside == 0:
                        res.append(Intersection(i.distance, i.pos, neg(i.normal), curprim, Intersection.EXIT))
                        curprim = None
            elif i.t == Intersection.EXIT:
                if obj == self.obj1:
                    inside -= 1
                    if inside == 0:
                        res.append(i)
                        curprim = None
                else:
                    inside += 1
                    if inside == 1:
                        res.append(Intersection(i.distance, i.pos, neg(i.normal), curprim, Intersection.ENTRY))
        return res

class Primitive(Node):
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

class Sphere(Primitive):
    def intersect(self, raypos, raydir):
        # According to Akenine-Moller
        # Transform to object space
        t = self.transform
        raydir = t.inv_transform_vector(raydir)
        scale = 1.0 / length(raydir)
        raydir = mul(raydir, scale) # normalize
        raypos = t.inv_transform_point(raypos)
        s = dot(neg(raypos), raydir)
        lsq = dot(raypos, raypos)
        if s < 0.0 and lsq > 1.0:
            return []
        msq = lsq - s * s
        if msq > 1.0:
            return []  
        q = math.sqrt(1.0 - msq)
        t1 = s + q
        t2 = s - q
        if lsq > 1.0:
            t1, t2 = t2, t1
        p1 = add(raypos, mul(raydir, t1))
        p2 = add(raypos, mul(raydir, t2))
        n1 = normalize(self.transform.transform_normal(p1))
        n2 = normalize(self.transform.transform_normal(p2))
        return [Intersection(scale * t1, t.transform_point(p1), n1, self, Intersection.ENTRY),
                Intersection(scale * t2, t.transform_point(p2), n2, self, Intersection.EXIT)]

class Cube(Primitive):
    pass

class Cylinder(Primitive):
    pass

class Cone(Primitive):
    pass

class Plane(Primitive):
    pass
