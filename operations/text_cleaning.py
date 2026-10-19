
import pandas as pd
import re

from core.dataset import Dataset


class TextCleaningOperation:
    """Clean text and split or combine spreadsheet columns."""

    @staticmethod
    def _check_columns(df, columns):
        missing = [column for column in columns if column not in df.columns]
        if missing:
            raise ValueError(f"Columns not found: {missing}")

    @staticmethod
    def _new_dataset(dataset, dataframe):
        return Dataset(
            dataframe=dataframe,
            source_file=dataset.source_file,
            sheet_name=dataset.sheet_name,
        )

    @staticmethod
    def _check_new_column(df, column_name):
        if not column_name or not column_name.strip():
            raise ValueError("Column name cannot be blank.")

        if column_name in df.columns:
            raise ValueError(f"Column '{column_name}' already exists.")

    @staticmethod
    def find_replace(
        dataset,
        columns,
        find_text,
        replace_text,
        partial=True,
        case_sensitive=False,
    ):
        """Find and replace text in selected columns."""
        df = dataset.dataframe.copy()

        if not columns:
            raise ValueError("Select at least one column.")

        TextCleaningOperation._check_columns(df, columns)

        find_text = str(find_text)
        replace_text = str(replace_text)

        if find_text == "":
            raise ValueError("The text to find cannot be empty.")

        for column in columns:
            # Convert to pandas string type while preserving missing values.
            values = df[column].astype("string")

            if partial:
                df[column] = values.str.replace(
                    find_text,
                    replace_text,
                    regex=False,
                    case=case_sensitive,
                )
            elif case_sensitive:
                df[column] = values.mask(
                    values.eq(find_text),
                    replace_text,
                )
            else:
                mask = values.str.lower().eq(find_text.lower())
                df[column] = values.mask(mask, replace_text)

        return TextCleaningOperation._new_dataset(dataset, df)

    @staticmethod
    def split_column(
        dataset,
        source_column,
        separator,
        first_column,
        second_column,
        max_splits=1,
    ):
        """
        Split a column into two columns.
        Example: 'Haider Ali' -> 'Haider' and 'Ali'.
        """
        df = dataset.dataframe.copy()

        TextCleaningOperation._check_columns(df, [source_column])

        if not separator:
            raise ValueError("Separator cannot be empty.")

        if first_column == second_column:
            raise ValueError("Output column names must be different.")

        TextCleaningOperation._check_new_column(df, first_column)
        TextCleaningOperation._check_new_column(df, second_column)

        if max_splits < 1:
            raise ValueError("Maximum splits must be at least 1.")

        split_values = df[source_column].astype("string").str.split(
            separator,
            n=max_splits,
            expand=True,
            regex=False,
        )

        first_values = (
            split_values[0]
            if 0 in split_values.columns
            else pd.Series(pd.NA, index=df.index, dtype="string")
        )

        second_values = (
            split_values[1]
            if 1 in split_values.columns
            else pd.Series(pd.NA, index=df.index, dtype="string")
        )

        # Trim spaces around each split part.
        df[first_column] = first_values.str.strip()
        df[second_column] = second_values.str.strip()

        return TextCleaningOperation._new_dataset(dataset, df)

    @staticmethod
    def combine_columns(
        dataset,
        columns,
        new_column,
        separator=" ",
        skip_blank=True,
    ):
        """Combine selected columns into one text column."""
        df = dataset.dataframe.copy()

        if len(columns) < 2:
            raise ValueError("Select at least two columns.")

        TextCleaningOperation._check_columns(df, columns)
        TextCleaningOperation._check_new_column(df, new_column)

        parts = []

        for column in columns:
            values = df[column].astype("string").fillna("").str.strip()
            parts.append(values)

        if skip_blank:
            combined = parts[0]

            for values in parts[1:]:
                combined = (
                    combined.str.cat(values, sep=separator)
                    .str.strip()
                )

            # Remove repeated separators caused by blank cells.
            if separator:
                # combined = combined.str.replace(
                #     f"(?:{separator})+",
                #     separator,
                #     regex=True,
                # )
                combined = combined.str.replace(
                f"(?:{re.escape(separator)})+",
                lambda match: separator,
                regex=True,
                )
        else:
            combined = parts[0]

            for values in parts[1:]:
                combined = combined.str.cat(values, sep=separator)

        df[new_column] = combined

        return TextCleaningOperation._new_dataset(dataset, df)

    @staticmethod
    def normalize_spaces(dataset, columns=None):
        """Trim outer spaces and collapse repeated whitespace."""
        df = dataset.dataframe.copy()

        if columns is None:
            columns = list(
                df.select_dtypes(include=["object", "string"]).columns
            )

        if not columns:
            raise ValueError("No text columns selected or found.")

        TextCleaningOperation._check_columns(df, columns)

        for column in columns:
            values = df[column].astype("string")
            df[column] = values.str.replace(
                r"\s+",
                " ",
                regex=True,
            ).str.strip()

        return TextCleaningOperation._new_dataset(dataset, df)

    @staticmethod
    def change_case(dataset, columns, case_style):
        """
        Change English/text capitalization.
        Supported styles: upper, lower, title.
        """
        df = dataset.dataframe.copy()

        if not columns:
            raise ValueError("Select at least one column.")

        TextCleaningOperation._check_columns(df, columns)

        if case_style not in {"upper", "lower", "title"}:
            raise ValueError("Choose upper, lower, or title.")

        for column in columns:
            values = df[column].astype("string")

            if case_style == "upper":
                df[column] = values.str.upper()
            elif case_style == "lower":
                df[column] = values.str.lower()
            else:
                df[column] = values.str.title()

        return TextCleaningOperation._new_dataset(dataset, df)
