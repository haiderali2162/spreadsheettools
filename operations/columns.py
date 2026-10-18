
import pandas as pd

from core.dataset import Dataset


class ColumnOperation:
    """Manage columns and clean spreadsheet values."""

    @staticmethod
    def _check_column(df, column):
        if column not in df.columns:
            raise ValueError(f"Column '{column}' does not exist.")

    @staticmethod
    def _new_dataset(dataset, dataframe):
        return Dataset(
            dataframe=dataframe,
            source_file=dataset.source_file,
            sheet_name=dataset.sheet_name,
        )

    @staticmethod
    def rename_column(dataset, old_name, new_name):
        df = dataset.dataframe

        ColumnOperation._check_column(df, old_name)
        new_name = new_name.strip()

        if not new_name:
            raise ValueError("The new column name cannot be blank.")

        if new_name != old_name and new_name in df.columns:
            raise ValueError(f"Column '{new_name}' already exists.")

        result = df.rename(columns={old_name: new_name}).copy()
        return ColumnOperation._new_dataset(dataset, result)

    @staticmethod
    def copy_column(dataset, source_column, new_column):
        df = dataset.dataframe

        ColumnOperation._check_column(df, source_column)
        new_column = new_column.strip()

        if not new_column:
            raise ValueError("The new column name cannot be blank.")

        if new_column in df.columns:
            raise ValueError(f"Column '{new_column}' already exists.")

        result = df.copy()
        result[new_column] = result[source_column].copy()

        return ColumnOperation._new_dataset(dataset, result)

    @staticmethod
    def delete_columns(dataset, columns):
        df = dataset.dataframe

        if not columns:
            raise ValueError("Select at least one column.")

        missing = [col for col in columns if col not in df.columns]
        if missing:
            raise ValueError(f"Columns not found: {missing}")

        result = df.drop(columns=columns).copy()
        return ColumnOperation._new_dataset(dataset, result)

    @staticmethod
    def move_columns_first(dataset, columns):
        df = dataset.dataframe

        if not columns:
            raise ValueError("Select at least one column.")

        missing = [col for col in columns if col not in df.columns]
        if missing:
            raise ValueError(f"Columns not found: {missing}")

        # Remove repeated selections while preserving their order.
        selected = list(dict.fromkeys(columns))
        remaining = [col for col in df.columns if col not in selected]
        result = df[selected + remaining].copy()

        return ColumnOperation._new_dataset(dataset, result)

    @staticmethod
    def trim_text(dataset, columns=None):
        df = dataset.dataframe.copy()

        if columns is None:
            columns = list(df.select_dtypes(include=["object", "string"]).columns)

        if not columns:
            raise ValueError("No text columns were selected or found.")

        for column in columns:
            ColumnOperation._check_column(df, column)

            # Trim leading/trailing spaces only from text values.
            df[column] = df[column].map(
                lambda value: value.strip()
                if isinstance(value, str)
                else value
            )

        return ColumnOperation._new_dataset(dataset, df)

    @staticmethod
    def replace_values(
        dataset,
        column,
        old_value,
        new_value,
        partial=False,
        case_sensitive=True,
    ):
        df = dataset.dataframe.copy()
        ColumnOperation._check_column(df, column)

        if partial:
            # Partial replacement applies only to text values.
            series = df[column].astype("string")

            df[column] = series.str.replace(
                str(old_value),
                str(new_value),
                regex=False,
                case=case_sensitive,
            )
        else:
            # Exact replacement: replace matching cell values.
            if case_sensitive:
                df[column] = df[column].replace(old_value, new_value)
            else:
                mask = (
                    df[column]
                    .astype("string")
                    .str.lower()
                    .eq(str(old_value).lower())
                )
                df.loc[mask, column] = new_value

        return ColumnOperation._new_dataset(dataset, df)

    @staticmethod
    def add_serial_numbers(
        dataset,
        column_name="Serial",
        start=1,
    ):
        df = dataset.dataframe.copy()
        column_name = column_name.strip()

        if not column_name:
            raise ValueError("The serial column name cannot be blank.")

        if column_name in df.columns:
            raise ValueError(
                f"Column '{column_name}' already exists. Choose another name."
            )

        if start < 0:
            raise ValueError("The starting serial number cannot be negative.")

        # Number the current rows in their current order.
        df.insert(
            0,
            column_name,
            range(start, start + len(df)),
        )

        return ColumnOperation._new_dataset(dataset, df)

    @staticmethod
    def compare_columns(
        dataset,
        left_column,
        operator,
        right_column,
        result_column=None,
    ):
        df = dataset.dataframe.copy()

        ColumnOperation._check_column(df, left_column)
        ColumnOperation._check_column(df, right_column)

        left = df[left_column]
        right = df[right_column]

        if operator == "==":
            comparison = left.eq(right)
        elif operator == "!=":
            comparison = left.ne(right)
        elif operator in {">", "<", ">=", "<="}:
            # Numeric comparison avoids accidental text ordering.
            left_num = pd.to_numeric(left, errors="coerce")
            right_num = pd.to_numeric(right, errors="coerce")

            if operator == ">":
                comparison = left_num.gt(right_num)
            elif operator == "<":
                comparison = left_num.lt(right_num)
            elif operator == ">=":
                comparison = left_num.ge(right_num)
            else:
                comparison = left_num.le(right_num)
        else:
            raise ValueError(
                "Supported comparison operators: ==, !=, >, <, >=, <="
            )

        # Unknown numeric comparisons should not count as matches.
        if operator in {">", "<", ">=", "<="}:
            comparison = comparison.fillna(False)

        if result_column:
            result_column = result_column.strip()

            if not result_column:
                raise ValueError("The result column name cannot be blank.")

            if result_column in df.columns:
                raise ValueError(
                    f"Column '{result_column}' already exists."
                )

            df[result_column] = comparison
            return ColumnOperation._new_dataset(dataset, df)

        # If no result column was specified, return only matching rows.
        result = df.loc[comparison.fillna(False)].copy()
        return ColumnOperation._new_dataset(dataset, result)

    @staticmethod
    def subtract_columns(
        dataset,
        left_column,
        right_column,
        result_column,
    ):
        df = dataset.dataframe.copy()

        ColumnOperation._check_column(df, left_column)
        ColumnOperation._check_column(df, right_column)

        result_column = result_column.strip()

        if not result_column:
            raise ValueError("The result column name cannot be blank.")

        if result_column in df.columns:
            raise ValueError(
                f"Column '{result_column}' already exists."
            )

        left = pd.to_numeric(df[left_column], errors="coerce")
        right = pd.to_numeric(df[right_column], errors="coerce")

        df[result_column] = left - right

        return ColumnOperation._new_dataset(dataset, df)
