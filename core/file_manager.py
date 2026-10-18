from pathlib import Path
from typing import List, Optional

import pandas as pd

from .dataset import Dataset


class FileManager:
    """
    Handles reading and writing spreadsheet files.

    Supported formats:
        CSV
        TSV
        XLSX
        XLS
        ODS
        XLSB
    """

    SUPPORTED_EXTENSIONS = {
        ".csv",
        ".tsv",
        ".xlsx",
        ".xls",
        ".ods",
        ".xlsb",
    }

    @staticmethod
    def validate_file(file_path: str | Path) -> Path:
        """
        Validate that the file exists and has a supported extension.
        """

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"File does not exist: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"Path is not a file: {path}"
            )

        extension = path.suffix.lower()

        if extension not in FileManager.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file format: {extension}"
            )

        return path

    @staticmethod
    def get_sheets(file_path: str | Path) -> List[str]:
        """
        Return available sheet names.

        CSV and TSV files don't have sheets, so the filename
        is treated as a single logical sheet.
        """

        path = FileManager.validate_file(file_path)

        extension = path.suffix.lower()

        if extension in {".csv", ".tsv"}:
            return [path.stem]

        if extension in {".xlsx", ".xls", ".xlsb", ".ods"}:
            excel_file = pd.ExcelFile(path)

            try:
                return excel_file.sheet_names
            finally:
                excel_file.close()

        raise ValueError(
            f"Unable to determine sheets for: {extension}"
        )

    @staticmethod
    def read_file(
        file_path: str | Path,
        sheet_name: Optional[str] = None
    ) -> Dataset:
        """
        Read a spreadsheet into a Dataset object.
        """

        path = FileManager.validate_file(file_path)

        extension = path.suffix.lower()

        if extension == ".csv":
            dataframe = pd.read_csv(
                path,
                encoding="utf-8-sig"
            )

            return Dataset(
                dataframe=dataframe,
                source_file=path
            )

        if extension == ".tsv":
            dataframe = pd.read_csv(
                path,
                sep="\t",
                encoding="utf-8-sig"
            )

            return Dataset(
                dataframe=dataframe,
                source_file=path
            )

        if extension == ".xlsx":
            dataframe = pd.read_excel(
                path,
                sheet_name=sheet_name or 0,
                engine="openpyxl"
            )

            actual_sheet = (
                sheet_name
                if sheet_name is not None
                else pd.ExcelFile(path).sheet_names[0]
            )

            return Dataset(
                dataframe=dataframe,
                source_file=path,
                sheet_name=actual_sheet
            )

        if extension == ".xls":
            dataframe = pd.read_excel(
                path,
                sheet_name=sheet_name or 0,
                engine="xlrd"
            )

            actual_sheet = (
                sheet_name
                if sheet_name is not None
                else pd.ExcelFile(path).sheet_names[0]
            )

            return Dataset(
                dataframe=dataframe,
                source_file=path,
                sheet_name=actual_sheet
            )

        if extension == ".ods":
            dataframe = pd.read_excel(
                path,
                sheet_name=sheet_name or 0,
                engine="odf"
            )

            actual_sheet = (
                sheet_name
                if sheet_name is not None
                else pd.ExcelFile(path).sheet_names[0]
            )

            return Dataset(
                dataframe=dataframe,
                source_file=path,
                sheet_name=actual_sheet
            )

        if extension == ".xlsb":
            dataframe = pd.read_excel(
                path,
                sheet_name=sheet_name or 0,
                engine="pyxlsb"
            )

            actual_sheet = (
                sheet_name
                if sheet_name is not None
                else pd.ExcelFile(path).sheet_names[0]
            )

            return Dataset(
                dataframe=dataframe,
                source_file=path,
                sheet_name=actual_sheet
            )

        raise ValueError(
            f"Unsupported file format: {extension}"
        )

    @staticmethod
    def write_file(
        dataset: Dataset,
        output_path: str | Path,
        sheet_name: str = "Sheet1"
    ) -> Path:
        """
        Write a Dataset to a new file.

        This method NEVER modifies the source file.
        """

        path = Path(output_path)

        extension = path.suffix.lower()

        if extension == ".csv":
            dataset.dataframe.to_csv(
                path,
                index=False,
                encoding="utf-8-sig"
            )

        elif extension == ".tsv":
            dataset.dataframe.to_csv(
                path,
                sep="\t",
                index=False,
                encoding="utf-8-sig"
            )

        elif extension == ".xlsx":
            dataset.dataframe.to_excel(
                path,
                index=False,
                sheet_name=sheet_name,
                engine="openpyxl"
            )

        elif extension == ".ods":
            dataset.dataframe.to_excel(
                path,
                index=False,
                sheet_name=sheet_name,
                engine="odf"
            )

        else:
            raise ValueError(
                f"Writing to '{extension}' is not supported yet."
            )

        return path