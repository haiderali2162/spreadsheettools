from typing import Any

import pandas as pd

from core.dataset import Dataset


class FilterOperation:

    SUPPORTED_OPERATORS = {
        "=",
        "==",
        "!=",
        ">",
        "<",
        ">=",
        "<=",
        "contains",
        "not_contains",
        "starts_with",
        "ends_with",
        "is_blank",
        "is_not_blank",
        "between",
        "in",
        "not_in",
    }

    @staticmethod
    def validate_column(
        dataframe: pd.DataFrame,
        column: str
    ):
        if column not in dataframe.columns:
            raise ValueError(
                f"Column '{column}' does not exist."
            )

    @staticmethod
    def apply_condition(
        dataframe: pd.DataFrame,
        column: str,
        operator: str,
        value: Any = None
    ) -> pd.Series:

        FilterOperation.validate_column(
            dataframe,
            column
        )

        if operator not in FilterOperation.SUPPORTED_OPERATORS:
            raise ValueError(
                f"Unsupported operator: {operator}"
            )

        series = dataframe[column]

        # -------------------------
        # Blank
        # -------------------------

        if operator == "is_blank":

            return series.isna() | (
                series.astype("string").str.strip() == ""
            )

        if operator == "is_not_blank":

            return ~(
                series.isna() |
                (series.astype("string").str.strip() == "")
            )

        # -------------------------
        # Text operators
        # -------------------------

        if operator == "contains":

            return series.astype("string").str.contains(
                str(value),
                case=False,
                na=False,
                regex=False
            )

        if operator == "not_contains":

            return ~series.astype("string").str.contains(
                str(value),
                case=False,
                na=False,
                regex=False
            )

        if operator == "starts_with":

            return series.astype("string").str.startswith(
                str(value),
                na=False
            )

        if operator == "ends_with":

            return series.astype("string").str.endswith(
                str(value),
                na=False
            )

        # -------------------------
        # List operators
        # -------------------------

        if operator == "in":

            if not isinstance(value, (list, tuple, set)):
                raise ValueError(
                    "'in' requires a list of values."
                )

            return series.isin(value)

        if operator == "not_in":

            if not isinstance(value, (list, tuple, set)):
                raise ValueError(
                    "'not_in' requires a list of values."
                )

            return ~series.isin(value)

        # -------------------------
        # Between
        # -------------------------

        if operator == "between":

            if not isinstance(value, (list, tuple)):
                raise ValueError(
                    "'between' requires two values."
                )

            if len(value) != 2:
                raise ValueError(
                    "'between' requires exactly two values."
                )

            return (
                series >= value[0]
            ) & (
                series <= value[1]
            )

        # -------------------------
        # Numeric / equality
        # -------------------------

        if operator in {
            "=",
            "==",
            "!=",
            ">",
            "<",
            ">=",
            "<="
        }:

            return FilterOperation.compare_values(
                series,
                operator,
                value
            )

        raise ValueError(
            f"Operator '{operator}' is not implemented."
        )

    @staticmethod
    def compare_values(
        series: pd.Series,
        operator: str,
        value: Any
    ) -> pd.Series:

        if operator in {"=", "=="}:
            return series == value

        if operator == "!=":
            return series != value

        if operator == ">":
            return series > value

        if operator == "<":
            return series < value

        if operator == ">=":
            return series >= value

        if operator == "<=":
            return series <= value

        raise ValueError(
            f"Invalid comparison operator: {operator}"
        )

    @staticmethod
    def filter(
        dataset: Dataset,
        column: str,
        operator: str,
        value: Any = None
    ) -> Dataset:

        mask = FilterOperation.apply_condition(
            dataset.dataframe,
            column,
            operator,
            value
        )

        result = dataset.dataframe.loc[mask].copy()

        return Dataset(
            dataframe=result,
            source_file=dataset.source_file,
            sheet_name=dataset.sheet_name
        )

    @staticmethod
    def filter_multiple(
        dataset: Dataset,
        conditions: list,
        logic: str = "AND"
    ) -> Dataset:

        if not conditions:
            raise ValueError(
                "At least one condition is required."
            )

        dataframe = dataset.dataframe

        masks = []

        for condition in conditions:

            mask = FilterOperation.apply_condition(
                dataframe,
                condition["column"],
                condition["operator"],
                condition.get("value")
            )

            masks.append(mask)

        final_mask = masks[0]

        logic = logic.upper()

        if logic == "AND":

            for mask in masks[1:]:
                final_mask = final_mask & mask

        elif logic == "OR":

            for mask in masks[1:]:
                final_mask = final_mask | mask

        else:
            raise ValueError(
                "Logic must be either AND or OR."
            )

        result = dataframe.loc[
            final_mask
        ].copy()

        return Dataset(
            dataframe=result,
            source_file=dataset.source_file,
            sheet_name=dataset.sheet_name
        )