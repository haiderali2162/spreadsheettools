from core.file_manager import FileManager
from operations.search import SearchOperation
from operations.filter import FilterOperation
from operations.sort import SortOperation
from operations.calculations import CalculationOperation
from operations.export_manager import ExportManager
from operations.duplicates import DuplicateOperation
from operations.columns import ColumnOperation
from operations.land_area import LandAreaOperation
from operations.reports import ReportOperation
from operations.text_cleaning import TextCleaningOperation
from operations.validation import ValidationOperation
from operations.safe_correction import SafeCorrectionOperation
from core.history_manager import HistoryManager


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



# ================ part 5 ============================

def get_sqft_standard():
    print("\nSquare feet per Marla:")
    print("1. 272 square feet (default)")
    print("2. 225 square feet")

    choice = input("Choose standard (press Enter for 272): ").strip()

    if choice in {"", "1"}:
        return 272
    if choice == "2":
        return 225

    raise ValueError("Choose 1 or 2.")


def land_area_menu(dataset):
    print("\n--- Land Area Operations ---")
    print("1. Convert K-M-F to square feet")
    print("2. Convert square feet to K-M-F")
    print("3. Add multiple land areas")
    print("4. Subtract one land area from another")
    print("5. Calculate an ownership share")
    print("6. Add area conversion columns to the dataset")
    print("7. Calculate share areas in the dataset")
    print("0. Cancel")

    choice = input("\nChoose an option: ").strip()

    if choice == "0":
        return None

    if choice not in {"1", "2", "3", "4", "5", "6", "7"}:
        print("Invalid option.")
        return None

    sqft_standard = get_sqft_standard()

    if choice == "1":
        area = input("Enter area in K-M-F (example 10-10-0): ")
        result = LandAreaOperation.to_square_feet(
            area, sqft_standard
        )
        print(f"\nTotal square feet: {result}")
        return None

    if choice == "2":
        total = input("Enter total square feet: ")
        result = LandAreaOperation.from_square_feet(
            total, sqft_standard
        )
        print(f"\nArea in K-M-F: {result}")
        return None

    if choice == "3":
        raw_areas = input(
            "Enter areas separated by commas (example 1-0-0,0-10-0): "
        )
        areas = [area.strip() for area in raw_areas.split(",")]

        result = LandAreaOperation.add_areas(
            areas, sqft_standard
        )
        print(f"\nCombined area: {result}")
        return None

    if choice == "4":
        area1 = input("Enter the original area in K-M-F: ")
        area2 = input("Enter the area to subtract in K-M-F: ")

        result = LandAreaOperation.subtract_areas(
            area1, area2, sqft_standard
        )
        print(f"\nRemaining area: {result}")
        return None

    if choice == "5":
        area = input("Enter total area in K-M-F: ")
        share = input("Enter ownership share (example 2/5): ")

        result = LandAreaOperation.calculate_share(
            area, share, sqft_standard
        )
        print(f"\nShare area: {result}")
        return None

    if choice == "6":
        source_column = select_column(dataset)
        if source_column is None:
            return None

        sqft_column = input(
            "Name for square-feet column (default Area_SqFt): "
        ).strip() or "Area_SqFt"

        kmf_column = input(
            "Name for normalized K-M-F column (default Area_KMF): "
        ).strip() or "Area_KMF"

        result = LandAreaOperation.add_area_columns(
            dataset,
            source_column=source_column,
            sqft_column=sqft_column,
            normalized_column=kmf_column,
            sqft_per_marla=sqft_standard,
        )

    else:
        print("\nSelect the column containing total area in K-M-F.")
        area_column = select_column(dataset)
        if area_column is None:
            return None

        print("\nSelect the column containing shares, such as 2/5 or 1/3.")
        share_column = select_column(dataset)
        if share_column is None:
            return None

        result_column = input(
            "Name for calculated share area (default Share_Area_KMF): "
        ).strip() or "Share_Area_KMF"

        result = LandAreaOperation.add_share_columns(
            dataset,
            area_column=area_column,
            share_column=share_column,
            result_column=result_column,
            sqft_per_marla=sqft_standard,
        )

    print(f"\nRows: {len(result.dataframe)}")
    print(result.preview(10).to_string(index=False))

    use_result = input(
        "\nUse this result as the current dataset? (y/n): "
    ).strip().lower()

    return result if use_result == "y" else None


# ============== part 6 ==================


