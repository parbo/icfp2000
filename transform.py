import math
from vecmat import mcmp, mmmul, mvmul, transpose, identity

class Transform(object):
    def __init__(self):
        self.m = identity()
        self.inv_m = identity()

    def _check(self):
        res = mmmul(self.m, self.inv_m)
        if mcmp(res, identity()):
            print "OK"
        else:
            print "FAIL", res

    def transform_point(self, p):
        return transform_point(self.m, p)

    def transform_vector(self, v):
        return transform_vector(self.m, v)

    def transform_normal(self, v):
        return transform_vector(transpose(self.inv_m), v)
    
    def inv_transform_point(self, p):
        return transform_point(self.inv_m, p)

    def inv_transform_vector(self, v):
        return transform_vector(self.inv_m, v)

    def scale(self, sx, sy, sz):
        sc = ((sx, 0.0, 0.0, 0.0),
              (0.0, sy, 0.0, 0.0),
              (0.0, 0.0, sz, 0.0),
              (0.0, 0.0, 0.0, 1.0))
        inv_sc = ((1.0/sx, 0.0, 0.0, 0.0),
                  (0.0, 1.0/sy, 0.0, 0.0),
                  (0.0, 0.0, 1.0/sz, 0.0),
                  (0.0, 0.0, 0.0, 1.0))
        self.m = mmmul(sc, self.m)
        self.inv_m = mmmul(self.inv_m, inv_sc)

    def isoscale(self, s):
        return self.scale(s, s, s)

    def translate(self, tx, ty, tz):
        tr = ((1.0, 0.0, 0.0, tx),
              (0.0, 1.0, 0.0, ty),
              (0.0, 0.0, 1.0, tz),
              (0.0, 0.0, 0.0, 1.0))
        inv_tr = ((1.0, 0.0, 0.0, -tx),
                  (0.0, 1.0, 0.0, -ty),
                  (0.0, 0.0, 1.0, -tz),
                  (0.0, 0.0, 0.0, 1.0))
        self.m = mmmul(tr, self.m)
        self.inv_m = mmmul(self.inv_m, inv_tr)

    def rotatex(self, d):
        cosd = math.cos(math.radians(d))
        sind = math.sin(math.radians(d))
        rx = ((1.0, 0.0, 0.0, 0.0),
              (0.0, cosd, -sind, 0.0),
              (0.0, sind, cosd, 0.0),
              (0.0, 0.0, 0.0, 1.0))
        inv_rx = ((1.0, 0.0, 0.0, 0.0),
                  (0.0, cosd, sind, 0.0),
                  (0.0, -sind, cosd, 0.0),
                  (0.0, 0.0, 0.0, 1.0))
        self.m = mmmul(rx, self.m)
        self.inv_m = mmmul(self.inv_m, inv_rx)

    def rotatey(self, d):
        cosd = math.cos(math.radians(d))
        sind = math.sin(math.radians(d))
        ry = ((cosd, 0.0, sind, 0.0),
              (0.0, 1.0, 0.0, 0.0),
              (-sind, 0.0, cosd, 0.0),
              (0.0, 0.0, 0.0, 1.0))
        inv_ry = ((cosd, 0.0, -sind, 0.0),
                  (0.0, 1.0, 0.0, 0.0),
                  (sind, 0.0, cosd, 0.0),
                  (0.0, 0.0, 0.0, 1.0))
        self.m = mmmul(ry, self.m)
        self.inv_m = mmmul(self.inv_m, inv_ry)
    
    def rotatez(self, d):
        cosd = math.cos(math.radians(d))
        sind = math.sin(math.radians(d))
        rz = ((cosd, -sind, 0.0, 0.0),
              (sind, cosd, 0.0, 0.0),
              (0.0, 0.0, 1.0, 0.0),
              (0.0, 0.0, 0.0, 1.0))
        inv_rz = ((cosd, sind, 0.0, 0.0),
                  (-sind, cosd, 0.0, 0.0),
                  (0.0, 0.0, 1.0, 0.0),
                  (0.0, 0.0, 0.0, 1.0))
        self.m = mmmul(rz, self.m)
        self.inv_m = mmmul(self.inv_m, inv_rz)

def transform_vector(m, v):
    x, y, z = v
    return mvmul(m, (x, y, z, 0.0))[:-1]

def transform_point(m, p):
    x, y, z = p
    return mvmul(m, (x, y, z, 1.0))[:-1]

if __name__=="__main__":
    t = Transform()
    t._check()
    t.scale(2,3,4)
    t._check()
    t.isoscale(math.pi)
    t._check()
    t.translate(7,11,13)
    t._check()
    t.rotatex(23)
    t._check()
    t.rotatey(12)
    t._check()
    t.rotatez(63)
    t._check()
