
import re
import pandas as pd

from core.dataset import Dataset


class ValidationOperation:
    """Checks spreadsheet data and returns a report of detected issues."""

    REPORT_COLUMNS = ["Row_Number", "Column", "Issue", "Value"]

    @staticmethod
    def _check_columns(df, columns):
        missing = [column for column in columns if column not in df.columns]

        if missing:
            raise ValueError(f"Columns not found: {missing}")

    @staticmethod
    def _make_report(dataset, issues):
        """Create a Dataset containing validation issues."""

        report_df = pd.DataFrame(issues, columns=ValidationOperation.REPORT_COLUMNS)

        return Dataset(
            dataframe=report_df,
            source_file=dataset.source_file,
            sheet_name=dataset.sheet_name
        )

    @staticmethod
    def _is_blank(value):
        if pd.isna(value):
            return True

        return str(value).strip() == ""

    @staticmethod
    def check_blank_fields(dataset, required_columns):
        """Find blank cells in columns that must contain a value."""

        df = dataset.dataframe
        ValidationOperation._check_columns(df, required_columns)

        issues = []

        for position, (_, row) in enumerate(df.iterrows(), start=1):
            for column in required_columns:
                value = row[column]

                if ValidationOperation._is_blank(value):
                    issues.append([
                        position,
                        column,
                        "Required field is blank",
                        ""
                    ])

        return ValidationOperation._make_report(dataset, issues)

    @staticmethod
    def check_duplicates(dataset, columns):
        """Report every row belonging to a duplicate group."""

        df = dataset.dataframe
        ValidationOperation._check_columns(df, columns)

        if not columns:
            raise ValueError("Select at least one column.")

        # Ignore rows where every selected field is blank.
        blank_rows = df[columns].apply(
            lambda row: all(
                ValidationOperation._is_blank(value)
                for value in row
            ),
            axis=1
        )

        duplicate_mask = df.duplicated(
            subset=columns,
            keep=False
        ) & ~blank_rows

        issues = []

        for position, (_, row) in enumerate(df.iterrows(), start=1):
            if duplicate_mask.iloc[position - 1]:
                values = "; ".join(
                    f"{column}={row[column]}"
                    for column in columns
                )

                issues.append([
                    position,
                    ", ".join(columns),
                    "Duplicate value combination",
                    values
                ])

        return ValidationOperation._make_report(dataset, issues)

    @staticmethod
    def validate_cnic(dataset, column):
        """Check CNIC formatting, not whether the CNIC was officially issued."""

        df = dataset.dataframe
        ValidationOperation._check_columns(df, [column])

        issues = []

        # Accept either 13 digits or the standard 5-7-1 hyphen format.
        digits_pattern = re.compile(r"^\d{13}$")
        formatted_pattern = re.compile(r"^\d{5}-\d{7}-\d$")

        for position, value in enumerate(df[column], start=1):
            if ValidationOperation._is_blank(value):
                continue

            text = str(value).strip()

            if (
                not digits_pattern.fullmatch(text)
                and not formatted_pattern.fullmatch(text)
            ):
                issues.append([
                    position,
                    column,
                    "Invalid CNIC format",
                    text
                ])

        return ValidationOperation._make_report(dataset, issues)

    @staticmethod
    def validate_kmf_area(dataset, column, sqft_per_marla=272):
        """Check K-M-F format and whether marla/foot values are in range."""

        if sqft_per_marla not in (225, 272):
            raise ValueError("Square feet per marla must be 225 or 272.")

        df = dataset.dataframe
        ValidationOperation._check_columns(df, [column])

        issues = []
        pattern = re.compile(r"^\s*(\d+)\s*-\s*(\d+)\s*-\s*(\d+)\s*$")

        for position, value in enumerate(df[column], start=1):
            if ValidationOperation._is_blank(value):
                continue

            text = str(value).strip()
            match = pattern.fullmatch(text)

            if not match:
                issues.append([
                    position,
                    column,
                    "Invalid K-M-F format; expected Kanal-Marla-Foot",
                    text
                ])
                continue

            kanal, marla, foot = map(int, match.groups())

            if marla >= 20:
                issues.append([
                    position,
                    column,
                    "Marla must be less than 20",
                    text
                ])

            elif foot >= sqft_per_marla:
                issues.append([
                    position,
                    column,
                    f"Foot value must be less than {sqft_per_marla}",
                    text
                ])

        return ValidationOperation._make_report(dataset, issues)

    @staticmethod
    def validate_numeric(dataset, columns, allow_negative=False):
        """Find non-numeric values and, optionally, negative numbers."""

        df = dataset.dataframe
        ValidationOperation._check_columns(df, columns)

        if not columns:
            raise ValueError("Select at least one column.")

        issues = []

        for position, (_, row) in enumerate(df.iterrows(), start=1):
            for column in columns:
                value = row[column]

                # Blank values are handled by the required-field check.
                if ValidationOperation._is_blank(value):
                    continue

                number = pd.to_numeric(value, errors="coerce")

                if pd.isna(number):
                    issues.append([
                        position,
                        column,
                        "Value is not numeric",
                        str(value)
                    ])

                elif not allow_negative and number < 0:
                    issues.append([
                        position,
                        column,
                        "Negative value is not allowed",
                        str(value)
                    ])

        return ValidationOperation._make_report(dataset, issues)
