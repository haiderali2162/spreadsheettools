from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd


@dataclass
class Dataset:
    """
    Represents a spreadsheet loaded into memory.

    The original file is never modified by this class.
    """

    dataframe: pd.DataFrame
    source_file: Path
    sheet_name: Optional[str] = None

    @property
    def row_count(self) -> int:
        return len(self.dataframe)

    @property
    def column_count(self) -> int:
        return len(self.dataframe.columns)

    @property
    def columns(self):
        return list(self.dataframe.columns)

    def preview(self, rows: int = 10) -> pd.DataFrame:
        """
        Return the first N rows of the dataset.
        """
        return self.dataframe.head(rows)

    def copy(self) -> "Dataset":
        """
        Create an independent copy of the dataset.
        """
        return Dataset(
            dataframe=self.dataframe.copy(),
            source_file=self.source_file,
            sheet_name=self.sheet_name
        )