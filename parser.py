class GMLSyntaxError(Exception):
    pass

def do_parse(tokenlist):
    ast = []
    if len(tokenlist) == 0:
        raise GMLSyntaxError
    while tokenlist:
        t = tokenlist[0]
        if t[0] in ['EndFunction', 'EndArray']:
            return tokenlist, ast
        tokenlist.pop(0)
        if t[0] == 'BeginFunction':
            tokenlist, tmp = do_parse(tokenlist)
            try:
                e = tokenlist.pop(0)
            except IndexError:
                raise GMLSyntaxError
            if e[0] != 'EndFunction':
                raise GMLSyntaxError
            ast.append(('Function', tmp))
        elif t[0] == 'BeginArray':
            tokenlist, tmp = do_parse(tokenlist)            
            try:
                e = tokenlist.pop(0)
            except IndexError:
                raise GMLSyntaxError
            if e[0] != 'EndArray':
                raise GMLSyntaxError
            ast.append(('Array', tmp))
        else:
            ast.append(t)
    return tokenlist, ast

def parse(tokenlist):
    tokenlist, ast = do_parse(tokenlist)
    if tokenlist:
        raise GMLSyntaxError
    return ast

def test(tokenlist, res):
    try:
        t = parse(tokenlist)    
        if t == res:
            pass
        else:
            print tokenlist,"!=",res
            print tokenlist,"==",t
    except Exception, e:
        if type(res) != type or not isinstance(e, res):
            raise    

if __name__=="__main__":
    from preprocess import preprocess
    from tokenizer import tokenize
    import sys
    
    if len(sys.argv) > 1:
        for f in sys.argv[1:]:
            print f
            print "=" * len(f)
            try:
                ast = parse(tokenize(preprocess(f)))
                print ast
            except GMLSyntaxError:
                print "contains syntax errors"
            print
        sys.exit(0)

    # Run some tests
    test([('BeginFunction', None)], GMLSyntaxError)
    test([('BeginArray', None)], GMLSyntaxError)
    test([('EndFunction', None)], GMLSyntaxError)
    test([('EndArray', None)], GMLSyntaxError)
    test([('BeginFunction', None),
          ('Integer', 1),
          ('BeginArray', None),
          ('Integer', 2),
          ('Integer', 3),
          ('EndFunction', None),
          ('EndArray', None)],
         GMLSyntaxError)
    test([('BeginArray', None),
          ('Integer', 1),
          ('Integer', 2),
          ('EndArray', None)],
         [('Array', [('Integer', 1), ('Integer', 2)])])
    test([('BeginFunction', None),
          ('Integer', 1),
          ('Integer', 2),
          ('EndFunction', None)],
         [('Function', [('Integer', 1), ('Integer', 2)])])
    test([('BeginFunction', None),
          ('Integer', 1),
          ('BeginArray', None),
          ('Integer', 2),
          ('Integer', 3),
          ('EndArray', None),
          ('EndFunction', None)],
         [('Function', [('Integer', 1), ('Array', [('Integer', 2), ('Integer', 3)])])])
    
