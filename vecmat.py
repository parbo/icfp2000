import math

def mcmp(m1, m2, eps=1e-10):
    for r in range(4):
        for c in range(4):
            if abs(m1[r][c] - m2[r][c]) > eps:
                return False
    return True

def identity():
    return ((1.0, 0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0, 0.0),
            (0.0, 0.0, 1.0, 0.0),
            (0.0, 0.0, 0.0, 1.0))

def transpose(m):
    m1, m2, m3, m4 = m
    m11, m12, m13, m14 = m1
    m21, m22, m23, m24 = m2
    m31, m32, m33, m34 = m3
    m41, m42, m43, m44 = m4
    return ((m11, m21, m31, m41),
            (m12, m22, m32, m42),
            (m13, m23, m33, m43),
            (m14, m24, m34, m44))
    
def normalize(v):
    m = math.sqrt(dot(v, v))
    x, y, z = v
    return (x / m, y / m, z / m)    

def add(v1, v2):
    x1, y1, z1 = v1
    x2, y2, z2 = v2
    return (x1 + x2, y1 + y2, z1 + z2)

def sub(v1, v2):
    x1, y1, z1 = v1
    x2, y2, z2 = v2
    return (x1 - x2, y1 - y2, z1 - z2)

def cmul(v1, v2):
    x1, y1, z1 = v1
    x2, y2, z2 = v2
    return (x1 * x2, y1 * y2, z1 * z2)

def neg(v):
    x, y, z = v
    return (-x, -y, -z)

def mul(v, s):
    x, y, z = v
    return (s * x, s * y, s * z)    

def dot(v1, v2):
    x1, y1, z1 = v1
    x2, y2, z2 = v2
    return x1 * x2 + y1 * y2 + z1 * z2

def length(v):
    x, y, z = v
    return math.sqrt(x * x + y * y + z * z)

def cross(v1, v2):
    x1, y1, z1 = v1
    x2, y2, z2 = v2
    return (y1 * z2 - z1 * y2,
            z1 * x2 - x1 * z2,
            x1 * y2 - y1 * x2)

def mvmul(m, v):
    m1, m2, m3, m4 = m
    m11, m12, m13, m14 = m1
    m21, m22, m23, m24 = m2
    m31, m32, m33, m34 = m3
    m41, m42, m43, m44 = m4
    v1, v2, v3, v4 = v
    return (m11 * v1 + m12 * v2 + m13 * v3 + m14 * v4,
            m21 * v1 + m22 * v2 + m23 * v3 + m24 * v4,
            m31 * v1 + m32 * v2 + m33 * v3 + m34 * v4,
            m41 * v1 + m42 * v2 + m43 * v3 + m44 * v4)

def mvmul3(m, v):
    m1, m2, m3, m4 = m
    m11, m12, m13, m14 = m1
    m21, m22, m23, m24 = m2
    m31, m32, m33, m34 = m3
    v1, v2, v3, v4 = v
    return (m11 * v1 + m12 * v2 + m13 * v3 + m14 * v4,
            m21 * v1 + m22 * v2 + m23 * v3 + m24 * v4,
            m31 * v1 + m32 * v2 + m33 * v3 + m34 * v4)
    
def mvmulx(m, v):
    m11, m12, m13, m14 = m[0]
    v1, v2, v3, v4 = v
    return m11 * v1 + m12 * v2 + m13 * v3 + m14 * v4

def mvmuly(m, v):
    m21, m22, m23, m24 = m[1]
    v1, v2, v3, v4 = v
    return m21 * v1 + m22 * v2 + m23 * v3 + m24 * v4

def mvmulz(m, v):
    m31, m32, m33, m34 = m[0]
    v1, v2, v3, v4 = v
    return m31 * v1 + m32 * v2 + m33 * v3 + m34 * v4
    
def mmmul(ma, mb):
    ma1, ma2, ma3, ma4 = ma
    ma11, ma12, ma13, ma14 = ma1
    ma21, ma22, ma23, ma24 = ma2
    ma31, ma32, ma33, ma34 = ma3
    ma41, ma42, ma43, ma44 = ma4
    mb1, mb2, mb3, mb4 = mb
    mb11, mb12, mb13, mb14 = mb1
    mb21, mb22, mb23, mb24 = mb2
    mb31, mb32, mb33, mb34 = mb3
    mb41, mb42, mb43, mb44 = mb4
    return ((ma11 * mb11 + ma12 * mb21 + ma13 * mb31 + ma14 * mb41,
             ma11 * mb12 + ma12 * mb22 + ma13 * mb32 + ma14 * mb42,
             ma11 * mb13 + ma12 * mb23 + ma13 * mb33 + ma14 * mb43,
             ma11 * mb14 + ma12 * mb24 + ma13 * mb34 + ma14 * mb44),
            (ma21 * mb11 + ma22 * mb21 + ma23 * mb31 + ma24 * mb41,
             ma21 * mb12 + ma22 * mb22 + ma23 * mb32 + ma24 * mb42,
             ma21 * mb13 + ma22 * mb23 + ma23 * mb33 + ma24 * mb43,
             ma21 * mb14 + ma22 * mb24 + ma23 * mb34 + ma24 * mb44),
            (ma31 * mb11 + ma32 * mb21 + ma33 * mb31 + ma34 * mb41,
             ma31 * mb12 + ma32 * mb22 + ma33 * mb32 + ma34 * mb42,
             ma31 * mb13 + ma32 * mb23 + ma33 * mb33 + ma34 * mb43,
             ma31 * mb14 + ma32 * mb24 + ma33 * mb34 + ma34 * mb44),
            (ma41 * mb11 + ma42 * mb21 + ma43 * mb31 + ma44 * mb41,
             ma41 * mb12 + ma42 * mb22 + ma43 * mb32 + ma44 * mb42,
             ma41 * mb13 + ma42 * mb23 + ma43 * mb33 + ma44 * mb43,
             ma41 * mb14 + ma42 * mb24 + ma43 * mb34 + ma44 * mb44))


if __name__=="__main__":
    pass
