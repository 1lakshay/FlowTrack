import ast, hashlib
from pathlib import Path
from .extractor import LogicNormalizer
from typing import Dict
import logging as lg

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
