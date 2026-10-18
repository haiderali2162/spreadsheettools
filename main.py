from core.file_manager import FileManager
from operations.search import SearchOperation
from operations.filter import FilterOperation
from operations.sort import SortOperation
from operations.calculations import CalculationOperation
from operations.export_manager import ExportManager
from operations.duplicates import DuplicateOperation
from operations.columns import ColumnOperation


APP_NAME = "Spreadsheet Data Tool"
APP_VERSION = "0.2.0"


def print_header():

    print()
    print("=" * 60)
    print(f"        {APP_NAME}")
    print(f"        Version {APP_VERSION}")
    print("=" * 60)
    print()


def print_dataset_info(dataset):

    print()
    print("-" * 60)
    print("DATASET INFORMATION")
    print("-" * 60)

    print(f"File       : {dataset.source_file}")
    print(f"Rows       : {dataset.row_count}")
    print(f"Columns    : {dataset.column_count}")

    if dataset.sheet_name:
        print(f"Sheet      : {dataset.sheet_name}")

    print()
    print("Columns:")

    for index, column in enumerate(
        dataset.columns,
        start=1
    ):
        print(f"  {index:>3}. {column}")

    print("-" * 60)


def print_preview(dataset, rows=10):

    print()
    print("-" * 60)
    print(f"FIRST {rows} RECORDS")
    print("-" * 60)

    if dataset.row_count == 0:
        print("No records found.")

    else:
        print(
            dataset.preview(rows).to_string(
                index=False
            )
        )

    print("-" * 60)


def select_file():

    while True:

        file_path = input(
            "\nEnter spreadsheet file path: "
        ).strip().strip('"')

        if not file_path:
            print("Please enter a file path.")
            continue

        try:
            return FileManager.validate_file(
                file_path
            )

        except Exception as error:
            print(f"\nError: {error}")


def select_sheet(file_path):

    sheets = FileManager.get_sheets(
        file_path
    )

    if len(sheets) == 1:
        return sheets[0]

    print()
    print("Available sheets:")
    print()

    for index, sheet in enumerate(
        sheets,
        start=1
    ):
        print(f"{index}. {sheet}")

    while True:

        choice = input(
            "\nSelect sheet number: "
        ).strip()

        try:

            number = int(choice)

            if 1 <= number <= len(sheets):
                return sheets[number - 1]

            print("Invalid sheet number.")

        except ValueError:
            print("Please enter a number.")


def load_dataset():

    file_path = select_file()

    extension = file_path.suffix.lower()

    if extension in {
        ".xlsx",
        ".xls",
        ".ods",
        ".xlsb"
    }:

        sheet_name = select_sheet(
            file_path
        )

        print(
            f"\nLoading sheet: {sheet_name}"
        )

        dataset = FileManager.read_file(
            file_path,
            sheet_name=sheet_name
        )

    else:

        print("\nLoading file...")

        dataset = FileManager.read_file(
            file_path
        )

    print("\nFile loaded successfully.")

    return dataset


def select_column(dataset):

    print()
    print("Available columns:")
    print()

    for index, column in enumerate(
        dataset.columns,
        start=1
    ):
        print(f"{index}. {column}")

    while True:

        choice = input(
            "\nSelect column number: "
        ).strip()

        try:

            number = int(choice)

            if 1 <= number <= dataset.column_count:
                return dataset.columns[
                    number - 1
                ]

            print("Invalid column number.")

        except ValueError:
            print("Please enter a number.")


def search_menu(dataset):

    print()
    print("=" * 60)
    print("SEARCH")
    print("=" * 60)

    column = select_column(dataset)

    value = input(
        "\nSearch value: "
    )

    print()
    print("Search mode:")
    print("1. Contains")
    print("2. Exact")
    print("3. Starts with")
    print("4. Ends with")

    mode_choice = input(
        "\nSelect mode [1]: "
    ).strip()

    modes = {
        "1": "contains",
        "2": "exact",
        "3": "starts_with",
        "4": "ends_with"
    }

    mode = modes.get(
        mode_choice,
        "contains"
    )

    result = SearchOperation.search(
        dataset,
        column,
        value,
        mode
    )

    print(
        f"\nFound {result.row_count} matching "
        f"record(s)."
    )

    print_preview(result, 10)

    return result


