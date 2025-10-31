import os 
import ast
import hashlib
import json
from pathlib import Path
from typing import Dict
import logging as lg 
from dotenv import load_dotenv

load_dotenv()

lg.basicConfig(level=lg.INFO, format="%(levelname)s: %(message)s")

FUNCTION_HASH_FILE_NAME = os.getenv("FUNCTION_HASH_FILE_NAME")
FUNCTION_CALLING_RECORD = os.getenv("FUNCTION_CALLING_RECORD")

functions_that_are_changed = []
notify_about_function_behaviour = []

class FunctionCallExtractor(ast.NodeVisitor):
    def __init__(self):
        self.calls = set()

    def visit_Call(self, node):
        # Check if the function being called is a simple name like foo()
        if isinstance(node.func, ast.Name):
            self.calls.add(node.func.id)
        self.generic_visit(node)

class LogicNormalizer(ast.NodeTransformer):
    """Remove cosmetic or debug statements before hashing."""

    def visit_Expr(self, node):
        # Remove print() and logging statements
        if isinstance(node.value, ast.Call):
            func = node.value.func
            if isinstance(func, ast.Name) and func.id in {"print", "logger", "logging"}:
                return None
        return self.generic_visit(node)

    def visit_Constant(self, node):
        # Replace literal constants with placeholders
        if isinstance(node.value, (str, int, float, bool, complex)):
            return ast.copy_location(ast.Constant(value=None), node)
        return node

def extract_call_relations(filepath: str):
    lg.info("Extracting call-relations")
    source = Path(filepath).read_text(encoding="utf-8")
    tree = ast.parse(source)

    call_relations = {}  # {called_function: [caller_function1, caller_function2]}

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            caller_name = node.name
            extractor = FunctionCallExtractor()
            extractor.visit(node)

            for called_func in extractor.calls:
                call_relations.setdefault(called_func, []).append(caller_name)

    return call_relations

def get_function_hashes(filepath: str) -> Dict:
    """Return a dict of {function_name: logic_hash} for a Python file."""
    lg.info(f"Extracting function hashing")
    source = Path(filepath).read_text(encoding="utf-8")
    tree = ast.parse(source)
    normalizer = LogicNormalizer()
    hashes = {}

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            # normalize function AST (ignore print/log/constants)
            clean_func = normalizer.visit(ast.fix_missing_locations(node))
            ast_repr = ast.dump(clean_func, include_attributes=False)
            func_hash = hashlib.sha256(ast_repr.encode()).hexdigest()
            hashes[node.name] = func_hash

    return hashes


if __name__ == "__main__":
    file_path = "code_to_parse.py"   
    result = get_function_hashes(file_path)
    if not os.path.exists(FUNCTION_HASH_FILE_NAME):
        lg.info("creating the new function hash file")
        output_path_for_hash = Path(FUNCTION_HASH_FILE_NAME)
        output_path_for_hash.write_text(json.dumps(result, indent=4))
        print(f"✅ Hashes saved to {output_path_for_hash.resolve()}")
    else:
        # - here their is no Logic of reading the currently made file as their will be no back version for comparison
        # - when the hash funciton is already present, then checking if the hash is changed, if yes the do overwrite & if not present then 
        #   do make a entry of it
        lg.info("reading the pre-made function hash file")
        extr_result = json.loads(Path(FUNCTION_HASH_FILE_NAME).read_text())
        for key,val in result.items():
            if key in extr_result:
                lg.info("pre-made function hash is being found")
                if val != extr_result[key]:
                    lg.info("function is being changed, hence updating")
                    functions_that_are_changed.append(key)
                    extr_result[key] = val
                else:
                    pass
            else:
                lg.info("function hash is not found, hence adding it in function's hash-file")
                extr_result[key] = val

        # - writing file 
        Path(FUNCTION_HASH_FILE_NAME).write_text(json.dumps(extr_result, indent=4))

    print(json.dumps(result, indent=4))

    call_relations = extract_call_relations(file_path)
    if not os.path.exists(FUNCTION_HASH_FILE_NAME):
        output_path_for_calling = Path(FUNCTION_CALLING_RECORD)
        output_path_for_calling.write_text(json.dumps(call_relations, indent=4))
        print(f"✅ Call relations saved to {output_path_for_calling.resolve()}")
    
    # - read this file no matter if it is bening created or not, as this don't matter like in the function hash files, 
    if len(functions_that_are_changed) > 0:    
        lg.info("some funcitons logic are being changed")
        for function in functions_that_are_changed:
            print(f"function = {function}")
            val_found = call_relations.get(function, [])
            if val_found:
                print(f"inside = {val_found}")
                for i in val_found:
                    notify_about_function_behaviour.append(i)
            else:
                pass

    print(json.dumps(call_relations, indent=4))

print(f"functions_that_are_changed = {functions_that_are_changed}")
print(f"notify_about_function_behaviour = {notify_about_function_behaviour}")
