class GMLRuntimeError(Exception):
    pass

def eval_if(env, stack, ast):
    c2 = stack.pop()
    if c2[0] != 'Closure':
        raise GMLRuntimeError
    c1 = stack.pop()
    if c1[0] != 'Closure':
        raise GMLRuntimeError
    pred = stack.pop()
    if pred[0] == 'Identifier':
        pred = env[pred[1]]
    if pred[0] != 'Boolean':
        raise GMLRuntimeError
    if pred[1]:
        return do_evaluate(c1[1][0], stack, c1[1][1])
    else:
        return do_evaluate(c2[1][0], stack, c2[1][1])

def eval_apply(env, stack, ast):
    c = stack.pop()
    if c[0] != 'Closure':
        raise GMLRuntimeError
    e, s, a = do_evaluate(c[1][0], stack, c[1][1])
    return env, s, ast

def eval_addi(env, stack, ast):
    i1 = stack.pop()
    if i1[0] != 'Integer':
        raise GMLRuntimeError
    i2 = stack.pop()
    if i2[0] != 'Integer':
        raise GMLRuntimeError
    return env, stack + [('Integer', i1[1]+i2[1])], ast

def do_evaluate(env, stack, ast):
    while ast:
        #print env, stack, ast
        node = ast.pop(0)
        t, v = node
        if t in ['Integer', 'Real', 'Boolean', 'String']:
            stack.append(node)
        elif t == 'Binder':
            env[v] = stack.pop()
        elif t == 'Identifier':
            try:
                stack.append(env[v])
            except KeyError:
                raise GMLRuntimeError
        elif t == 'Function':
            stack.append(('Closure', (dict(env), v)))
        elif t == 'Array':
            stack.extend(v)
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

if __name__=="__main__":
    from preprocess import preprocess
    from tokenizer import tokenize
    from parser import parse
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
            print
        sys.exit(0)

    # Run some tests
    env, stack, ast = evaluate(parse(tokenize("1 /x")))
    print env['x']
    env, stack, ast = evaluate(parse(tokenize("true { 1 } { 2 } if")))
    print stack
    env, stack, ast = evaluate(parse(tokenize("false { 1 } { 2 } if")))
    print stack
    env, stack, ast = evaluate(parse(tokenize("false /b b { 1 } { 2 } if")))
    print stack
    env, stack, ast = evaluate(parse(tokenize("1 { /x x x } apply")))
    print stack
    env, stack, ast = evaluate(parse(tokenize("1 2 addi")))
    print stack
    env, stack, ast = evaluate(parse(tokenize("4 /x 2 x addi")))
    print stack
    env, stack, ast = evaluate(parse(tokenize("1 { /x x x } apply addi")))
    print stack
    
