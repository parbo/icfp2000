import math
from vecmat import sub, dot, neg, normalize, mul, length

class Light(object):
    def __init__(self, d, c):
        self.direction = d
        self.color = c

    def get_direction(self, pos):
        return neg(self.direction), None

    def get_intensity(self, pos):
        return self.color

class PointLight(object):
    def __init__(self, p, c):
        self.pos = p
        self.color = c
        
    def get_direction(self, pos):
        d = sub(self.pos, pos)
        return d, length(d)

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
        self.exp = exp
    
    def get_direction(self, pos):
        d = sub(self.pos, pos)
        return d, length(d)

    def get_intensity(self, pos):
        d = sub(self.pos, pos)
        dsq = dot(d, d)
        angle = math.degrees(math.acos(-dot(d, self.d) / math.sqrt(dsq)))
        if angle > self.cutoff:
            return (0.0, 0.0, 0.0)
        i = pow(dot(normalize(sub(self.at, self.pos)), normalize(sub(pos, self.pos))), self.exp)
        return mul(self.color, i * 100.0 / (99.0 + dsq))