def report_menu(dataset):
    print("\n--- Reports and Subtotals ---")
    print("1. Grouped summary")
    print("2. Overall dataset summary")
    print("0. Cancel")

    choice = input("\nChoose an option: ").strip()

    if choice == "0":
        return None

    if choice == "2":
        result = ReportOperation.overall_summary(dataset)

    elif choice == "1":
        print("\nSelect the column(s) used to group records.")
        group_columns = select_columns(dataset)

        if not group_columns:
            return None

        aggregations = {}

        while True:
            add_more = input(
                "\nAdd a calculation for a column? (y/n): "
            ).strip().lower()

            if add_more != "y":
                break

            column = select_column(dataset)
            if column is None:
                continue

            print("\nAvailable calculations:")
            print("1. Sum (numeric columns)")
            print("2. Average (numeric columns)")
            print("3. Minimum")
            print("4. Maximum")
            print("5. Count non-empty values")
            print("6. Count unique values")
            print("7. Median (numeric columns)")

            operation_map = {
                "1": "sum",
                "2": "mean",
                "3": "min",
                "4": "max",
                "5": "count",
                "6": "nunique",
                "7": "median",
            }

            operation_choice = input(
                "Choose calculation: "
            ).strip()

            operation = operation_map.get(operation_choice)

            if operation is None:
                print("Invalid calculation.")
                continue

            aggregations.setdefault(column, []).append(operation)

        result = ReportOperation.group_summary(
            dataset,
            group_columns=group_columns,
            aggregations=aggregations,
            include_record_count=True,
        )

    else:
        print("Invalid option.")
        return None

    print("\n--- Report Preview ---")
    print(f"Report rows: {len(result.dataframe)}")
    print(result.preview(20).to_string(index=False))

    export_now = input(
        "\nExport this report now? (y/n): "
    ).strip().lower()

    if export_now == "y":
        format_choice = input(
            "Format: xlsx, ods, csv, or tsv (default xlsx): "
        ).strip().lower() or "xlsx"

        prefix = input(
            "Report filename prefix (press Enter for default): "
        ).strip() or "property_report"

        try:
            path = ExportManager.export(
                result,
                output_format=format_choice,
                output_directory="output",
                filename_prefix=prefix,
            )
            print(f"\nReport exported to: {path}")
        except Exception as error:
            print(f"Report export failed: {error}")

    use_result = input(
        "\nMake this report the current dataset? (y/n): "
    ).strip().lower()

    return result if use_result == "y" else None


# ============== part 7 ================

def text_cleaning_menu(dataset):
    print("\n--- Text Cleaning and Column Transformations ---")
    print("1. Find and replace across selected columns")
    print("2. Split one column into two")
    print("3. Combine multiple columns")
    print("4. Normalize spaces")
    print("5. Change text capitalization")
    print("0. Cancel")

    choice = input("\nChoose an option: ").strip()

    if choice == "0":
        return None

    if choice == "1":
        columns = select_columns(dataset)
        if not columns:
            return None

        find_text = input("Text to find: ")
        replace_text = input("Replace with: ")

        partial = input(
            "Replace matching text inside cells? (y/n): "
        ).strip().lower() == "y"

        case_sensitive = input(
            "Case-sensitive matching? (y/n): "
        ).strip().lower() == "y"

        result = TextCleaningOperation.find_replace(
            dataset,
            columns=columns,
            find_text=find_text,
            replace_text=replace_text,
            partial=partial,
            case_sensitive=case_sensitive,
        )

    elif choice == "2":
        source_column = select_column(dataset)
        if source_column is None:
            return None

        separator = input(
            "Separator (press Enter for a space): "
        )
        if separator == "":
            separator = " "

        first_column = input("Name for first output column: ").strip()
        second_column = input("Name for second output column: ").strip()

        result = TextCleaningOperation.split_column(
            dataset,
            source_column=source_column,
            separator=separator,
            first_column=first_column,
            second_column=second_column,
        )

    elif choice == "3":
        columns = select_columns(dataset)
        if not columns or len(columns) < 2:
            print("Select at least two columns.")
            return None

        new_column = input("Name for combined column: ").strip()
        separator = input(
            "Separator (press Enter for a space): "
        )
        if separator == "":
            separator = " "

        result = TextCleaningOperation.combine_columns(
            dataset,
            columns=columns,
            new_column=new_column,
            separator=separator,
            skip_blank=True,
        )

    elif choice == "4":
        print("1. Normalize all text columns")
        print("2. Select columns")
        clean_choice = input("Choose an option: ").strip()

        if clean_choice == "1":
            result = TextCleaningOperation.normalize_spaces(dataset)
        elif clean_choice == "2":
            columns = select_columns(dataset)
            if not columns:
                return None

            result = TextCleaningOperation.normalize_spaces(
                dataset, columns=columns
            )
        else:
            print("Invalid option.")
            return None

    elif choice == "5":
        columns = select_columns(dataset)
        if not columns:
            return None

        print("1. UPPERCASE")
        print("2. lowercase")
        print("3. Title Case")

        case_choice = input("Choose capitalization style: ").strip()

        case_map = {
            "1": "upper",
            "2": "lower",
            "3": "title",
        }

        case_style = case_map.get(case_choice)

        if case_style is None:
            print("Invalid option.")
            return None

        result = TextCleaningOperation.change_case(
            dataset,
            columns=columns,
            case_style=case_style,
        )

    else:
        print("Invalid option.")
        return None

    print("\n--- Result Preview ---")
    print(result.preview(10).to_string(index=False))

    use_result = input(
        "\nUse this result as the current dataset? (y/n): "
    ).strip().lower()

    return result if use_result == "y" else None


