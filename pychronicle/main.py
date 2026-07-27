from pychronicle.ast_parser import find_assignments
from pychronicle.storage import create_table, save_assignment
from pychronicle.tracer import ExecutionTracer


TARGET_FILE = "sample_target.py"


def main():

    print("=" * 60)
    print("PyChronicle - Week 1 + Week 2")
    print("=" * 60)

    create_table()

    print("\nSTEP 1 : AST Parsing")
    print("-" * 40)

    assignments = find_assignments(TARGET_FILE)

    for assignment in assignments:

        print(
            f"Line {assignment['line_number']} : "
            f"{assignment['variable_name']} = "
            f"{assignment['serialized_value']}"
        )

        save_assignment(
            assignment["line_number"],
            assignment["variable_name"],
            assignment["serialized_value"],
        )

    print(f"\nSaved {len(assignments)} assignments.\n")

    print("=" * 60)
    print("STEP 2 : Runtime Tracing")
    print("=" * 60)

    tracer = ExecutionTracer(TARGET_FILE)

    tracer.run(TARGET_FILE)

    print("\nTracing Finished.")


if __name__ == "__main__":
    main()