def get_operator():

    print()
    print("Operators:")
    print()
    print("1. =")
    print("2. !=")
    print("3. >")
    print("4. <")
    print("5. >=")
    print("6. <=")
    print("7. contains")
    print("8. not contains")
    print("9. starts with")
    print("10. ends with")
    print("11. is blank")
    print("12. is not blank")
    print("13. between")
    print("14. in")
    print("15. not in")

    operators = {
        "1": "=",
        "2": "!=",
        "3": ">",
        "4": "<",
        "5": ">=",
        "6": "<=",
        "7": "contains",
        "8": "not_contains",
        "9": "starts_with",
        "10": "ends_with",
        "11": "is_blank",
        "12": "is_not_blank",
        "13": "between",
        "14": "in",
        "15": "not_in"
    }

    while True:

        choice = input(
            "\nSelect operator: "
        ).strip()

        if choice in operators:
            return operators[choice]

        print("Invalid operator.")


def get_condition(dataset):

    column = select_column(dataset)

    operator = get_operator()

    value = None

    if operator not in {
        "is_blank",
        "is_not_blank"
    }:

        if operator == "between":

            first = input(
                "Minimum value: "
            ).strip()

            second = input(
                "Maximum value: "
            ).strip()

            value = [
                convert_value(first),
                convert_value(second)
            ]

        elif operator in {
            "in",
            "not_in"
        }:

            raw = input(
                "Enter values separated by commas: "
            )

            value = [
                convert_value(item.strip())
                for item in raw.split(",")
            ]

        else:

            raw = input(
                "Comparison value: "
            ).strip()

            value = convert_value(raw)

    return {
        "column": column,
        "operator": operator,
        "value": value
    }


def convert_value(value):

    if value == "":
        return value

    # Integer
    try:
        return int(value)
    except ValueError:
        pass

    # Float
    try:
        return float(value)
    except ValueError:
        pass

    return value


def filter_menu(dataset):

    print()
    print("=" * 60)
    print("FILTER")
    print("=" * 60)

    print()
    print("How many conditions?")
    
    while True:

        try:
            count = int(
                input(
                    "Number of conditions: "
                )
            )

            if count >= 1:
                break

            print(
                "Enter at least one condition."
            )

        except ValueError:
            print("Enter a valid number.")

    conditions = []

    for index in range(count):

        print()
        print(
            f"--- Condition {index + 1} ---"
        )

        conditions.append(
            get_condition(dataset)
        )

    logic = "AND"

    if count > 1:

        print()
        print("Combine conditions using:")
        print("1. AND")
        print("2. OR")

        logic_choice = input(
            "\nSelect [1]: "
        ).strip()

        if logic_choice == "2":
            logic = "OR"

    result = FilterOperation.filter_multiple(
        dataset,
        conditions,
        logic
    )

    print()
    print(
        f"Filter returned {result.row_count} "
        f"record(s)."
    )

    print_preview(result, 10)

    return result


def sort_menu(dataset):

    print()
    print("=" * 60)
    print("SORT")
    print("=" * 60)

    print()
    print("How many sort columns?")

    while True:

        try:

            count = int(
                input(
                    "Number of columns [1]: "
                ) or "1"
            )

            if count >= 1:
                break

            print("Enter at least one column.")

        except ValueError:
            print("Enter a valid number.")

    columns = []
    directions = []

    for index in range(count):

        print()
        print(
            f"--- Sort level {index + 1} ---"
        )

        column = select_column(dataset)

        print()
        print("1. Ascending")
        print("2. Descending")

        direction = input(
            "Select [1]: "
        ).strip()

        ascending = direction != "2"

        columns.append(column)
        directions.append(ascending)

    result = SortOperation.sort_multiple(
        dataset,
        columns,
        directions
    )

    print("\nSorting completed.")

    print_preview(result, 10)

    return result



