import math

class GMLRuntimeError(Exception):
    pass

class GMLTypeError(Exception):
    pass

class GMLSubscriptError(Exception):
    pass

def get_type(t):
    return t[0]

def check_type(obj, typename):
    t = get_type(obj)
    if t != typename:
        print "Wrong type", t, ", Expected", typename
        raise GMLTypeError

check_integer = lambda t: check_type(t, 'Integer')
check_real = lambda t: check_type(t, 'Real')
check_boolean = lambda t: check_type(t, 'Boolean')
check_closure = lambda t: check_type(t, 'Closure')
check_identifier = lambda t: check_type(t, 'Identifier')
check_point = lambda t: check_type(t, 'Point')
check_array = lambda t: check_type(t, 'Array')

def make_integer(v):
    return ('Integer', v)

def get_integer(i):
    check_integer(i)
    return i[1]

def make_real(v):
    return ('Real', v)

def get_real(r):
    check_real(r)
    return r[1]

def make_boolean(v):
    return ('Boolean', v)

def get_boolean(b):
    check_boolean(b)
    return b[1]

def make_closure(env, v):
    return ('Closure', (env, v[:]))

def get_closure_env(c):
    check_closure(c)
    return c[1][0]

def get_closure_function(c):
    check_closure(c)
    return c[1][1]

def make_array(v):
    return ('Array', v[:])

def get_array(a):
    check_array(a)
    return a[1]

def make_point(x, y, z):
    return ('Point', (x,y,z))

def get_point(p):
    check_point(p)
    return p[1]

def get_point_x(p):
    check_point(p)
    return p[1][0]

def get_point_y(p):
    check_point(p)
    return p[1][1]

def get_point_z(p):
    check_point(p)
    return p[1][2]

def make_sphere(s):
    return ('Sphere', (s,                        # surface
                       make_real(1.0),           # radius
                       make_point(0.0,0.0,0.0))) # origin

def make_plane(s):
    return ('Plane', (s,                         # surface
                      make_point(0.0,0.0,0.0),   # point in plane
                      make_point(0.0,1.0,0.0)))  # normal

def make_union(o1, o2):
    return ('Union', (o1, o2))

def make_stack():
    return ()

def push(stack, elem):
    return stack + (elem,)

def pop(stack):
    return stack[-1], stack[:-1]

def make_env():
    return {}

def add_env(env, key, value):
    newenv = dict(env)
    newenv[key] = value
    return newenv

def get_env(env, key):
    return env[key]

def eval_if(env, stack, ast):
    c2, stack = pop(stack)
    c1, stack = pop(stack)
    pred, stack = pop(stack)
    if get_boolean(pred):
        e, s, a = do_evaluate(get_closure_env(c1), stack, get_closure_function(c1))
    else:
        e, s, a = do_evaluate(get_closure_env(c2), stack, get_closure_function(c2))
    return env, s, ast

def eval_apply(env, stack, ast):
    c, stack = pop(stack)
    check_closure(c)
    e, s, a = do_evaluate(get_closure_env(c), stack, get_closure_function(c))
    return env, s, ast

def eval_addi(env, stack, ast):
    i1, stack = pop(stack)
    i2, stack = pop(stack)
    return env, push(stack, make_integer(get_integer(i1)+get_integer(i2))), ast

def eval_addf(env, stack, ast):
    r1, stack = pop(stack)
    r2, stack = pop(stack)
    return env, push(stack, make_real(get_real(r1)+get_real(r2))), ast

def eval_acos(env, stack, ast):
    r, stack = pop(stack)
    return env, push(stack, make_real(math.degrees(math.acos(get_real(r))))), ast
    
def eval_asin(env, stack, ast):
    r, stack = pop(stack)
    return env, push(stack, make_real(math.degrees(math.asin(get_real(r))))), ast

def eval_clampf(env, stack, ast):
    r, stack = pop(stack)
    rv = get_real(r)
    if rv < 0.0:
        rv = 0.0
    elif rv > 1.0:
        rv = 1.0
    return env, push(stack, make_real(rv)), ast

def eval_cos(env, stack, ast):
    r, stack = pop(stack)
    res = math.cos(math.radians(get_real(r)))
    if -1e-7 < res < 1e-7:
        res = 0.0
    return env, push(stack, make_real(res)), ast

def eval_divi(env, stack, ast):
    i2, stack = pop(stack)
    i1, stack = pop(stack)
    rv = get_integer(i1) / get_integer(i2)
    if rv < 0:
        rv += 1 # we need to round towards zero, which python doesn't
    return env, push(stack, make_integer(rv)), ast

def eval_divf(env, stack, ast):
    r2, stack = pop(stack)
    r1, stack = pop(stack)
    rv = getreal(r1) / get_real(r2)
    return env, push(stack, make_real(rv)), ast

def eval_eqi(env, stack, ast):
    i2, stack = pop(stack)
    i1, stack = pop(stack)
    rv = False
    if get_integer(i1) == get_integer(i2):
        rv = True        
    return env, push(stack, make_boolean(rv)), ast

