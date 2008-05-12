import math
from vecmat import sub, dot, neg, normalize, mul, length

class Light(object):
    def __init__(self, d, c):
        self.direction = normalize(neg(d))
        self.color = c

    def get_direction(self, pos):
        return self.direction, None

    def get_intensity(self, pos):
        return self.color

class PointLight(object):
    def __init__(self, p, c):
        self.pos = p
        self.color = c
        
    def get_direction(self, pos):
        d = sub(self.pos, pos)
        dl = length(d)
        return mul(d, 1.0 / dl), length(d)

    def get_intensity(self, pos):
        d = sub(self.pos, pos)
        dsq = dot(d, d)
        return mul(self.color, 100.0 / (99.0 + dsq))

class SpotLight(object):
    def __init__(self, pos, at, c, cutoff, exp):
        self.pos = pos
        self.at = at
        self.d = normalize(sub(self.at, self.pos))
        self.color = c
        self.cutoff = cutoff
        self.coscutoff = math.cos(math.radians(self.cutoff))
        self.exp = exp
    
    def get_direction(self, pos):
        d = sub(self.pos, pos)
        dl = length(d)
        return mul(d, 1.0 / dl), length(d)

    def get_intensity(self, pos):
        q = sub(self.pos, pos)
        dsq = dot(q, q)
        invlend = 1 / math.sqrt(dsq)
        cosangle = -dot(q, self.d) * invlend
        if cosangle < self.coscutoff:
            return (0.0, 0.0, 0.0)
        i = pow(dot(self.d, mul(d, -invlend)), self.exp)
        return mul(self.color, i * 100.0 / (99.0 + dsq))


