import math
import primitives
import lights
import raytracer
import copy

class GMLRuntimeError(Exception):
    pass

class GMLTypeError(Exception):
    pass

class GMLSubscriptError(Exception):
    pass

def get_type(t):
    return t[0]

def get_value(t):
    return t[1]

def check_type(obj, typename):
    return typename == get_type(obj)

check_integer = lambda t: check_type(t, 'Integer')
check_real = lambda t: check_type(t, 'Real')
check_boolean = lambda t: check_type(t, 'Boolean')
check_closure = lambda t: check_type(t, 'Closure')
check_identifier = lambda t: check_type(t, 'Identifier')
check_point = lambda t: check_type(t, 'Point')
check_array = lambda t: check_type(t, 'Array')
check_string = lambda t: check_type(t, 'String')

def make_integer(v):
    assert type(v) == int
    return ('Integer', v)

def get_integer(i):
    assert check_integer(i)
    return get_value(i)

def make_string(v):
    assert type(v) == str
    return ('String', v)

def get_string(s):
    assert check_string(s)
    return get_value(s)

def make_real(v):
    assert type(v) == float
    return ('Real', v)

def get_real(r):
    assert check_real(r)
    return get_value(r)

def make_boolean(v):
    assert type(v) == bool
    return ('Boolean', v)

def get_boolean(b):
    assert check_boolean(b)
    return get_value(b)

def make_closure(env, v):
    return ('Closure', (env, v[:]))

def get_closure_env(c):
    assert check_closure(c)
    closure = get_value(c)
    return closure[0]

def get_closure_function(c):
    assert check_closure(c)
    closure = get_value(c)
    return closure[1]

def make_array(v):
    tmp = []
    while v:
        e, v = pop(v)
        tmp.insert(0, e)
    return ('Array', tmp)

def get_array(a):
    assert check_array(a)
    return get_value(a)

def make_point(x, y, z):
    return ('Point', (x,y,z))

def get_point(p):
    assert check_point(p)
    return get_value(p)

def get_point_x(p):
    point = get_point(p)
    return point[0]

def get_point_y(p):
    point = get_point(p)
    return point[1]

def get_point_z(p):
    point = get_point(p)
    return point[2]

def get_node(obj):
    if not isinstance(obj, primitives.Node):
        raise GMLTypeError
    return obj

def make_stack():
    return ()

def push(stack, elem):
    return (elem, stack)

def pop(stack):
    return stack[0], stack[1]

def make_env():
    return {}

def add_env(env, key, value):
    newenv = dict(env)
    newenv[key] = value
    return newenv

def get_env(env, key):
    return env[key]

def eval_if(env, stack):
    c2, stack = pop(stack)
    c1, stack = pop(stack)
    pred, stack = pop(stack)
    if get_boolean(pred):
        e, s, a = do_evaluate(get_closure_env(c1), stack, get_closure_function(c1))
    else:
        e, s, a = do_evaluate(get_closure_env(c2), stack, get_closure_function(c2))
    return env, s

def eval_apply(env, stack):
    c, stack = pop(stack)
    assert check_closure(c)
    e, s, a = do_evaluate(get_closure_env(c), stack, get_closure_function(c))
    return env, s

def eval_addi(env, stack):
    i1, stack = pop(stack)
    i2, stack = pop(stack)
    return env, push(stack, make_integer(get_integer(i1)+get_integer(i2)))

def eval_addf(env, stack):
    r1, stack = pop(stack)
    r2, stack = pop(stack)
    return env, push(stack, make_real(get_real(r1)+get_real(r2)))

def eval_acos(env, stack):
    r, stack = pop(stack)
    return env, push(stack, make_real(math.degrees(math.acos(get_real(r)))))
    
def eval_asin(env, stack):
    r, stack = pop(stack)
    return env, push(stack, make_real(math.degrees(math.asin(get_real(r)))))

def eval_clampf(env, stack):
    r, stack = pop(stack)
    rv = get_real(r)
    if rv < 0.0:
        rv = 0.0
    elif rv > 1.0:
        rv = 1.0
    return env, push(stack, make_real(rv))

