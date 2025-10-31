import ast
import logging as lg
with open('code_to_parse.py', 'r') as f:
    tree = ast.parse(f.read())

print(f"tree = {tree}")

print(f"some = {ast.dump(tree, indent=4)}")
print(f"type = {type(ast.dump(tree, indent=4))}")
