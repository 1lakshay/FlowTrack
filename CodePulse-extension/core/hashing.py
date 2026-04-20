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

    def _hash_func(name, func_node):
        clean_func = normalizer.visit(ast.fix_missing_locations(func_node))
        ast_repr = ast.dump(clean_func, include_attributes=False)
        hashes[name] = hashlib.sha256(ast_repr.encode()).hexdigest()

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            _hash_func(node.name, node)
        elif isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    _hash_func(f"{node.name}.{item.name}", item)

    return hashes