def eval_cos(env, stack):
    r, stack = pop(stack)
    res = math.cos(math.radians(get_real(r)))
    if -1e-7 < res < 1e-7:
        res = 0.0
    return env, push(stack, make_real(res))

def eval_divi(env, stack):
    i2, stack = pop(stack)
    i1, stack = pop(stack)
    rv = get_integer(i1) / get_integer(i2)
    if rv < 0:
        rv += 1 # we need to round towards zero, which python doesn't
    return env, push(stack, make_integer(rv))

def eval_divf(env, stack):
    r2, stack = pop(stack)
    r1, stack = pop(stack)
    rv = get_real(r1) / get_real(r2)
    return env, push(stack, make_real(rv))

def eval_eqi(env, stack):
    i2, stack = pop(stack)
    i1, stack = pop(stack)
    rv = False
    if get_integer(i1) == get_integer(i2):
        rv = True        
    return env, push(stack, make_boolean(rv))

def eval_eqf(env, stack):
    r2, stack = pop(stack)
    r1, stack = pop(stack)
    rv = False
    if get_real(r1) == get_real(r2):
        rv = True        
    return env, push(stack, make_boolean(rv))

def eval_floor(env, stack):
    r, stack = pop(stack)
    return env, push(stack, make_integer(int(math.floor(get_real(r)))))

def eval_frac(env, stack):
    r, stack = pop(stack)
    return env, push(stack, make_real(math.modf(get_real(r))[0]))

def eval_lessi(env, stack):
    i2, stack = pop(stack)
    i1, stack = pop(stack)
    rv = False
    if get_integer(i1) < get_integer(i2):
        rv = True
    return env, push(stack, make_boolean(rv))

def eval_lessf(env, stack):
    r2, stack = pop(stack)
    r1, stack = pop(stack)
    rv = False
    if get_real(r1) < get_real(r2):
        rv = True
    return env, push(stack, make_boolean(rv))

def eval_modi(env, stack):
    i2, stack = pop(stack)
    i1, stack = pop(stack)
    return env, push(stack, make_integer(get_integer(i1) % get_integer(i2)))

def eval_muli(env, stack):
    i2, stack = pop(stack)
    i1, stack = pop(stack)
    return env, push(stack, make_integer(get_integer(i1)*get_integer(i2)))

def eval_mulf(env, stack):
    r2, stack = pop(stack)
    r1, stack = pop(stack)
    return env, push(stack, make_real(get_real(r1)*get_real(r2)))

def eval_negi(env, stack):
    i, stack = pop(stack)
    return env, push(stack, make_integer(-get_integer(i)))

def eval_negf(env, stack):
    r, stack = pop(stack)
    return env, push(stack, make_real(-get_real(r)))

def eval_real(env, stack):
    i, stack = pop(stack)
    return env, push(stack, make_real(float(get_integer(i))))

def eval_sin(env, stack):
    r, stack = pop(stack)
    res = math.sin(math.radians(get_real(r)))
    if -1e-7 < res < 1e-7:
        res = 0.0
    return env, push(stack, make_real(res))

def eval_sqrt(env, stack):
    r, stack = pop(stack)
    return env, push(stack, make_real(math.sqrt(get_real(r))))

def eval_subi(env, stack):
    i2, stack = pop(stack)
    i1, stack = pop(stack)
    return env, push(stack, make_integer(get_integer(i1)-get_integer(i2)))    

def eval_subf(env, stack):
    r2, stack = pop(stack)
    r1, stack = pop(stack)
    return env, push(stack, make_real(get_real(r1)-get_real(r2)))

def eval_point(env, stack):
    z, stack = pop(stack)
    y, stack = pop(stack)
    x, stack = pop(stack)
    return env, push(stack, make_point(get_real(x), get_real(y), get_real(z)))

def eval_getx(env, stack):
    p, stack = pop(stack)
    return env, push(stack, make_real(get_point_x(p)))

def eval_gety(env, stack):
    p, stack = pop(stack)
    return env, push(stack, make_real(get_point_y(p)))

