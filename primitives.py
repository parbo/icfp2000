import math
from transform import Transform
from vecmat import normalize, dot, neg, add, mul, length, sub
import copy

class Intersection(object):
    ENTRY = 0
    EXIT = 1
    def __init__(self, distance, wpos, opos, normal, primitive, t, face):
        self.distance = distance
        self.wpos = wpos
        self.opos = opos
        self.normal = normal
        self.primitive = primitive
        self.t = t
        self.face = face

    def __cmp__(self, rhs):
        return cmp(self.distance, rhs.distance)

    def __str__(self):
        return "%s %s %s %s %s %s"%(self.distance, self.wpos, self.opos, self.normal, self.primitive, self.t)

    def switch(self, t):
        if self.t != t:
            self.t = t
            self.normal = neg(self.normal)            

class Node(object):
    def intersect(self, raypos, raydir):
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

    def intersect(self, raypos, raydir):
        intersections = sorted([(i, self.obj1) for i in self.obj1.intersect(raypos, raydir)] +
                               [(i, self.obj2) for i in self.obj2.intersect(raypos, raydir)])
        res = []
        inside1 = 0
        inside2 = 0
        inside = False
        for i, obj in intersections:
            if i.t == Intersection.ENTRY:
                if obj == self.obj1:
                    inside1 += 1
                else:
                    inside2 += 1
            elif i.t == Intersection.EXIT:
                if obj == self.obj1:
                    inside1 -= 1
                else:
                    inside2 -= 1
                    
            newinside = self.rule(inside1 > 0, inside2 > 0)
            if inside and not newinside:
                i.switch(Intersection.EXIT)
                res.append(i)
            if not inside and newinside:
                i.switch(Intersection.ENTRY)
                res.append(i)
            inside = newinside
                
        return res

class Union(Operator):
    def rule(self, a, b):
        return a or b

class Intersect(Operator):
    def rule(self, a, b):
        return a and b
    
class Difference(Operator):
    def rule(self, a, b):
        return a and not b        

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

    def get_surface(self, i):
        def yellow(face, u, v):
            return (0.1, 1.0, 1.0), 0.4, 0.05, 4        

class Sphere(Primitive):
    def intersect(self, raypos, raydir):
        tr = self.transform
        raydir = tr.inv_transform_vector(raydir)
        scale = 1.0 / length(raydir)
        raydir = mul(raydir, scale) # normalize
        raypos = tr.inv_transform_point(raypos)
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
        n1 = normalize(tr.transform_normal(p1))
        n2 = normalize(tr.transform_normal(p2))
        return [Intersection(scale * t1, tr.transform_point(p1), p1, n1, self, Intersection.ENTRY, 0),
                Intersection(scale * t2, tr.transform_point(p2), p2, n2, self, Intersection.EXIT, 0)]

    def get_surface(self, i):
        x, y, z = i.opos
        v = (y + 1.0) / 2.0
        u = math.asin(x / math.sqrt(1 - y * y)) / (2.0 * math.pi)
        return self.surface(i.face, u, v)

class Cube(Primitive):
    slabs = [(((1.0, 0.0, 0.0), 5), (((-1.0, 0.0, 0.0), 2))),
             (((0.0, 1.0, 0.0), 4), (((0.0, -1.0, 0.0), 3))),
             (((0.0, 0.0, 1.0), 1), (((0.0, 0.0, -1.0), 0)))
             ]
    def intersect(self, raypos, raydir):
        tr = self.transform
        raydir = tr.inv_transform_vector(raydir)
        scale = 1.0 / length(raydir)
        raydir = mul(raydir, scale) # normalize
        raypos = tr.inv_transform_point(raypos)
        eps = 1e-15
        tmin = None
        tmax = None
        p = sub((0.5, 0.5, 0.5), raypos)
        for i in range(3):
            face1, face2 = self.slabs[i]
            e = p[i]
            f = raydir[i]
            if abs(f) > eps:
                t1 = (e + 0.5) / f
                t2 = (e - 0.5) / f
                if t1 > t2:
                    t1, t2 = t2, t1
                    face1, face2 = face2, face1
                if tmin is None or t1 > tmin[0]:
                    tmin = (t1, face1)
                if tmax is None or t2 < tmax[0]:
                    tmax = (t2, face2)
                if tmin > tmax:
                    return []
                if tmax < 0.0:
                    return []
            elif -e - 0.5 > 0.0 or -e + 0.5 < 0.0:
                return []
        if tmin[0] > 0:
            try:
                nmin = normalize(tr.transform_normal(tmin[1][0]))
                pmin = add(raypos, mul(raydir, tmin[0]))
                tpmin = tr.transform_point(pmin)
                nmax = normalize(tr.transform_normal(tmax[1][0]))
                pmax = add(raypos, mul(raydir, tmax[0]))
                tpmax = tr.transform_point(pmax)
                #print scale * tmin[0], scale * tmax[0], dot(raydir, nmin), dot(raydir, nmax)
                return [Intersection(scale * tmin[0], tpmin, pmin, nmin, self, Intersection.ENTRY, tmin[1][1]),
                        Intersection(scale * tmax[0], tpmax, pmax, nmax, self, Intersection.EXIT, tmax[1][1])]
            except:
                print tmin
                print tmax
        return []
        
    def get_surface(self, i):
        x, y, z = i.opos
        face = i.face
        if face == 0:
            return self.surface(0, x, y)
        elif face == 1:
            return self.surface(1, x, y)
        elif face == 2:
            return self.surface(2, z, y)
        elif face == 3:
            return self.surface(3, z, y)
        elif face == 4:
            return self.surface(4, x, z)
        elif face == 5:
            return self.surface(5, x, z)
        else:
            print opos
            assert False
            

class Cylinder(Primitive):
    pass

class Cone(Primitive):
    pass

class Plane(Primitive):
    def intersect(self, raypos, raydir):
        tr = self.transform
        raydir = tr.inv_transform_vector(raydir)
        scale = 1.0 / length(raydir)
        raydir = mul(raydir, scale) # normalize
        raypos = tr.inv_transform_point(raypos)
        np = (0.0, 1.0, 0.0) # unit plane
        denom = dot(np, raydir)
        if abs(denom) < 1e-7:
            return []
        t = -dot(np, raypos) / denom
        if t <= 0.0:
            return []
        p = add(raypos, mul(raydir, t))
        n = normalize(tr.transform_normal(np))
        tp = tr.transform_point(p)
        ts = scale * t
        return [Intersection(ts, tp, p, n, self, Intersection.ENTRY, 0),
                Intersection(ts, tp, p, neg(n), self, Intersection.EXIT, 0)]
        
    def get_surface(self, i):
        x, y, z = i.opos
        return self.surface(0, x, z)
