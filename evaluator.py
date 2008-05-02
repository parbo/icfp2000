import math

class GMLRuntimeError(Exception):
    pass

class GMLTypeError(Exception):
    pass

class GMLSubscriptError(Exception):
    pass

def check_type(t, typename):
    if t[0] != typename:
        print "Wrong type", t[0], ", Expected", typename
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

def make_real(v):
    return ('Real', v)

def make_boolean(v):
    return ('Boolean', v)

def make_closure(env, v):
    return ('Closure', (dict(env), v[:]))

def make_array(v):
    return ('Array', v[:])

def make_point(x, y, z):
    return ('Point', (x,y,z))

def eval_if(env, stack, ast):
    c2 = stack.pop()
    c1 = stack.pop()
    pred = stack.pop()
    check_closure(c2)
    check_closure(c1)
    check_boolean(pred)
    if pred[1]:
        e, s, a = do_evaluate(c1[1][0], stack, c1[1][1])
    else:
        e, s, a = do_evaluate(c2[1][0], stack, c2[1][1])
    return env, s, ast

def eval_apply(env, stack, ast):
    c = stack.pop()
    check_closure(c)
    e, s, a = do_evaluate(c[1][0], stack, c[1][1])
    return env, s, ast

def eval_addi(env, stack, ast):
    i1 = stack.pop()
    i2 = stack.pop()
    check_integer(i1)
    check_integer(i2)
    return env, stack + [make_integer(i1[1]+i2[1])], ast

def eval_addf(env, stack, ast):
    r1 = stack.pop()
    r2 = stack.pop()
    check_real(r1)
    check_real(r2)
    return env, stack + [make_real(r1[1]+r2[1])], ast

def eval_acos(env, stack, ast):
    r1 = stack.pop()
    check_real(r1)
    return env, stack + [make_real(math.degrees(math.acos(r1[1])))], ast
    
def eval_asin(env, stack, ast):
    r1 = stack.pop()
    check_real(r1)
    return env, stack + [make_real(math.degrees(math.asin(r1[1])))], ast

def eval_clampf(env, stack, ast):
    r1 = stack.pop()
    check_real(r1)
    rv = r1[1]
    if rv < 0.0:
        rv = 0.0
    elif rv > 1.0:
        rv = 1.0
    return env, stack + [make_real(rv)], ast

def eval_cos(env, stack, ast):
    r1 = stack.pop()
    check_real(r1)
    res = math.cos(math.radians(r1[1]))
    if -1e-7 < res < 1e-7:
        res = 0.0
    return env, stack + [make_real(res)], ast

def eval_divi(env, stack, ast):
    i2 = stack.pop()
    i1 = stack.pop()
    check_integer(i1)
    check_integer(i2)
    rv = i1[1] / i2[1]
    if rv < 0:
        rv += 1 # we need to round towards zero
    return env, stack + [make_integer(rv)], ast

def eval_divf(env, stack, ast):
    r2 = stack.pop()
    r1 = stack.pop()
    check_real(r1)
    check_real(r2)
    rv = r1[1] / r2[1]
    return env, stack + [make_real(r1[1] / r2[1])], ast

def eval_eqi(env, stack, ast):
    i2 = stack.pop()
    i1 = stack.pop()
    check_integer(i1)
    check_integer(i2)
    rv = False
    if i1[1] == i2[1]:
        rv = True        
    return env, stack + [make_boolean(rv)], ast

def eval_eqf(env, stack, ast):
    r2 = stack.pop()
    r1 = stack.pop()
    check_real(r1)
    check_real(r2)
    rv = False
    if r1[1] == r2[1]:
        rv = True        
    return env, stack + [make_boolean(rv)], ast

def eval_floor(env, stack, ast):
    r = stack.pop()
    check_real(r)
    return env, stack + [make_integer(math.floor(r))], ast

def eval_frac(env, stack, ast):
    r = stack.pop()
    check_real(r)
    return env, stack + [make_real(math.modf(r[1])[0])], ast

def eval_lessi(env, stack, ast):
    i2 = stack.pop()
    i1 = stack.pop()
    check_integer(i1)
    check_integer(i2)
    rv = False
    if i1[1] < i2[1]:
        rv = True
    return env, stack + [make_boolean(rv)], ast

