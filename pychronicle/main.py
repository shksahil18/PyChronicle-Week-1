from pychronicle.ast_parser import find_assignments
from pychronicle.storage import create_table, save_assignment


TARGET_FILE = "sample_target.py"


def main() -> None:
    try:
        create_table()
        assignments = find_assignments(TARGET_FILE)

        if not assignments:
            print("No variable assignments found.")
            return

        print("\nDetected variable assignments")
        print("-" * 50)

        for assignment in assignments:
            line_number = assignment["line_number"]
            variable_name = assignment["variable_name"]
            serialized_value = assignment["serialized_value"]

            print(
                f"Line {line_number}: "
                f"{variable_name} = {serialized_value}"
            )

            save_assignment(
                line_number=line_number,
                variable_name=variable_name,
                serialized_value=serialized_value,
            )

        print("-" * 50)
        print(f"Saved {len(assignments)} assignments to SQLite.")

    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")
    except Exception as error:
        print(f"Unexpected error: {error}")


if __name__ == "__main__":
    main()


