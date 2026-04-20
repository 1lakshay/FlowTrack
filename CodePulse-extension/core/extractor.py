import ast

class FunctionCallExtractor(ast.NodeVisitor):
    def __init__(self):
        self.calls = set()

    def visit_Call(self, node):
        # Simple call: funct2()
        if isinstance(node.func, ast.Name):
            self.calls.add(node.func.id)
        # Method call: obj.some_method()
        elif isinstance(node.func, ast.Attribute):
            attr = node.func.attr
            if isinstance(node.func.value, ast.Name):
                self.calls.add(f"{node.func.value.id}.{attr}")
            else:
                self.calls.add(attr)
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
