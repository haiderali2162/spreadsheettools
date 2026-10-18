
import pandas as pd

from core.dataset import Dataset
from operations.filter import FilterOperation


class CalculationOperation:
    """Calculate statistics and summaries for spreadsheet data."""

    SUPPORTED_OPERATIONS = {
        "sum",
        "average",
        "min",
        "max",
        "count",
        "count_non_empty",
        "count_unique",
        "median",
    }

    @staticmethod
    def calculate(
        dataset: Dataset,
        operation: str,
        column: str | None = None,
    ):
        df = dataset.dataframe
        operation = operation.lower().strip()

        if operation not in CalculationOperation.SUPPORTED_OPERATIONS:
            raise ValueError(
                f"Unsupported calculation: {operation}"
            )

        # Count every record, including records with blank cells.
        if operation == "count":
            return len(df)

        if column is None or column not in df.columns:
            raise ValueError(
                "Select a valid column for this calculation."
            )

        series = df[column]

        # Count non-empty cells.
        if operation == "count_non_empty":
            return int(series.count())

        # Count distinct non-empty values.
        if operation == "count_unique":
            return int(series.nunique(dropna=True))

        # Convert values to numbers for mathematical operations.
        numbers = pd.to_numeric(series, errors="coerce").dropna()

        if numbers.empty:
            if operation in {"sum"}:
                return 0
            return None

        if operation == "sum":
            return numbers.sum()

        if operation == "average":
            return numbers.mean()

        if operation == "min":
            return numbers.min()

        if operation == "max":
            return numbers.max()

        if operation == "median":
            return numbers.median()

        raise ValueError("Calculation could not be completed.")

    @staticmethod
    def conditional_calculate(
        dataset: Dataset,
        operation: str,
        target_column: str | None = None,
        conditions: list | None = None,
        logic: str = "AND",
    ):
        """
        Calculate a value only for rows matching the conditions.

        Example:
            Sum DC Rate where Classification = Agricultural.
        """

        conditions = conditions or []

        if conditions:
            filtered = FilterOperation.filter_multiple(
                dataset,
                conditions,
                logic,
            )
        else:
            filtered = dataset

        return CalculationOperation.calculate(
            filtered,
            operation,
            target_column,
        )

    @staticmethod
    def group_summary(
        dataset: Dataset,
        group_columns: list[str],
        aggregations: dict[str, list[str]],
    ) -> Dataset:
        """
        Group records and calculate summaries.

        Example:
            Group by Classification.
            Sum DC Rate and count Owner Name.
        """

        df = dataset.dataframe

        if not group_columns:
            raise ValueError(
                "Select at least one grouping column."
            )

        for column in group_columns:
            if column not in df.columns:
                raise ValueError(
                    f"Grouping column '{column}' does not exist."
                )

        if not aggregations:
            raise ValueError(
                "Select at least one aggregation."
            )

        allowed = {
            "sum",
            "mean",
            "min",
            "max",
            "count",
            "nunique",
            "median",
        }

        for column, operations in aggregations.items():
            if column not in df.columns:
                raise ValueError(
                    f"Aggregation column '{column}' does not exist."
                )

            for operation in operations:
                if operation not in allowed:
                    raise ValueError(
                        f"Unsupported group calculation: {operation}"
                    )

        summary = df.groupby(
            group_columns,
            dropna=False,
            sort=True,
        ).agg(aggregations)

        # Flatten column names, for example DC Rate_sum.
        summary.columns = [
            f"{column}_{operation}"
            for column, operation in summary.columns
        ]

        summary = summary.reset_index()

        return Dataset(
            dataframe=summary,
            source_file=dataset.source_file,
            sheet_name="Summary",
        )
