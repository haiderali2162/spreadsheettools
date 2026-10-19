
import re
import pandas as pd

from core.dataset import Dataset


class SafeCorrectionOperation:
    """Preview spreadsheet corrections and record every changed cell."""

    LOG_COLUMNS = [
        "Row_Number",
        "Column",
        "Old_Value",
        "New_Value",
        "Operation"
    ]

    @staticmethod
    def _check_columns(df, columns):
        missing = [column for column in columns if column not in df.columns]

        if missing:
            raise ValueError(f"Columns not found: {missing}")

        if not columns:
            raise ValueError("Select at least one column.")

    @staticmethod
    def _make_dataset(original, dataframe):
        return Dataset(
            dataframe=dataframe,
            source_file=original.source_file,
            sheet_name=original.sheet_name
        )

    @staticmethod
    def _make_log(original, changes):
        log_df = pd.DataFrame(
            changes,
            columns=SafeCorrectionOperation.LOG_COLUMNS
        )

        return SafeCorrectionOperation._make_dataset(original, log_df)

    @staticmethod
    def _is_blank(value):
        if pd.isna(value):
            return True

        return str(value).strip() == ""

    @staticmethod
    def preview_replace(
        dataset,
        columns,
        find_text,
        replace_text,
        mode="contains",
        case_sensitive=False
    ):
        """
        Return a proposed dataset and a change log.
        The original dataset is not modified.
        """

        df = dataset.dataframe.copy()
        SafeCorrectionOperation._check_columns(df, columns)

        find_text = str(find_text)
        replace_text = str(replace_text)

        if find_text == "":
            raise ValueError("The text to find cannot be blank.")

        if mode not in ("contains", "exact"):
            raise ValueError("Mode must be 'contains' or 'exact'.")

        changes = []

        for column in columns:
            original_values = df[column].copy()

            for position, (index, value) in enumerate(
                original_values.items(), start=1
            ):
                if SafeCorrectionOperation._is_blank(value):
                    continue

                old_text = str(value)

                if mode == "exact":
                    if case_sensitive:
                        matches = old_text == find_text
                    else:
                        matches = old_text.casefold() == find_text.casefold()

                    new_text = replace_text if matches else old_text

                else:
                    if case_sensitive:
                        new_text = old_text.replace(find_text, replace_text)
                    else:
                        new_text = re.sub(
                            re.escape(find_text),
                            lambda _: replace_text,
                            old_text,
                            flags=re.IGNORECASE
                        )

                if new_text != old_text:
                    df.at[index, column] = new_text

                    changes.append([
                        position,
                        column,
                        old_text,
                        new_text,
                        f"Replace ({mode})"
                    ])

        proposed_dataset = SafeCorrectionOperation._make_dataset(
            dataset, df
        )
        change_log = SafeCorrectionOperation._make_log(dataset, changes)

        return proposed_dataset, change_log

    @staticmethod
    def preview_trim_spaces(dataset, columns):
        """Preview removal of leading/trailing and repeated spaces."""

        df = dataset.dataframe.copy()
        SafeCorrectionOperation._check_columns(df, columns)

        changes = []

        for column in columns:
            for position, (index, value) in enumerate(
                df[column].items(), start=1
            ):
                if SafeCorrectionOperation._is_blank(value):
                    continue

                old_text = str(value)
                new_text = re.sub(r"\s+", " ", old_text).strip()

                if new_text != old_text:
                    df.at[index, column] = new_text

                    changes.append([
                        position,
                        column,
                        old_text,
                        new_text,
                        "Trim and normalize spaces"
                    ])

        proposed_dataset = SafeCorrectionOperation._make_dataset(
            dataset, df
        )
        change_log = SafeCorrectionOperation._make_log(dataset, changes)

        return proposed_dataset, change_log
