import ast


def find_assignments(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        source_code = file.read()

    tree = ast.parse(source_code)

    assignments = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assignments.append({
                        "line_number": node.lineno,
                        "variable_name": target.id,
                        "value_type": type(node.value).__name__
                    })

    return assignments