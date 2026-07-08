from pychronicle.ast_parser import find_assignments
from pychronicle.storage import create_table, save_assignment


def main():
    target_file = "sample_target.py"

    create_table()

    assignments = find_assignments(target_file)

    print("Detected Variable Assignments:")
    print("-" * 40)

    for item in assignments:
        line_number = item["line_number"]
        variable_name = item["variable_name"]
        value_type = item["value_type"]

        print(f"Line {line_number}: {variable_name} = {value_type}")

        save_assignment(
            line_number=line_number,
            variable_name=variable_name,
            serialized_value=value_type
        )

    print("-" * 40)
    print("Assignments saved into SQLite database.")


if __name__ == "__main__":
    main()