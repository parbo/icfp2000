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
        self.obj1.uscale(s)
        self.obj2.uscale(s)

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
        inside1 = 0
        inside2 = 0
        obj1i = self.obj1.intersect(raypos, raydir)
        if len(obj1i) % 2 != 0:
            inside1 = 1
        obj2i = self.obj2.intersect(raypos, raydir)
        if len(obj2i) % 2 != 0:
            inside2 = 1        
        intersections = sorted([(i, self.obj1) for i in obj1i] +
                               [(i, self.obj2) for i in obj2i])
        res = []
        inside = self.rule(inside1 > 0, inside2 > 0)
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
        return yellow

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
        if t1 > t2:
            t1, t2 = t2, t1
        ts = []
        if t1 > 0.0:
            p1 = add(raypos, mul(raydir, t1))
            n1 = normalize(tr.transform_normal(p1))
            ts.append(Intersection(scale * t1, tr.transform_point(p1), p1, n1, self, Intersection.ENTRY, 0))
        if t2 > 0.0:
            p2 = add(raypos, mul(raydir, t2))
            n2 = normalize(tr.transform_normal(p2))
            ts.append(Intersection(scale * t2, tr.transform_point(p2), p2, n2, self, Intersection.EXIT, 0))
        return ts

    def get_surface(self, i):
        x, y, z = i.opos
        v = (y + 1.0) / 2.0
        u = math.asin(x / math.sqrt(1 - y * y)) / (2.0 * math.pi)
        return self.surface(i.face, u, v)

class Cube(Primitive):
    slabs = [(((1.0, 0.0, 0.0), 3), (((-1.0, 0.0, 0.0), 2))),
             (((0.0, 1.0, 0.0), 4), (((0.0, -1.0, 0.0), 5))),
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
                if tmin[0] > tmax[0]:
                    return []
                if tmax[0] < 0.0:
                    return []
            elif -e - 0.5 > 0.0 or -e + 0.5 < 0.0:
                return []
        ts = []
        if tmin[0] > 0.0:
            nmin = normalize(tr.transform_normal(tmin[1][0]))
            pmin = add(raypos, mul(raydir, tmin[0]))
            tpmin = tr.transform_point(pmin)
            ts.append(Intersection(scale * tmin[0], tpmin, pmin, nmin, self, Intersection.ENTRY, tmin[1][1]))
        if tmax[0] > 0.0:
            nmax = normalize(tr.transform_normal(tmax[1][0]))
            pmax = add(raypos, mul(raydir, tmax[0]))
            tpmax = tr.transform_point(pmax)
            ts.append(Intersection(scale * tmax[0], tpmax, pmax, nmax, self, Intersection.EXIT, tmax[1][1]))
        return ts
        
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
    def _solveCyl(self, px, pz, dx, dz):
        fa0 = px * px + pz * pz - 1.0
        fa1 = px * dx + pz * dz
        fa2 = dx * dx + dz * dz
        fdiscr = fa1 * fa1 - fa0 * fa2
        if fdiscr < 0.0:
            return None
        else:
            froot = math.sqrt(fdiscr)
            finv = 1.0 / fa2
            t1 = ((-fa1 - froot) * finv, 0)
            t2 = ((-fa1 + froot) * finv, 0)
            if t1 > t2:
                t1, t2 = t2, t1
            return t1, t2

    def _solvePlane(self, py, dy):
        dinv = 1.0 / dy
        t1 = -py * dinv
        t2 = (-py + 1.0) * dinv
        face1 = 2 # bottom
        face2 = 1 # top
        tt1 = (t1, face1)
        tt2 = (t2, face2)
        if t1 > t2:
            tt1, tt2 = tt2, tt1
        return tt1, tt2

    def normal(self, face, pos):
        if face == 0:
            return (pos[0], 0.0, pos[2])
        elif face == 1:
            return (0.0, 1.0, 0.0)
        elif face == 2:
            return (0.0, -1.0, 0.0)
    
    def intersect(self, raypos, raydir):
        tr = self.transform
        raydir = tr.inv_transform_vector(raydir)
        scale = 1.0 / length(raydir)
        raydir = mul(raydir, scale) # normalize
        raypos = tr.inv_transform_point(raypos)
        eps = 1e-7

        px, py, pz = raypos
        dx, dy, dz = raydir
        ts = []
        if abs(dy) + eps >= 1.0:
            # ray is parallel to the cylinder axis
            frsd = 1.0 - px * px - pz * pz
            if frsd < 0.0:
                # outside cylinder
                return []
            ts = list(self._solvePlane(py, dy))
        elif abs(dy) < eps:
            # ray is orthogonal to the cylinder axis
            # check planes
            if py < 0.0 or py > 1.0:
                return []            
            # check cylinder
            res = self._solveCyl(px, pz, dx, dz)
            if not res:
                return []
            ts = list(res)
        else:
            # general case
            # check cylinder
            res = self._solveCyl(px, pz, dx, dz)
            if not res:
                #print "baz"
                return []
            tc1, tc2  = res
            # check planes
            tp1, tp2 = self._solvePlane(py, dy)
            # same min-max strategy as for cubes
            # Check max of mins
            tmin = tp1
            tmax = tp2
            if tc1 > tmin:
                tmin = tc1
            if tc2 < tmax:
                tmax = tc2
            if tmin[0] > tmax[0]:
                return []
            if tmax[0] < 0.0:
                return []
            ts = [tmin, tmax]

        tmin, tmax = ts
        ts = []
        if tmin[0] > 0.0:
            pmin = add(raypos, mul(raydir, tmin[0]))
            nmin = normalize(tr.transform_normal(self.normal(tmin[1], pmin)))
            tpmin = tr.transform_point(pmin)
            ts.append(Intersection(scale * tmin[0], tpmin, pmin, nmin, self, Intersection.ENTRY, tmin[1]))
        if tmax[0] > 0.0:
            pmax = add(raypos, mul(raydir, tmax[0]))
            nmax = normalize(tr.transform_normal(self.normal(tmax[1], pmax)))
            tpmax = tr.transform_point(pmax)
            ts.append(Intersection(scale * tmax[0], tpmax, pmax, nmax, self, Intersection.EXIT, tmax[1]))
        return ts

    def get_surface(self, i):
        x, y, z = i.opos
        face = i.face
        if face == 0:
            return self.surface(0, math.asin(x) / (2.0 * math.pi), y)
        elif face == 1:
            return self.surface(1, (x + 1.0) / 2.0, (y + 1.0) / 2.0)
        elif face == 2:
            return self.surface(2, (x + 1.0) / 2.0, (y + 1.0) / 2.0)
        else:
            print face
            raise

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
