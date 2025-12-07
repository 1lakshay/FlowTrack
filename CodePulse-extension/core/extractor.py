import ast

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