def eval_getz(env, stack):
    p, stack = pop(stack)
    return env, push(stack, make_real(get_point_z(p)))

def eval_get(env, stack):
    i, stack = pop(stack)
    a, stack = pop(stack)
    iv = get_integer(i)
    av = get_array(a)
    if iv < 0 or iv > len(av):
        raise GMLSubscriptError
    try:
        return env, push(stack, av[iv])
    except:
        print iv
        raise

def eval_length(env, stack):
    a, stack = pop(stack)
    return env, push(stack, make_integer(len(get_array(a))))

def eval_sphere(env, stack):
    surface, stack = pop(stack)
    return env, push(stack, primitives.Sphere(get_surface(surface)))

def eval_cube(env, stack):
    surface, stack = pop(stack)
    return env, push(stack, primitives.Cube(get_surface(surface)))

def eval_cylinder(env, stack):
    surface, stack = pop(stack)
    return env, push(stack, primitives.Cylinder(get_surface(surface)))

def eval_cone(env, stack):
    surface, stack = pop(stack)
    return env, push(stack, primitives.Cone(get_surface(surface)))

def eval_plane(env, stack):
    surface, stack = pop(stack)
    return env, push(stack, primitives.Plane(get_surface(surface)))

def eval_union(env, stack):
    obj1, stack = pop(stack)
    obj2, stack = pop(stack)
    return env, push(stack, primitives.Union(obj1, obj2))

def eval_intersect(env, stack):
    obj1, stack = pop(stack)
    obj2, stack = pop(stack)
    return env, push(stack, primitives.Intersect(obj1, obj2))

def eval_difference(env, stack):
    obj1, stack = pop(stack)
    obj2, stack = pop(stack)
    return env, push(stack, primitives.Difference(obj1, obj2))

def eval_translate(env, stack):
    tz, stack = pop(stack)
    ty, stack = pop(stack)
    tx, stack = pop(stack)
    obj, stack = pop(stack)
    obj.translate(get_real(tx), get_real(ty), get_real(tz))
    return env, push(stack, obj)

def eval_scale(env, stack):
    sz, stack = pop(stack)
    sy, stack = pop(stack)
    sx, stack = pop(stack)
    obj, stack = pop(stack)
    obj.scale(get_real(sx), get_real(sy), get_real(sz))
    return env, push(stack, obj)

def eval_uscale(env, stack):
    s, stack = pop(stack)
    obj, stack = pop(stack)
    obj.uscale(get_real(s))
    return env, push(stack, obj)

def eval_rotatex(env, stack):
    d, stack = pop(stack)
    obj, stack = pop(stack)
    obj.rotatex(get_real(d))
    return env, push(stack, obj)

def eval_rotatey(env, stack):
    d, stack = pop(stack)
    obj, stack = pop(stack)
    obj.rotatey(get_real(d))
    return env, push(stack, obj)

def eval_rotatez(env, stack):
    d, stack = pop(stack)
    obj, stack = pop(stack)
    obj.rotatez(get_real(d))
    return env, push(stack, obj)

def eval_light(env, stack):
    color, stack = pop(stack)
    d, stack = pop(stack)
    return env, push(stack, lights.Light(get_point(d),
                                         get_point(color)))

def eval_pointlight(env, stack):
    color, stack = pop(stack)
    pos, stack = pop(stack)
    return env, push(stack, lights.PointLight(get_point(pos),
                                              get_point(color)))

def eval_spotlight(env, stack):
    exp, stack = pop(stack)
    cutoff, stack = pop(stack)
    color, stack = pop(stack)
    at, stack = pop(stack)
    pos, stack = pop(stack)
    return env, push(stack, lights.SpotLight(get_point(pos),
                                             get_point(at),
                                             get_point(color),
                                             get_real(cutoff),
                                             get_real(exp)))