# ============== part 8 ================

def validation_menu(dataset):
    """Menu for spreadsheet validation and data-quality checks."""

    while True:
        print("\n--- Data Validation and Quality Checks ---")
        print("1. Check required fields for blanks")
        print("2. Find duplicate values or combinations")
        print("3. Validate CNIC format")
        print("4. Validate K-M-F land area")
        print("5. Validate numeric columns")
        print("0. Return to main menu")

        choice = input("Choose an option: ").strip()

        if choice == "0":
            return None

        try:
            if choice == "1":
                columns = select_columns(dataset)

                if not columns:
                    continue

                report = ValidationOperation.check_blank_fields(
                    dataset, columns
                )

            elif choice == "2":
                print(
                    "Select one column for duplicates such as CNIC, "
                    "or multiple columns for duplicate combinations."
                )
                columns = select_columns(dataset)

                if not columns:
                    continue

                report = ValidationOperation.check_duplicates(
                    dataset, columns
                )

            elif choice == "3":
                column = select_column(dataset)

                if not column:
                    continue

                report = ValidationOperation.validate_cnic(
                    dataset, column
                )

            elif choice == "4":
                column = select_column(dataset)

                if not column:
                    continue

                print("Choose the square-foot standard:")
                print("1. 272 square feet per marla")
                print("2. 225 square feet per marla")

                standard_choice = input("Choose 1 or 2: ").strip()

                if standard_choice == "1":
                    sqft_per_marla = 272
                elif standard_choice == "2":
                    sqft_per_marla = 225
                else:
                    print("Invalid standard.")
                    continue

                report = ValidationOperation.validate_kmf_area(
                    dataset, column, sqft_per_marla
                )

            elif choice == "5":
                columns = select_columns(dataset)

                if not columns:
                    continue

                allow_negative_input = input(
                    "Allow negative values? (y/n): "
                ).strip().lower()

                if allow_negative_input not in ("y", "n"):
                    print("Please enter y or n.")
                    continue

                report = ValidationOperation.validate_numeric(
                    dataset,
                    columns,
                    allow_negative=(allow_negative_input == "y")
                )

            else:
                print("Invalid option. Please try again.")
                continue

            print("\n--- Validation Report ---")

            if report.row_count == 0:
                print("No issues found by this check.")
            else:
                print(f"Issues found: {report.row_count}")
                print(report.dataframe.to_string(index=False))

            export_choice = input(
                "\nExport this report? (y/n): "
            ).strip().lower()

            if export_choice == "y":
                from operations.export_manager import ExportManager

                ExportManager.export(
                    report,
                    output_format="xlsx",
                    filename_prefix="validation_report"
                )
                print("Export request completed.")

            use_report = input(
                "Make this report the current dataset? (y/n): "
            ).strip().lower()

            if use_report == "y":
                return report

        except (ValueError, TypeError, KeyError) as error:
            print(f"Could not complete validation: {error}")



# ============== part 9 ================