def eval_lessf(env, stack, ast):
    r2 = stack.pop()
    r1 = stack.pop()
    check_real(r1)
    check_real(r2)
    rv = False
    if r1[1] < r2[1]:
        rv = True
    return env, stack + [make_boolean(rv)], ast

def eval_modi(env, stack, ast):
    i2 = stack.pop()
    i1 = stack.pop()
    check_integer(i1)
    check_integer(i2)
    return env, stack + [make_integer(i1[1] % i2[1])], ast

def eval_muli(env, stack, ast):
    i2 = stack.pop()
    i1 = stack.pop()
    check_integer(i1)
    check_integer(i2)
    return env, stack + [make_integer(i1[1]*i2[1])], ast

def eval_mulf(env, stack, ast):
    r2 = stack.pop()
    r1 = stack.pop()
    check_real(r1)
    check_real(r2)
    return env, stack + [make_real(r1[1]*r2[1])], ast

def eval_negi(env, stack, ast):
    i = stack.pop()
    check_integer(i)
    return env, stack + [make_integer(-i[1])], ast

def eval_negf(env, stack, ast):
    r = stack.pop()
    check_real(r)
    return env, stack + [make_real(-r[1])], ast

def eval_real(env, stack, ast):
    i = stack.pop()
    check_integer(i)
    return env, stack + [make_real(float(i[1]))], ast

def eval_sin(env, stack, ast):
    r1 = stack.pop()
    check_real(r1)
    res = math.sin(math.radians(r1[1]))
    if -1e-7 < res < 1e-7:
        res = 0.0
    return env, stack + [make_real(res)], ast

def eval_sqrt(env, stack, ast):
    r1 = stack.pop()
    check_real(r1)
    return env, stack + [make_real(math.sqrt(r1[1]))], ast

def eval_subi(env, stack, ast):
    i2 = stack.pop()
    i1 = stack.pop()
    check_integer(i1)
    check_integer(i2)
    return env, stack + [make_integer(i1[1]-i2[1])], ast    

def eval_subf(env, stack, ast):
    r2 = stack.pop()
    r1 = stack.pop()
    check_real(r1)
    check_real(r2)
    return env, stack + [make_real(r1[1]-r2[1])], ast

def eval_point(env, stack, ast):
    z = stack.pop()
    y = stack.pop()
    x = stack.pop()
    check_real(x)
    check_real(y)
    check_real(z)
    return env, stack + [make_point(x[1], y[1], z[1])], ast

def eval_getx(env, stack, ast):
    p = stack.pop()
    check_point(p)
    return env, stack + [make_real(p[1][0])], ast

def eval_gety(env, stack, ast):
    p = stack.pop()
    check_point(p)
    return env, stack + [make_real(p[1][1])], ast

def eval_getz(env, stack, ast):
    p = stack.pop()
    check_point(p)
    return env, stack + [make_real(p[1][2])], ast

def eval_get(env, stack, ast):
    i = stack.pop()
    a = stack.pop()
    check_integer(i)
    check_array(a)
    if i[1] < 0 or i[1] > len(a[1]):
        raise GMLSubscriptError    
    return env, stack + [a[1][i[1]]], ast

def eval_length(env, stack, ast):
    a = stack.pop()
    check_array(a)
    return env, stack + [make_integer(len(a[1]))], ast

def do_evaluate(env, stack, ast):
    while ast:
        node = ast[0]
        ast = ast[1:]
        t, v = node
        if t in ['Integer', 'Real', 'Boolean', 'String']:
            stack = stack + [node]
        elif t == 'Binder':
            env[v] = stack[-1]
            stack = stack[:-1]
        elif t == 'Identifier':
            try:
                e = env[v]
                stack = stack + [e]
            except KeyError:
                raise GMLRuntimeError
        elif t == 'Function':
            c = make_closure(env, v)
            stack = stack + [c]
        elif t == 'Array':
            e, s, a = do_evaluate(env, [], v)
            stack = stack + [make_array(s)]
        elif t == 'Operator':
            env, stack, ast = globals()["eval_"+v](env, stack, ast)
    return env, stack, ast

def evaluate(ast):
    env = {}
    stack = []
    return do_evaluate(env, stack, ast)

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

    
