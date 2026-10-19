
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

import pandas as pd

from core.dataset import Dataset


class LandAreaOperation:
    """Convert and calculate land areas in Kanal-Marla-Foot format."""

    MARLA_PER_KANAL = 20
    DEFAULT_SQFT_PER_MARLA = 272

    @staticmethod
    def _validate_standard(sqft_per_marla=272):
        if not isinstance(sqft_per_marla, int) or sqft_per_marla <= 0:
            raise ValueError("Square feet per Marla must be a positive integer.")

    @staticmethod
    def to_square_feet(area, sqft_per_marla=272):
        """
        Convert K-M-F text such as '10-10-0' to total square feet.
        Also accepts a three-item tuple/list: (10, 10, 0).
        """
        LandAreaOperation._validate_standard(sqft_per_marla)

        if isinstance(area, (tuple, list)):
            parts = area
        else:
            parts = str(area).strip().split("-")

        if len(parts) != 3:
            raise ValueError(
                f"Invalid area '{area}'. Use Kanal-Marla-Foot, e.g. 10-10-0."
            )

        try:
            kanal, marla, foot = [int(str(part).strip()) for part in parts]
        except (ValueError, TypeError):
            raise ValueError(
                f"Invalid area '{area}'. Each part must be a whole number."
            )

        if kanal < 0 or marla < 0 or foot < 0:
            raise ValueError("Area values cannot be negative.")

        return (
            kanal * LandAreaOperation.MARLA_PER_KANAL * sqft_per_marla
            + marla * sqft_per_marla
            + foot
        )

    @staticmethod
    def from_square_feet(total_sqft, sqft_per_marla=272):
        """Convert total square feet into normalized K-M-F text."""
        LandAreaOperation._validate_standard(sqft_per_marla)

        try:
            total = Decimal(str(total_sqft)).quantize(
                Decimal("1"),
                rounding=ROUND_HALF_UP,
            )
        except (InvalidOperation, ValueError):
            raise ValueError("Total square feet must be a valid number.")

        if total < 0:
            raise ValueError("Total area cannot be negative.")

        total = int(total)
        sqft_per_kanal = (
            LandAreaOperation.MARLA_PER_KANAL * sqft_per_marla
        )

        kanal, remainder = divmod(total, sqft_per_kanal)
        marla, foot = divmod(remainder, sqft_per_marla)

        return f"{kanal}-{marla}-{foot}"

    @staticmethod
    def add_areas(areas, sqft_per_marla=272):
        """Add multiple K-M-F areas and return normalized K-M-F."""
        total = sum(
            LandAreaOperation.to_square_feet(area, sqft_per_marla)
            for area in areas
        )
        return LandAreaOperation.from_square_feet(total, sqft_per_marla)

    @staticmethod
    def subtract_areas(area1, area2, sqft_per_marla=272):
        """Subtract area2 from area1. Negative land area is not allowed."""
        total1 = LandAreaOperation.to_square_feet(
            area1, sqft_per_marla
        )
        total2 = LandAreaOperation.to_square_feet(
            area2, sqft_per_marla
        )

        if total2 > total1:
            raise ValueError("The result would be a negative land area.")

        return LandAreaOperation.from_square_feet(
            total1 - total2, sqft_per_marla
        )

    @staticmethod
    def calculate_share(
        total_area,
        share,
        sqft_per_marla=272,
    ):
        """
        Calculate a fractional ownership share.
        Examples of share: '2/5', '1/3', '0.25'.
        The result is rounded to the nearest whole square foot.
        """
        total_sqft = LandAreaOperation.to_square_feet(
            total_area, sqft_per_marla
        )

        # try:
        #     share_value = Decimal(str(share).strip())

        #     if "/" in str(share).strip():
        #         numerator, denominator = str(share).strip().split("/")
        #         share_value = Decimal(numerator.strip()) / Decimal(
        #             denominator.strip()
        #         )
        # except (InvalidOperation, ValueError, ZeroDivisionError):
        #     raise ValueError("Enter a valid share, such as 2/5 or 0.25.")

        
        try:
            share_text = str(share).strip()

            if "/" in share_text:
                numerator, denominator = share_text.split("/", 1)
                denominator_value = Decimal(denominator.strip())

                if denominator_value == 0:
                    raise ValueError("Share denominator cannot be zero.")

                share_value = (
                    Decimal(numerator.strip()) / denominator_value
                )
            else:
                share_value = Decimal(share_text)

        except (InvalidOperation, ValueError, ZeroDivisionError):
            raise ValueError(
                "Enter a valid share, such as 2/5, 1/3, or 0.25."
            )


        if share_value < 0 or share_value > 1:
            raise ValueError("Share must be between 0 and 1.")

        share_sqft = (
            Decimal(total_sqft) * share_value
        ).quantize(Decimal("1"), rounding=ROUND_HALF_UP)

        return LandAreaOperation.from_square_feet(
            int(share_sqft), sqft_per_marla
        )

    @staticmethod
    def _new_dataset(dataset, dataframe):
        return Dataset(
            dataframe=dataframe,
            source_file=dataset.source_file,
            sheet_name=dataset.sheet_name,
        )

    @staticmethod
    def add_area_columns(
        dataset,
        source_column,
        sqft_column="Area_SqFt",
        normalized_column="Area_KMF",
        sqft_per_marla=272,
    ):
        """
        Add total square feet and normalized K-M-F columns.
        Invalid or blank cells become blank results rather than stopping
        the entire spreadsheet operation.
        """
        df = dataset.dataframe.copy()

        if source_column not in df.columns:
            raise ValueError(f"Column '{source_column}' does not exist.")

        if sqft_column in df.columns or normalized_column in df.columns:
            raise ValueError(
                "An output column already exists. Choose new column names."
            )

        LandAreaOperation._validate_standard(sqft_per_marla)

        def convert(value):
            if pd.isna(value) or str(value).strip() == "":
                return None
            try:
                return LandAreaOperation.to_square_feet(
                    value, sqft_per_marla
                )
            except ValueError:
                return None

        df[sqft_column] = df[source_column].map(convert)

        df[normalized_column] = df[sqft_column].map(
            lambda value: (
                LandAreaOperation.from_square_feet(
                    value, sqft_per_marla
                )
                if pd.notna(value)
                else None
            )
        )

        return LandAreaOperation._new_dataset(dataset, df)

    @staticmethod
    def add_share_columns(
        dataset,
        area_column,
        share_column,
        result_column="Share_Area_KMF",
        sqft_per_marla=272,
    ):
        """
        Calculate area shares from an area column and a share column.
        Share cells can contain values such as 2/5, 1/3, or 0.25.
        """
        df = dataset.dataframe.copy()

        for column in (area_column, share_column):
            if column not in df.columns:
                raise ValueError(f"Column '{column}' does not exist.")

        if result_column in df.columns:
            raise ValueError(
                f"Column '{result_column}' already exists."
            )

        LandAreaOperation._validate_standard(sqft_per_marla)

        def calculate_row(row):
            area = row[area_column]
            share = row[share_column]

            if pd.isna(area) or pd.isna(share):
                return None

            try:
                return LandAreaOperation.calculate_share(
                    area,
                    share,
                    sqft_per_marla,
                )
            except (ValueError, TypeError):
                return None

        df[result_column] = df.apply(calculate_row, axis=1)

        return LandAreaOperation._new_dataset(dataset, df)