def calculation_menu(dataset):
    """Interactive menu for basic and conditional calculations."""

    options = {
        "1": ("Sum", "sum"),
        "2": ("Average", "average"),
        "3": ("Minimum", "min"),
        "4": ("Maximum", "max"),
        "5": ("Count records", "count"),
        "6": ("Count non-empty cells", "count_non_empty"),
        "7": ("Count unique values", "count_unique"),
        "8": ("Median", "median"),
    }

    print("\n" + "=" * 50)
    print("CALCULATIONS")
    print("=" * 50)

    for key, (label, _) in options.items():
        print(f"{key}. {label}")

    print("9. Conditional calculation")

    choice = input("\nSelect calculation: ").strip()

    if choice not in options and choice != "9":
        print("Invalid selection.")
        return

    if choice == "9":
        print("\nChoose the calculation to perform:")
        print("1. Sum")
        print("2. Average")
        print("3. Count records")
        print("4. Count unique values")

        sub_choice = input("Select: ").strip()

        conditional_options = {
            "1": "sum",
            "2": "average",
            "3": "count",
            "4": "count_unique",
        }

        if sub_choice not in conditional_options:
            print("Invalid selection.")
            return

        operation = conditional_options[sub_choice]

        target_column = None
        if operation != "count":
            target_column = select_column(dataset)

        condition_count = int(
            input("Number of conditions [1]: ") or "1"
        )

        if condition_count < 1:
            print("At least one condition is required.")
            return

        conditions = []

        for index in range(condition_count):
            print(f"\nCondition {index + 1}")
            conditions.append(get_condition(dataset))

        logic = "AND"

        if condition_count > 1:
            logic_choice = input(
                "Combine with AND or OR [AND]: "
            ).strip().upper()

            if logic_choice in {"AND", "OR"}:
                logic = logic_choice

        result = CalculationOperation.conditional_calculate(
            dataset,
            operation,
            target_column,
            conditions,
            logic,
        )

    else:
        label, operation = options[choice]

        if operation == "count":
            target_column = None
        else:
            target_column = select_column(dataset)

        result = CalculationOperation.calculate(
            dataset,
            operation,
            target_column,
        )

    print("\nCalculation result")
    print("-" * 40)
    print(f"Result: {result}")
    print("-" * 40)


def group_summary_menu(dataset):
    """Create a grouped summary dataset."""

    print("\n" + "=" * 50)
    print("GROUP SUMMARY")
    print("=" * 50)

    group_count = int(
        input("Number of grouping columns [1]: ") or "1"
    )

    if group_count < 1:
        print("Select at least one grouping column.")
        return None

    group_columns = []

    for index in range(group_count):
        print(f"\nGrouping column {index + 1}")
        group_columns.append(select_column(dataset))

    aggregation_count = int(
        input("\nNumber of calculations [1]: ") or "1"
    )

    if aggregation_count < 1:
        print("Select at least one calculation.")
        return None

    aggregations = {}

    allowed_operations = {
        "1": "sum",
        "2": "mean",
        "3": "min",
        "4": "max",
        "5": "count",
        "6": "nunique",
        "7": "median",
    }

    for index in range(aggregation_count):
        print(f"\nCalculation {index + 1}")
        column = select_column(dataset)

        print(
            "1. Sum\n"
            "2. Average\n"
            "3. Minimum\n"
            "4. Maximum\n"
            "5. Count non-empty values\n"
            "6. Count unique values\n"
            "7. Median"
        )

        operation_choice = input("Select: ").strip()

        if operation_choice not in allowed_operations:
            print("Invalid calculation.")
            return None

        operation = allowed_operations[operation_choice]

        aggregations.setdefault(column, []).append(operation)

    result = CalculationOperation.group_summary(
        dataset,
        group_columns,
        aggregations,
    )

    print(f"\nCreated {result.row_count} summary row(s).")
    print_preview(result, 20)

    return result


