import os 
import ast 
import logging as lg
from pathlib import Path
from .extractor import FunctionCallExtractor

def extract_call_relations(filepath: str):
    lg.info("Extracting call-relations")
    source = Path(filepath).read_text(encoding="utf-8")
    tree = ast.parse(source)

    call_relations = {}  # {called_function: [caller_function1, caller_function2]}

    def _scan_func(caller_name, func_node):
        extractor = FunctionCallExtractor()
        extractor.visit(func_node)
        for called_func in extractor.calls:
            call_relations.setdefault(called_func, []).append({
                "caller": caller_name,
                "file": os.path.basename(filepath)
            })

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            _scan_func(node.name, node)
        elif isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    _scan_func(f"{node.name}.{item.name}", item)

    return call_relations