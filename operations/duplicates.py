
from core.dataset import Dataset
import pandas as pd


class DuplicateOperation:
    """Find and remove duplicate spreadsheet records."""

    @staticmethod
    def find_duplicates(
        dataset: Dataset,
        columns: list[str] | None = None,
        keep: str = "first",
    ) -> Dataset:
        df = dataset.dataframe

        if columns is not None:
            if not columns:
                raise ValueError("Select at least one column.")

            missing = [col for col in columns if col not in df.columns]
            if missing:
                raise ValueError(f"Columns not found: {missing}")

        if keep not in {"first", "last", "all"}:
            raise ValueError("Keep must be first, last, or all.")

        # Mark every occurrence that belongs to a duplicate group.
        if keep == "all":
            mask = df.duplicated(subset=columns, keep=False)
        else:
            # For first/last, show only the occurrences that would be removed.
            mask = df.duplicated(subset=columns, keep=keep)

        result = df.loc[mask].copy()

        return Dataset(
            dataframe=result,
            source_file=dataset.source_file,
            sheet_name=dataset.sheet_name,
        )

    @staticmethod
    def remove_duplicates(
        dataset: Dataset,
        columns: list[str] | None = None,
        keep: str = "first",
    ) -> Dataset:
        df = dataset.dataframe

        if columns is not None:
            if not columns:
                raise ValueError("Select at least one column.")

            missing = [col for col in columns if col not in df.columns]
            if missing:
                raise ValueError(f"Columns not found: {missing}")

        if keep not in {"first", "last"}:
            raise ValueError("Keep must be first or last.")

        result = df.drop_duplicates(
            subset=columns,
            keep=keep,
        ).copy()

        return Dataset(
            dataframe=result,
            source_file=dataset.source_file,
            sheet_name=dataset.sheet_name,
        )

    @staticmethod
    def keep_highest_or_lowest(
        dataset: Dataset,
        duplicate_columns: list[str],
        priority_column: str,
        highest: bool = True,
    ) -> Dataset:
        df = dataset.dataframe

        if not duplicate_columns:
            raise ValueError("Select at least one duplicate-check column.")

        missing = [
            col for col in duplicate_columns + [priority_column]
            if col not in df.columns
        ]
        if missing:
            raise ValueError(f"Columns not found: {missing}")

        if priority_column in duplicate_columns:
            raise ValueError(
                "The priority column must not be one of the duplicate-check columns."
            )

        # Convert the priority values to numbers for a numeric comparison.
        # priority_values = __import__("pandas").to_numeric(
        priority_values = pd.to_numeric(
            df[priority_column],
            errors="coerce",
        )

        # Keep the original row order when priorities are tied.
        working = df.copy()
        working["__original_row_position__"] = range(len(working))
        working["__priority_number__"] = priority_values

        working = working.sort_values(
            by="__priority_number__",
            ascending=not highest,
            na_position="last",
            kind="stable",
        )

        working = working.drop_duplicates(
            subset=duplicate_columns,
            keep="first",
        )

        working = working.sort_values(
            by="__original_row_position__",
            kind="stable",
        )

        result = working.drop(
            columns=[
                "__original_row_position__",
                "__priority_number__",
            ]
        ).copy()

        return Dataset(
            dataframe=result,
            source_file=dataset.source_file,
            sheet_name=dataset.sheet_name,
        )
