import sys,io
from lexer import *

__VERSION__ = 'v0.1'

if len(sys.argv)!=2:
    sys.exit('Usage: run.py test.bp')
try:
    f = open(sys.argv[1], 'r')
    tokens = Lexer().tokenize(f.read())
    for x in tokens:
        print(x)
except Exception as e:
    print(e)

print(Token.dic)