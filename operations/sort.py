from core.dataset import Dataset


class SortOperation:

    @staticmethod
    def sort(
        dataset: Dataset,
        column: str,
        ascending: bool = True
    ) -> Dataset:

        if column not in dataset.dataframe.columns:
            raise ValueError(
                f"Column '{column}' does not exist."
            )

        result = dataset.dataframe.sort_values(
            by=column,
            ascending=ascending,
            kind="stable"
        ).copy()

        return Dataset(
            dataframe=result,
            source_file=dataset.source_file,
            sheet_name=dataset.sheet_name
        )

    @staticmethod
    def sort_multiple(
        dataset: Dataset,
        columns: list[str],
        ascending: list[bool] | None = None
    ) -> Dataset:

        if not columns:
            raise ValueError(
                "At least one column is required."
            )

        for column in columns:

            if column not in dataset.dataframe.columns:
                raise ValueError(
                    f"Column '{column}' does not exist."
                )

        if ascending is None:
            ascending = [True] * len(columns)

        if len(ascending) != len(columns):
            raise ValueError(
                "Number of sort directions must match "
                "number of columns."
            )

        result = dataset.dataframe.sort_values(
            by=columns,
            ascending=ascending,
            kind="stable"
        ).copy()

        return Dataset(
            dataframe=result,
            source_file=dataset.source_file,
            sheet_name=dataset.sheet_name
        )