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

tokens = []
tokens.append((re.compile(r"\s+"), "Whitespace", False))
tokens.append((re.compile(r"%.*\n"), "Comment", False))
tokens.append((re.compile("|".join(operators)), "Operator", True))
tokens.append((re.compile(r"true|false"), "Boolean", True))
tokens.append((re.compile(r"[a-zA-Z][a-zA-Z0-9-_]*"), "Identifier", True))
tokens.append((re.compile(r"/[a-zA-Z][a-zA-Z0-9-_]*"), "Binder", True))
tokens.append((re.compile(r"-{0,1}\d+(?:(?:\.\d+(?:[eE]-{0,1}\d+){0,1})|(?:[eE]-{0,1}\d+))"), "Real", True))
tokens.append((re.compile(r"-{0,1}\d+"), "Integer", True))
tokens.append((re.compile(r"\".*\""), "String", True))

def do_tokenize(text, tokenlist):
    while text:
        if text[0] == '}':
            return text[1:]
        elif text[0] == ']':
            return text[1:]
        elif text[0] == '{':
            tmp = []
            text = do_tokenize(text[1:], tmp)
            tokenlist.append(("Function", tmp))
        elif text[0] == '[':
            tmp = []
            text = do_tokenize(text[1:], tmp)
            tokenlist.append(("Array", tmp))
        if not text:
            return
        for regexp, tokenname, emit in tokens:
            m = regexp.match(text)
            if m:
                text = text[m.end():]
                if emit:
                    tokenlist.append((tokenname, m.group()))
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

    # Run some tests
    test("1 % apa", [('Integer', '1')])
    test("1 % apa\n2", [('Integer', '1'), ('Integer', '2')])
    test("1", [('Integer', '1')])
    test("123", [('Integer', '123')])
    test("-1", [('Integer', '-1')])
    test("-123", [('Integer', '-123')])
    test("1 2", [('Integer', '1'), ('Integer', '2')])
    test("123 321", [('Integer', '123'), ('Integer', '321')])
    test("-1-1", [('Integer', '-1'), ('Integer', '-1')])
    test("1.0", [('Real', '1.0')])
    test("-1.0", [('Real', '-1.0')])
    test("1.0e12", [('Real', '1.0e12')])
    test("1e12", [('Real', '1e12')])
    test("1e-12", [('Real', '1e-12')])
    test("\"test\"", [('String', '\"test\"')])
    test("true", [('Boolean', 'true')])
    test("false", [('Boolean', 'false')])
    test("/x", [('Binder', '/x')])
    test("/x-y_2", [('Binder', '/x-y_2')])
    test("x", [('Identifier', 'x')])
    test("x-y_2", [('Identifier', 'x-y_2')])
    test("addi", [('Operator', 'addi')])
    test("[1 2]", [('Array', [('Integer', '1'), ('Integer', '2')])])
    test("{1 2}", [('Function', [('Integer', '1'), ('Integer', '2')])])
    test("{1 [2 3]}", [('Function', [('Integer', '1'), ('Array', [('Integer', '2'), ('Integer', '3')])])])

    