def export_menu(dataset):
    """Export the current dataset to a new file."""

    print("\n" + "=" * 50)
    print("EXPORT RESULTS")
    print("=" * 50)

    print("1. Excel (.xlsx)")
    print("2. OpenDocument (.ods)")
    print("3. CSV (.csv)")
    print("4. TSV (.tsv)")

    formats = {
        "1": "xlsx",
        "2": "ods",
        "3": "csv",
        "4": "tsv",
    }

    choice = input("\nSelect output format: ").strip()

    if choice not in formats:
        print("Invalid selection.")
        return

    prefix = input(
        "Output filename prefix [original filename]: "
    ).strip()

    try:
        output_path = ExportManager.export(
            dataset,
            output_format=formats[choice],
            output_directory="output",
            filename_prefix=prefix or None,
        )

        print("\nExport completed.")
        print(f"Saved to: {output_path.resolve()}")
        print(f"Records exported: {dataset.row_count}")

    except Exception as error:
        print(f"\nExport failed: {error}")



# ================ 0.4.0 ================

def select_columns(dataset):
    print("\nAvailable columns:")

    for index, column in enumerate(dataset.columns, start=1):
        print(f"{index}. {column}")

    raw = input(
        "\nEnter column numbers separated by commas: "
    ).strip()

    try:
        indexes = [int(item.strip()) for item in raw.split(",")]
    except ValueError:
        print("Please enter valid column numbers.")
        return None

    if not indexes:
        print("No columns selected.")
        return None

    if any(index < 1 or index > len(dataset.columns) for index in indexes):
        print("One or more column numbers are invalid.")
        return None

    selected = [dataset.columns[index - 1] for index in indexes]

    # Remove repeated selections but preserve the chosen order.
    return list(dict.fromkeys(selected))


def duplicate_menu(dataset):
    print("\n--- Duplicate Operations ---")
    print("1. Find all rows that have duplicates")
    print("2. Find duplicate occurrences after the first")
    print("3. Remove duplicates and keep the first")
    print("4. Remove duplicates and keep the last")
    print("5. Keep the row with the highest value")
    print("6. Keep the row with the lowest value")
    print("0. Cancel")

    choice = input("\nChoose an option: ").strip()

    if choice == "0":
        return None

    if choice not in {"1", "2", "3", "4", "5", "6"}:
        print("Invalid option.")
        return None

    print(
        "\nChoose columns used to identify duplicates."
        "\nFor the entire row, enter all column numbers."
    )
    columns = select_columns(dataset)

    if not columns:
        return None

    if choice == "1":
        result = DuplicateOperation.find_duplicates(
            dataset, columns, keep="all"
        )
    elif choice == "2":
        result = DuplicateOperation.find_duplicates(
            dataset, columns, keep="first"
        )
    elif choice == "3":
        result = DuplicateOperation.remove_duplicates(
            dataset, columns, keep="first"
        )
    elif choice == "4":
        result = DuplicateOperation.remove_duplicates(
            dataset, columns, keep="last"
        )
    else:
        print("\nSelect the column used to determine the highest/lowest value.")
        priority_column = select_column(dataset)

        if priority_column is None or priority_column in columns:
            print("Choose a priority column not used to identify duplicates.")
            return None

        result = DuplicateOperation.keep_highest_or_lowest(
            dataset,
            duplicate_columns=columns,
            priority_column=priority_column,
            highest=(choice == "5"),
        )

    print(f"\nRows before operation: {len(dataset.dataframe)}")
    print(f"Rows after operation:  {len(result.dataframe)}")
    print(result.preview(10).to_string(index=False))

    use_result = input(
        "\nUse this result as the current dataset? (y/n): "
    ).strip().lower()

    return result if use_result == "y" else None


