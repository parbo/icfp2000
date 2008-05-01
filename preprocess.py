#!/bin/python
import subprocess

def preprocess(filename):
    cmd = "gcc -E -x c -P %s"%filename
    return subprocess.Popen(cmd.split(), stdout=subprocess.PIPE).stdout.read()

if __name__=="__main__":
    import sys
    print preprocess(sys.argv[1])
    
