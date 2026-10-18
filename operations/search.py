import pandas as pd

from core.dataset import Dataset


class SearchOperation:

    @staticmethod
    def search(
        dataset: Dataset,
        column: str,
        value: str,
        mode: str = "contains",
        case_sensitive: bool = False
    ) -> Dataset:
        """
        Search a column and return matching records.

        Modes:
            exact
            contains
            starts_with
            ends_with
        """

        dataframe = dataset.dataframe

        if column not in dataframe.columns:
            raise ValueError(
                f"Column '{column}' does not exist."
            )

        series = dataframe[column].astype("string")

        if not case_sensitive:
            series = series.str.lower()
            value = value.lower()

        if mode == "exact":

            mask = series == value

        elif mode == "contains":

            mask = series.str.contains(
                value,
                na=False,
                regex=False
            )

        elif mode == "starts_with":

            mask = series.str.startswith(
                value,
                na=False
            )

        elif mode == "ends_with":

            mask = series.str.endswith(
                value,
                na=False
            )

        else:
            raise ValueError(
                f"Unknown search mode: {mode}"
            )

        result = dataframe.loc[mask].copy()

        return Dataset(
            dataframe=result,
            source_file=dataset.source_file,
            sheet_name=dataset.sheet_name
        )