def safe_correction_menu(dataset):
    """Preview corrections, ask for approval, and optionally export."""

    from operations.export_manager import ExportManager

    while True:
        print("\n--- Safe Correction and Change Tracking ---")
        print("1. Find and replace text")
        print("2. Trim and normalize spaces")
        print("0. Return to main menu")

        choice = input("Choose an option: ").strip()

        if choice == "0":
            return None

        try:
            if choice == "1":
                columns = select_columns(dataset)

                if not columns:
                    continue

                find_text = input("Text to find: ")
                replace_text = input("Replace it with: ")

                print("\nMatch type:")
                print("1. Contains the text")
                print("2. Exact cell match")

                mode_choice = input("Choose 1 or 2: ").strip()

                if mode_choice == "1":
                    mode = "contains"
                elif mode_choice == "2":
                    mode = "exact"
                else:
                    print("Invalid match type.")
                    continue

                case_choice = input(
                    "Case-sensitive matching? (y/n): "
                ).strip().lower()

                if case_choice not in ("y", "n"):
                    print("Please enter y or n.")
                    continue

                proposed, change_log = (
                    SafeCorrectionOperation.preview_replace(
                        dataset,
                        columns,
                        find_text,
                        replace_text,
                        mode=mode,
                        case_sensitive=(case_choice == "y")
                    )
                )

            elif choice == "2":
                columns = select_columns(dataset)

                if not columns:
                    continue

                proposed, change_log = (
                    SafeCorrectionOperation.preview_trim_spaces(
                        dataset, columns
                    )
                )

            else:
                print("Invalid option. Please try again.")
                continue

            print("\n--- Proposed Changes ---")

            if change_log.row_count == 0:
                print("No changes are required.")
                continue

            print(f"Cells that would change: {change_log.row_count}")
            print(change_log.dataframe.to_string(index=False))

            preview_choice = input(
                "\nShow the proposed corrected data? (y/n): "
            ).strip().lower()

            if preview_choice == "y":
                print("\n--- Corrected Data Preview ---")
                print(proposed.preview(10).to_string(index=False))

            confirm = input(
                "\nApply these changes to the current session? (y/n): "
            ).strip().lower()

            if confirm != "y":
                print("Changes were not applied.")
                continue

            print("Changes approved for the current session.")

            export_corrected = input(
                "Export corrected data to a new Excel file? (y/n): "
            ).strip().lower()

            if export_corrected == "y":
                ExportManager.export(
                    proposed,
                    output_format="xlsx",
                    filename_prefix="corrected_data"
                )

            export_log = input(
                "Export the change log to a new Excel file? (y/n): "
            ).strip().lower()

            if export_log == "y":
                ExportManager.export(
                    change_log,
                    output_format="xlsx",
                    filename_prefix="change_log"
                )

            return proposed

        except (ValueError, TypeError, KeyError) as error:
            print(f"Could not prepare corrections: {error}")




def main_menu():

    original_dataset = None
    dataset = None
    history = HistoryManager()

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
        print("16. Reports and subtotals")
        print("17. Text cleaning and column transformations")
        print("18. Data validation and quality checks")
        print("19. Safe correction and change tracking")
        print("20. View operation history")
        print("21. Undo last change")
        print("22. Redo undone change")
        print()

        choice = input(
            "Select operation: "
        ).strip()

        if choice == "1":


            try:
                original_dataset = load_dataset()
                # dataset = original_dataset.copy()
                if original_dataset is not None:
                    dataset = original_dataset.copy()
                    history.reset(dataset)

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

        elif choice == "16":
            if dataset is None:
                print("Please load a file first.")
                continue

            try:
                result = report_menu(dataset)

                if result is not None:
                    dataset = result
                    print("Current dataset updated to the report.")

            except Exception as error:
                print(f"Report generation failed: {error}")

        
        elif choice == "17":
            if dataset is None:
                print("Please load a file first.")
                continue

            try:
                result = text_cleaning_menu(dataset)

                if result is not None:
                    dataset = result
                    print("Current dataset updated.")

            except Exception as error:
                print(f"Text-cleaning operation failed: {error}")

        elif choice == "18":
            result = validation_menu(dataset)

            if result is not None:
                history.record(result, "Validation report")
                dataset = result

        elif choice == "19":
            result = safe_correction_menu(dataset)

            if result is not None:
                history.record(result, "Safe correction")
                dataset = result

        
        elif choice == "20":
            history_table = history.get_history()

            if history_table.empty:
                print("No operation history is available.")
            else:
                print("\n--- Operation History ---")
                print(history_table.to_string(index=False))

        elif choice == "21":
            restored_dataset = history.undo()

            if restored_dataset is None:
                print("Nothing to undo.")
            else:
                dataset = restored_dataset
                print("Undo successful. Previous dataset state restored.")
                print_dataset_info(dataset)

        elif choice == "22":
            restored_dataset = history.redo()

            if restored_dataset is None:
                print("Nothing to redo.")
            else:
                dataset = restored_dataset
                print("Redo successful. Dataset state restored.")
                print_dataset_info(dataset)


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