def column_menu(dataset):
    print("\n--- Column Operations ---")
    print("1. Rename a column")
    print("2. Copy a column")
    print("3. Delete columns")
    print("4. Move selected columns to the beginning")
    print("5. Trim spaces from text")
    print("6. Replace values")
    print("7. Add serial numbers")
    print("8. Compare two columns")
    print("9. Subtract one column from another")
    print("0. Cancel")

    choice = input("\nChoose an option: ").strip()

    if choice == "0":
        return None

    if choice == "1":
        old_name = select_column(dataset)
        if old_name is None:
            return None

        new_name = input("Enter the new column name: ")
        result = ColumnOperation.rename_column(
            dataset, old_name, new_name
        )

    elif choice == "2":
        source = select_column(dataset)
        if source is None:
            return None

        new_name = input("Enter the name for the copied column: ")
        result = ColumnOperation.copy_column(
            dataset, source, new_name
        )

    elif choice == "3":
        columns = select_columns(dataset)
        if not columns:
            return None

        confirm = input(
            f"Delete these columns {columns}? (y/n): "
        ).strip().lower()

        if confirm != "y":
            return None

        result = ColumnOperation.delete_columns(dataset, columns)

    elif choice == "4":
        columns = select_columns(dataset)
        if not columns:
            return None

        result = ColumnOperation.move_columns_first(dataset, columns)

    elif choice == "5":
        print("1. Trim all text columns")
        print("2. Select specific columns")
        trim_choice = input("Choose an option: ").strip()

        if trim_choice == "1":
            result = ColumnOperation.trim_text(dataset)
        elif trim_choice == "2":
            columns = select_columns(dataset)
            if not columns:
                return None
            result = ColumnOperation.trim_text(dataset, columns)
        else:
            print("Invalid option.")
            return None

    elif choice == "6":
        column = select_column(dataset)
        if column is None:
            return None

        old_value = input("Value to find: ")
        new_value = input("Replace it with: ")

        partial = input(
            "Replace part of text rather than the entire cell? (y/n): "
        ).strip().lower() == "y"

        case_sensitive = input(
            "Case-sensitive replacement? (y/n): "
        ).strip().lower() == "y"

        result = ColumnOperation.replace_values(
            dataset,
            column,
            old_value,
            new_value,
            partial=partial,
            case_sensitive=case_sensitive,
        )

    elif choice == "7":
        name = input(
            "Serial column name (press Enter for Serial): "
        ).strip() or "Serial"

        raw_start = input(
            "Starting number (press Enter for 1): "
        ).strip()

        try:
            start = int(raw_start) if raw_start else 1
        except ValueError:
            print("Starting number must be a whole number.")
            return None

        result = ColumnOperation.add_serial_numbers(
            dataset, column_name=name, start=start
        )

    elif choice == "8":
        left = select_column(dataset)
        if left is None:
            return None

        right = select_column(dataset)
        if right is None:
            return None

        print("Operators: ==, !=, >, <, >=, <=")
        operator = input("Enter comparison operator: ").strip()

        print("1. Return matching rows")
        print("2. Add a new column containing True/False")
        compare_choice = input("Choose an option: ").strip()

        if compare_choice == "2":
            result_name = input("Name for the result column: ").strip()
        elif compare_choice == "1":
            result_name = None
        else:
            print("Invalid option.")
            return None

        result = ColumnOperation.compare_columns(
            dataset,
            left,
            operator,
            right,
            result_column=result_name,
        )

    elif choice == "9":
        left = select_column(dataset)
        if left is None:
            return None

        right = select_column(dataset)
        if right is None:
            return None

        result_name = input("Name for the difference column: ").strip()

        result = ColumnOperation.subtract_columns(
            dataset, left, right, result_name
        )

    else:
        print("Invalid option.")
        return None

    print(f"\nResult: {len(result.dataframe)} rows, "
          f"{len(result.dataframe.columns)} columns")
    print(result.preview(10).to_string(index=False))

    use_result = input(
        "\nUse this result as the current dataset? (y/n): "
    ).strip().lower()

    return result if use_result == "y" else None





