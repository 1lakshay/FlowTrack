"""function file to read and parse the AST of it"""

import logging as lg
import ast

def funct2():
    d = 10+2
    return d

tri = 2+9

def func1():
    a = 10 + 3 + 86
    lg.info("this is the logging information")
    print("another print")
    print("another something")
    c = a - funct2()
    print(f"something")
    return c 