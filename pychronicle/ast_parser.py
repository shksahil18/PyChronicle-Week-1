import ast
from pathlib import Path


def find_assignments(file_path: str) -> list[dict]:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Target file not found: {path}")

    try:
        source_code = path.read_text(encoding="utf-8")
        tree = ast.parse(source_code, filename=str(path))
    except SyntaxError as error:
        raise ValueError(
            f"Invalid Python syntax at line {error.lineno}: {error.msg}"
        ) from error

    assignments = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assignments.append(
                        {
                            "line_number": node.lineno,
                            "variable_name": target.id,
                            "serialized_value": ast.unparse(node.value),
                        }
                    )

    return sorted(assignments, key=lambda item: item["line_number"])