def main_menu():

    original_dataset = None
    dataset = None

    while True:

        print()
        print("=" * 60)
        print("MAIN MENU")
        print("=" * 60)

        if dataset:

            print(
                f"Loaded: {dataset.source_file.name}"
                f" ({dataset.row_count} rows)"
            )

        else:

            print("No file loaded.")

        print()
        print("1. Load spreadsheet")
        print("2. View dataset information")
        print("3. Preview records")
        print("4. Find records")
        print("5. Filter records")
        print("6. Sort records")
        # print("7. Exit")
        print("8. Calculations")
        print("9. Group summary")
        print("10. Export current results")
        print("11. Return to original dataset")
        print("13. Duplicate operations")
        print("14. Column operations")
        print("12. Exit")
        print()

        choice = input(
            "Select operation: "
        ).strip()

        if choice == "1":


            try:
                original_dataset = load_dataset()
                dataset = original_dataset.copy()

            except Exception as error:
                print(f"\nFailed to load file: {error}")

            # try:

            #     dataset = load_dataset()

            # except Exception as error:

            #     print()
            #     print(
            #         f"Failed to load file: {error}"
            #     )

        elif choice == "2":

            if dataset is None:

                print(
                    "\nPlease load a file first."
                )
                continue

            print_dataset_info(dataset)

        elif choice == "3":

            if dataset is None:

                print(
                    "\nPlease load a file first."
                )
                continue

            value = input(
                "\nNumber of records to preview [10]: "
            ).strip()

            if value == "":
                rows = 10

            else:

                try:
                    rows = int(value)

                except ValueError:

                    print("Invalid number.")
                    continue

            print_preview(
                dataset,
                rows
            )

        elif choice == "4":

            if dataset is None:

                print(
                    "\nPlease load a file first."
                )
                continue

            # result = search_menu(dataset)

            # ask_replace_dataset(
            #     result,
            #     globals()
            # )

            result = search_menu(dataset)

            # Temporary behavior:
            # search result becomes current dataset
            dataset = result

        elif choice == "5":

            if dataset is None:

                print(
                    "\nPlease load a file first."
                )
                continue

            result = filter_menu(dataset)

            dataset = result

        elif choice == "6":

            if dataset is None:

                print(
                    "\nPlease load a file first."
                )
                continue

            result = sort_menu(dataset)

            dataset = result

        # elif choice == "7":

        #     print("\nGoodbye!")
        #     break

        elif choice == "8":
            if dataset is None:
                print("Please load a file first.")
                continue

            calculation_menu(dataset)

        elif choice == "9":
            if dataset is None:
                print("Please load a file first.")
                continue

            try:
                result = group_summary_menu(dataset)

                if result is not None:
                    use_result = input(
                        "\nUse this summary as the current dataset? (y/n): "
                    ).strip().lower()

                    if use_result == "y":
                        dataset = result

            except Exception as error:
                print(f"Group summary failed: {error}")

        elif choice == "10":
            if dataset is None:
                print("Please load a file first.")
                continue

            export_menu(dataset)

        elif choice == "11":
            if original_dataset is None:
                print("Please load a file first.")
                continue

            dataset = original_dataset.copy()
            print("Returned to the original dataset.")

        elif choice == "12":
            print("Goodbye!")
            break

        elif choice == "13":
            if dataset is None:
                print("Please load a file first.")
                continue

            try:
                result = duplicate_menu(dataset)
                if result is not None:
                    dataset = result
                    print("Current dataset updated.")
            except Exception as error:
                print(f"Duplicate operation failed: {error}")

        elif choice == "14":
            if dataset is None:
                print("Please load a file first.")
                continue

            try:
                result = column_menu(dataset)
                if result is not None:
                    dataset = result
                    print("Current dataset updated.")
            except Exception as error:
                print(f"Column operation failed: {error}")

        else:

            print("\nInvalid selection.")


# def ask_replace_dataset(result, context=None):
#     """
#     Placeholder for the future operation-history system.

#     For Part 2 the result is automatically used
#     as the current dataset.
#     """

#     return True


def main():

    print_header()

    try:

        main_menu()

    except KeyboardInterrupt:

        print("\n\nApplication closed.")


if __name__ == "__main__":
    main()