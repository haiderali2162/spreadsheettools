
import pandas as pd

from core.dataset import Dataset


class ReportOperation:
    """Generate grouped summaries and subtotals."""

    SUPPORTED_AGGREGATIONS = {
        "sum",
        "mean",
        "min",
        "max",
        "count",
        "nunique",
        "median",
    }

    @staticmethod
    def group_summary(
        dataset: Dataset,
        group_columns: list[str],
        aggregations: dict[str, list[str]] | None = None,
        include_record_count: bool = True,
    ) -> Dataset:
        df = dataset.dataframe

        if not group_columns:
            raise ValueError("Select at least one grouping column.")

        if len(set(group_columns)) != len(group_columns):
            raise ValueError("A grouping column was selected more than once.")

        missing_groups = [
            column for column in group_columns if column not in df.columns
        ]
        if missing_groups:
            raise ValueError(f"Grouping columns not found: {missing_groups}")

        aggregations = aggregations or {}

        for column, operations in aggregations.items():
            if column not in df.columns:
                raise ValueError(
                    f"Aggregation column '{column}' does not exist."
                )

            if column in group_columns:
                raise ValueError(
                    f"'{column}' is a grouping column. "
                    "Choose a different column to calculate."
                )

            if not operations:
                raise ValueError(
                    f"Select at least one calculation for '{column}'."
                )

            for operation in operations:
                if operation not in ReportOperation.SUPPORTED_AGGREGATIONS:
                    raise ValueError(
                        f"Unsupported calculation: {operation}"
                    )

        working = df.copy()
        aggregation_plan = {}

        # Numeric calculations should use numeric values, not concatenate
        # strings that happen to look like numbers.
        numeric_operations = {
            "sum", "mean", "median", "min", "max"
        }

        for column, operations in aggregations.items():
            for operation in operations:
                if operation in numeric_operations:
                    if column not in working.columns:
                        raise ValueError(f"Column '{column}' does not exist.")

                    if not pd.api.types.is_numeric_dtype(working[column]):
                        working[column] = pd.to_numeric(
                            working[column],
                            errors="coerce",
                        )

                aggregation_plan.setdefault(column, []).append(operation)

        grouped = working.groupby(
            group_columns,
            dropna=False,
            sort=True,
            observed=False,
        )

        # Build the summary.
        if aggregation_plan:
            summary = grouped.agg(aggregation_plan)

            # Give calculated columns simple, readable names.
            summary.columns = [
                f"{column}_{operation}"
                for column, operation in summary.columns
            ]

            summary = summary.reset_index()
        else:
            summary = grouped.size().reset_index(name="Record_Count")

        # Add a record count even when other calculations were selected.
        if include_record_count and "Record_Count" not in summary.columns:
            counts = grouped.size().reset_index(name="Record_Count")

            summary = summary.merge(
                counts,
                on=group_columns,
                how="left",
                sort=False,
            )

        return Dataset(
            dataframe=summary,
            source_file=dataset.source_file,
            sheet_name="Summary",
        )

    @staticmethod
    def overall_summary(dataset: Dataset) -> Dataset:
        """Create one overall row describing the current dataset."""
        df = dataset.dataframe

        result = {
            "Record_Count": len(df),
            "Column_Count": len(df.columns),
        }

        for column in df.columns:
            result[f"{column}_Non_Empty"] = int(df[column].count())
            result[f"{column}_Unique"] = int(df[column].nunique(dropna=True))

        summary = pd.DataFrame([result])

        return Dataset(
            dataframe=summary,
            source_file=dataset.source_file,
            sheet_name="Overall_Summary",
        )
