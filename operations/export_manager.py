
from datetime import datetime
from pathlib import Path

from core.dataset import Dataset
from core.file_manager import FileManager


class ExportManager:

    SUPPORTED_FORMATS = {
        "xlsx": ".xlsx",
        "ods": ".ods",
        "csv": ".csv",
        "tsv": ".tsv",
    }

    @staticmethod
    def export(
        dataset: Dataset,
        output_format: str = "xlsx",
        output_directory: str | Path = "output",
        filename_prefix: str | None = None,
    ) -> Path:
        output_format = output_format.lower().strip().lstrip(".")

        if output_format not in ExportManager.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported output format: {output_format}"
            )

        output_dir = Path(output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)

        if filename_prefix is None:
            filename_prefix = dataset.source_file.stem

        # Make the prefix safe for filenames.
        safe_prefix = "".join(
            ch if ch.isalnum() or ch in "-_"
            else "_"
            for ch in filename_prefix
        ).strip("_")

        if not safe_prefix:
            safe_prefix = "spreadsheet_result"

        extension = ExportManager.SUPPORTED_FORMATS[output_format]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        candidate = output_dir / (
            f"{safe_prefix}_{timestamp}{extension}"
        )

        # Add a counter if two exports happen within the same second.
        counter = 1
        while candidate.exists():
            candidate = output_dir / (
                f"{safe_prefix}_{timestamp}_{counter}{extension}"
            )
            counter += 1

        # A final guard against accidentally targeting the source.
        if candidate.resolve() == dataset.source_file.resolve():
            raise ValueError(
                "Output path must not be the original input file."
            )

        FileManager.write_file(
            dataset,
            candidate,
            sheet_name="Results",
        )

        return candidate
