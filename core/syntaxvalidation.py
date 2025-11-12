from pathlib import Path
import ast

def is_syntax_valid(filepath: str) -> bool:
    """Return True if the file can be parsed by Python."""
    try:
        source = Path(filepath).read_text(encoding="utf-8")
        ast.parse(source)
        return True
    except SyntaxError:
        return False