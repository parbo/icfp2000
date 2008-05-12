#!/bin/python

import re

operators = [
"acos",
"addi",
"addf",
"apply",
"asin",
"clampf",
"cone",
"cos",
"cube",
"cylinder",
"difference",
"divi",
"divf",
"eqi",
"eqf",
"floor",
"frac",
"get",
"getx",
"gety",
"getz",
"if",
"intersect",
"length",
"lessi",
"lessf",
"light",
"modi",
"muli",
"mulf",
"negi",
"negf",
"plane",
"point",
"pointlight",
"real",
"render",
"rotatex",
"rotatey",
"rotatez",
"scale",
"sin",
"sphere",
"spotlight",
"sqrt",
"subi",
"subf",
"translate",
"union",
"uscale"
]

# Sort descending on length to make matching greedy
operators.sort(lambda a, b: cmp(len(b), len(a)))

class EvaluationError(Exception):
    pass

def eval_boolean(s):
    if s == 'true':
        return True
    elif s == 'false':
        return False
    else:
        raise EvaluationError

tokens = []
tokens.append((re.compile(r"\s+"), "Whitespace", False, None))
tokens.append((re.compile(r"%.*\n"), "Comment", False, None))
tokens.append((re.compile(r"\{"), "BeginFunction", True, None))
tokens.append((re.compile(r"\}"), "EndFunction", True, None))
tokens.append((re.compile(r"\["), "BeginArray", True, None))
tokens.append((re.compile(r"\]"), "EndArray", True, None))
tokens.append((re.compile(r"true|false"), "Boolean", True, eval_boolean))
tokens.append((re.compile(r"[a-zA-Z][a-zA-Z0-9-_]*"), "Identifier", True, str))
tokens.append((re.compile(r"/[a-zA-Z][a-zA-Z0-9-_]*"), "Binder", True, lambda s: s[1:]))
tokens.append((re.compile(r"-{0,1}\d+(?:(?:\.\d+(?:[eE]-{0,1}\d+){0,1})|(?:[eE]-{0,1}\d+))"), "Real", True, lambda r: float(r)))
tokens.append((re.compile(r"-{0,1}\d+"), "Integer", True, lambda i: int(i)))
tokens.append((re.compile(r"\".*\""), "String", True, lambda s: s[1:-1]))

def do_tokenize(text, tokenlist):
    while text:
        for regexp, tokenname, emit, evaluator in tokens:
            m = regexp.match(text)
            if m:
                text = text[m.end():]
                if emit:
                    if tokenname == "Identifier":
                        if m.group() in operators:
                            tokenname = "Operator"
                    elif tokenname == "Binder":
                        if m.group() in operators:
                            raise EvaluationError, m.group() + " is a reserved word, cannot bind"
                    tokenlist.append((tokenname, evaluator and evaluator(m.group())))
                break
        else:
            break

def tokenize(text):
    ret = []
    do_tokenize(text, ret)
    return ret


def test(gml, res):
    t = tokenize(gml)
    if t == res:
        pass
    else:
        print gml,"!=",res
        print gml,"==",t
    

if __name__=="__main__":
    from preprocess import preprocess
    import sys
    
    if len(sys.argv) > 1:
        for f in sys.argv[1:]:
            print f
            print "=" * len(f)
            tokenlist = tokenize(preprocess(f))
            print tokenlist
            print
        sys.exit(0)

    # Run some tests
    test("1 % apa", [('Integer', 1)])
    test("1 % apa\n2", [('Integer', 1), ('Integer', 2)])
    test("1", [('Integer', 1)])
    test("123", [('Integer', 123)])
    test("-1", [('Integer', -1)])
    test("-123", [('Integer', -123)])
    test("1 2", [('Integer', 1), ('Integer', 2)])
    test("123 321", [('Integer', 123), ('Integer', 321)])
    test("-1-1", [('Integer', -1), ('Integer', -1)])
    test("1.0", [('Real', 1.0)])
    test("-1.0", [('Real', -1.0)])
    test("1.0e12", [('Real', 1.0e12)])
    test("1e12", [('Real', 1e12)])
    test("1e-12", [('Real', 1e-12)])
    test("\"test\"", [('String', 'test')])
    test("true", [('Boolean', True)])
    test("false", [('Boolean', False)])
    test("/x", [('Binder', 'x')])
    test("/x-y_2", [('Binder', 'x-y_2')])
    test("x", [('Identifier', 'x')])
    test("x-y_2", [('Identifier', 'x-y_2')])
    test("addi", [('Operator', 'addi')])
    test("[1 2]", [('BeginArray', None),
                   ('Integer', 1),
                   ('Integer', 2),
                   ('EndArray', None)])
    test("{1 2}", [('BeginFunction', None),
                   ('Integer', 1),
                   ('Integer', 2),
                   ('EndFunction', None)])
    test("{1 [2 3]}", [('BeginFunction', None),
                       ('Integer', 1),
                       ('BeginArray', None),
                       ('Integer', 2),
                       ('Integer', 3),
                       ('EndArray', None),
                       ('EndFunction', None)])

    