def eval_eqf(env, stack, ast):
    r2, stack = pop(stack)
    r1, stack = pop(stack)
    rv = False
    if get_real(r1) == get_real(r2):
        rv = True        
    return env, push(stack, make_boolean(rv)), ast

def eval_floor(env, stack, ast):
    r, stack = pop(stack)
    return env, push(stack, make_integer(math.floor(get_real(r)))), ast

def eval_frac(env, stack, ast):
    r, stack = pop(stack)
    return env, push(stack, make_real(math.modf(get_real(r))[0])), ast

def eval_lessi(env, stack, ast):
    i2, stack = pop(stack)
    i1, stack = pop(stack)
    rv = False
    if get_integer(i1) < get_integer(i2):
        rv = True
    return env, push(stack, make_boolean(rv)), ast

def eval_lessf(env, stack, ast):
    r2, stack = pop(stack)
    r1, stack = pop(stack)
    rv = False
    if get_real(r1) < get_real(r2):
        rv = True
    return env, push(stack, make_boolean(rv)), ast

def eval_modi(env, stack, ast):
    i2, stack = pop(stack)
    i1, stack = pop(stack)
    return env, push(stack, make_integer(get_integer(i1) % get_integer(i2))), ast

def eval_muli(env, stack, ast):
    i2, stack = pop(stack)
    i1, stack = pop(stack)
    return env, push(stack, make_integer(get_integer(i1)*get_integer(i2))), ast

def eval_mulf(env, stack, ast):
    r2, stack = pop(stack)
    r1, stack = pop(stack)
    return env, push(stack, make_real(get_real(r1)*get_real(r2))), ast

def eval_negi(env, stack, ast):
    i, stack = pop(stack)
    return env, push(stack, make_integer(-get_integer(i))), ast

def eval_negf(env, stack, ast):
    r, stack = pop(stack)
    return env, push(stack, make_real(-get-real(r))), ast

def eval_real(env, stack, ast):
    i, stack = pop(stack)
    return env, push(stack, make_real(float(get_integer(i)))), ast

def eval_sin(env, stack, ast):
    r, stack = pop(stack)
    res = math.sin(math.radians(get_real(r)))
    if -1e-7 < res < 1e-7:
        res = 0.0
    return env, push(stack, make_real(res)), ast

def eval_sqrt(env, stack, ast):
    r, stack = pop(stack)
    return env, push(stack, make_real(math.sqrt(get_real(r)))), ast

def eval_subi(env, stack, ast):
    i2, stack = pop(stack)
    i1, stack = pop(stack)
    return env, push(stack, make_integer(get_integer(i1)-get_integer(i2))), ast    

def eval_subf(env, stack, ast):
    r2, stack = pop(stack)
    r1, stack = pop(stack)
    return env, push(stack, make_real(get_real(r1)-get_real(r2))), ast

def eval_point(env, stack, ast):
    z, stack = pop(stack)
    y, stack = pop(stack)
    x, stack = pop(stack)
    return env, push(stack, make_point(get_real(x), get_real(y), get_real(z))), ast

def eval_getx(env, stack, ast):
    p, stack = pop(stack)
    return env, push(stack, make_real(get_point_x(p))), ast

def eval_gety(env, stack, ast):
    p, stack = pop(stack)
    return env, push(stack, make_real(get_point_y(p))), ast

def eval_getz(env, stack, ast):
    p, stack = pop(stack)
    return env, push(stack, make_real(get_point_z(p))), ast

def eval_get(env, stack, ast):
    i, stack = pop(stack)
    a, stack = pop(stack)
    iv = get_integer(i)
    av = get_array(a)
    if iv < 0 or iv > len(av):
        raise GMLSubscriptError    
    return env, push(stack, av[iv]), ast

def eval_length(env, stack, ast):
    a, stack = pop(stack)
    return env, push(stack, make_integer(len(get_array(a)))), ast

def eval_sphere(env, stack, ast):
    surface, stack = pop(stack)
    return env, push(stack, make_sphere(s)), ast

def eval_plane(env, stack, ast):
    surface, stack = pop(stack)
    return env, push(stack, make_plane(s)), ast

def eval_translate(env, stack, ast):
    rtz, stack = pop(stack)
    rty, stack = pop(stack)
    rtx, stack = pop(stack)
    obj, stack = pop(stack)
    t = get_type(obj)
    if t == 'Sphere':
        pass
    elif t == 'Plane':
        pass
    else:
        raise GMLRuntimeError
    return env, stack + [retobj], ast

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
            env, stack, ast = globals()["eval_"+v](env, stack, ast)
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
    
    if len(sys.argv) > 1:
        for f in sys.argv[1:]:
            print f
            print "=" * len(f)
            try:
                r = evaluate(parse(tokenize(preprocess(f))))
                print r
            except GMLSyntaxError:
                print "contains syntax errors"
            except GMLRuntimeError:
                print "runtime error"
            except GMLSubscriptError:
                print "array index out of range"
            except KeyError:
                print "contains unimplemented feature"
            print
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

    
