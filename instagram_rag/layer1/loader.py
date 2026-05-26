"""Reads and validates the Instagram analytics CSV."""

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

REQUIRED_COLUMNS: list[str] = [
    "post_id",
    "upload_date",
    "media_type",
    "likes",
    "comments",
    "shares",
    "saves",
    "reach",
    "impressions",
    "caption_length",
    "hashtags_count",
    "followers_gained",
    "traffic_source",
    "engagement_rate",
    "content_category",
]

NUMERIC_COLUMNS: list[str] = [
    "likes",
    "comments",
    "shares",
    "saves",
    "reach",
    "impressions",
    "caption_length",
    "hashtags_count",
    "followers_gained",
    "engagement_rate",
]


def load_csv(path: Path) -> list[dict[str, Any]]:
    """Load and validate the Instagram CSV.

    Args:
        path: Path to the CSV file.

    Returns:
        List of clean row dicts ready for the processor.

    Raises:
        FileNotFoundError: If the CSV does not exist at the given path.
        ValueError: If required columns are missing.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found at '{path}'. "
            "Place your CSV at data/instagram_dataset.csv and re-run."
        )

    df = pd.read_csv(path)

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(
            f"CSV is missing required columns: {missing}\n"
            f"Found columns: {list(df.columns)}"
        )

    df["upload_date"] = pd.to_datetime(df["upload_date"], errors="coerce")

    for col in NUMERIC_COLUMNS:
        if col == "engagement_rate":
            df[col] = pd.to_numeric(df[col], errors="coerce").astype(float)
        else:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    rows: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        record = row.to_dict()
        if isinstance(record.get("upload_date"), pd.Timestamp):
            record["upload_date"] = record["upload_date"].isoformat()
        for col in NUMERIC_COLUMNS:
            val = record.get(col)
            if pd.isna(val):
                record[col] = None
            elif col != "engagement_rate":
                record[col] = int(val) if val is not None else None
        rows.append(record)

    return rows