def eval_render(env, stack):
    file, stack = pop(stack)
    ht, stack = pop(stack)
    wid, stack = pop(stack)
    fov, stack = pop(stack)
    depth, stack = pop(stack)
    obj, stack = pop(stack)
    lights, stack = pop(stack)
    amb, stack = pop(stack)
    raytracer.render(get_point(amb),
                     get_array(lights),
                     get_node(obj),
                     get_integer(depth),
                     get_real(fov),
                     get_integer(wid),
                     get_integer(ht),
                     get_string(file))
    return env, stack

def get_surface(surface):
    assert check_closure(surface)
    def do_surface(face, u, v):
        stack = make_stack()
        stack = push(stack, make_integer(face))
        stack = push(stack, make_real(u))
        stack = push(stack, make_real(v))
        e, stack, a = do_evaluate(get_closure_env(surface),
                                  stack,
                                  get_closure_function(surface))
        n, stack = pop(stack)
        ks, stack = pop(stack)
        kd, stack = pop(stack)
        sc, stack = pop(stack)
        return get_point(sc), get_real(kd), get_real(ks), get_real(n)
    return do_surface

def do_evaluate(env, stack, ast):
    while ast:        
        node = ast[0]
        ast = ast[1:]
        t, v = node
        if t in ['Integer', 'Real', 'Boolean', 'String']:
            stack = push(stack, node)
        elif t == 'Binder':
            i, stack = pop(stack)
            env = add_env(env, v, i)
        elif t == 'Identifier':
            try:
                e = get_env(env, v)
                if isinstance(e, primitives.Node):
                    e = copy.deepcopy(e)
                stack = push(stack, e)
            except KeyError:
                raise GMLRuntimeError
        elif t == 'Function':
            c = make_closure(env, v)
            stack = push(stack, c)
        elif t == 'Array':
            e, s, a = do_evaluate(env, make_stack(), v)
            stack = push(stack, make_array(s))
        elif t == 'Operator':
            env, stack = globals()["eval_"+v](env, stack)
    return env, stack, ast

def evaluate(ast):    
    return do_evaluate(make_env(), make_stack(), ast)

def test(ast, res):    
    try:
        t = evaluate(ast)    
        if t == res:
            pass
        else:
            print ast,"!=",res
            print ast,"==",t
    except Exception, e:
        if type(res) != type or not isinstance(e, res):
            raise

def run(gml):
    return evaluate(parse(tokenize(gml)))

if __name__=="__main__":
    from preprocess import preprocess
    from tokenizer import tokenize
    from parser import parse, GMLSyntaxError
    import sys

    psyco = (sys.argv[1] == "-p")
    if psyco:
        files = sys.argv[2:]
    else:
        files = sys.argv[1:]


    if psyco:
        try:
            import psyco
            psyco.full()
            print "Using psyco"
        except ImportError:
            print "psyco not installed"
            pass
    
    for f in files:
        print f
        print "=" * len(f)
        try:
            r = evaluate(parse(tokenize(preprocess(f))))
        except GMLSyntaxError:
            print "contains syntax errors"
        except GMLRuntimeError:
            print "runtime error"
        except GMLSubscriptError:
            print "array index out of range"
        except KeyError:
            print "contains unimplemented feature"
        print

    if files:
        sys.exit(0)

    # Run some tests
    env, stack, ast = run("1 /x")
    print env['x']
    env, stack, ast = run("true { 1 } { 2 } if")
    print stack
    env, stack, ast = run("false { 1 } { 2 } if")
    print stack
    env, stack, ast = run("false /b b { 1 } { 2 } if")
    print stack
    env, stack, ast = run("1 { /x x x } apply")
    print stack
    env, stack, ast = run("1 2 addi")
    print stack
    env, stack, ast = run("4 /x 2 x addi")
    print stack
    env, stack, ast = run("1 { /x x x } apply addi")
    print stack
    env, stack, ast = run("{ /x x x } /dup { dup apply muli } /sq 3 sq apply")
    print stack
    env, stack, ast = run("{ /x /y x y } /swap 3 4 swap apply")
    print stack
    env, stack, ast = run("{ /self /n n 2 lessi { 1 } { n 1 subi self self apply n muli } if } /fact 12 fact fact apply")
    print stack

    
