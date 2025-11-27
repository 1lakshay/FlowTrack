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

    filename = Path(filepath).name

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            caller_name = node.name
            extractor = FunctionCallExtractor()
            extractor.visit(node)

            for called_func in extractor.calls:
                call_relations.setdefault(called_func, []).append({
                    "caller": caller_name,
                    "file": os.path.basename(filepath)
                })

    # for node in tree.body:
    #     if isinstance(node, ast.FunctionDef):
    #         caller_name = node.name
    #         extractor = FunctionCallExtractor()
    #         extractor.visit(node)

    #         for called_func in extractor.calls:
    #             entry = {"file": filename, "function": caller_name}
    #             call_relations.setdefault(called_func, []).append(caller_name)

    return call_relations