"""
data_processing.py
------------------
Data loading and preprocessing module for the Carbon-Aware Electricity
Production Analysis mini-project.

Handles:
- Automated CSV loading from project folder
- Datetime parsing and chronological sorting
- Duplicate timestamp detection and removal
- Missing value imputation (time-series forward/backward fill)
- Negative wind value investigation and non-negative generation alignment
- Incomplete year detection (e.g., partial year 2026)
"""

import os
import pandas as pd
import streamlit as st

DATASET_FILENAME = "electricityConsumptionAndProductioction_modified.csv"

# Canonical energy source columns in the dataset
ENERGY_SOURCES = [
    "Nuclear",
    "Wind",
    "Hydroelectric",
    "Oil and Gas",
    "Coal",
    "Solar",
    "Biomass",
]

RENEWABLE_SOURCES = ["Wind", "Hydroelectric", "Solar", "Biomass"]
NON_RENEWABLE_SOURCES = ["Coal", "Oil and Gas", "Nuclear"]


@st.cache_data
def load_and_preprocess_data(csv_path: str = None):
    """
    Loads and cleans the electricity dataset from the project folder.
    
    Returns:
        df (pd.DataFrame): Preprocessed DataFrame.
        metadata (dict): Preprocessing inspection statistics and metadata.
    """
    if csv_path is None:
        # Resolve path relative to current working directory
        csv_path = DATASET_FILENAME
        if not os.path.exists(csv_path):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            csv_path = os.path.join(base_dir, DATASET_FILENAME)

    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"Dataset not found at '{csv_path}'. Please ensure '{DATASET_FILENAME}' "
            f"is placed in the project root directory."
        )

    # 1. Load CSV
    df = pd.read_csv(csv_path)
    total_raw_rows = len(df)

    # Record initial missing values
    initial_nulls = df.isnull().sum().to_dict()

    # 2. Datetime Conversion
    df["DateTime"] = pd.to_datetime(df["DateTime"], errors="coerce")

    # Drop any row where DateTime could not be parsed
    df = df.dropna(subset=["DateTime"])

    # 3. Sort Chronologically
    df = df.sort_values("DateTime").reset_index(drop=True)

    # 4. Duplicate Timestamps
    initial_duplicates = int(df["DateTime"].duplicated().sum())
    # Keep the first occurrence of duplicate timestamps
    df = df.drop_duplicates(subset=["DateTime"], keep="first").reset_index(drop=True)

    # 5. Missing Values Handling
    # In continuous hourly power systems data, forward-fill followed by backward-fill
    # preserves temporal continuity without inventing artificial external trends.
    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
    df[numeric_cols] = df[numeric_cols].ffill().bfill()

    # 6. Negative Wind Investigation & Generation Alignment
    # Wind turbines consume small amounts of power (auxiliary / parasitic load for yaw motors,
    # control electronics, heaters) when wind speeds are below cut-in speed, resulting in
    # small negative net generation readings (-1 to -26 MWh).
    negative_wind_count = int((df["Wind"] < 0).sum())
    min_wind_val = float(df["Wind"].min())

    # For physical generation and emission share calculations, electricity production
    # cannot be negative. We clip negative source values at 0 for generation accounting
    # while preserving original behavior.
    for src in ENERGY_SOURCES:
        if src in df.columns:
            df[src] = df[src].clip(lower=0.0)

    # Recompute total production from energy sources to ensure consistency
    df["Production_Cleaned"] = df[ENERGY_SOURCES].sum(axis=1)

    # 7. Temporal Features
    df["Year"] = df["DateTime"].dt.year
    df["Month"] = df["DateTime"].dt.month
    df["Month_Name"] = df["DateTime"].dt.strftime("%B")
    df["Day"] = df["DateTime"].dt.day
    df["Hour"] = df["DateTime"].dt.hour

    # 8. Identify Incomplete Years
    # A full leap year has 8,784 hours, regular year has 8,760 hours.
    # Years with fewer than 8,000 hours or fewer than 12 months are marked incomplete.
    year_summary = df.groupby("Year").agg(
        hours=("DateTime", "count"),
        months=("Month", "nunique"),
        first_date=("DateTime", "min"),
        last_date=("DateTime", "max"),
    )
    incomplete_years = {}
    for yr, row in year_summary.iterrows():
        if row["months"] < 12 or row["hours"] < 8000:
            incomplete_years[int(yr)] = {
                "hours": int(row["hours"]),
                "months": int(row["months"]),
                "start": row["first_date"].strftime("%Y-%m-%d"),
                "end": row["last_date"].strftime("%Y-%m-%d"),
                "note": (
                    f"{yr} contains partial data ({row['months']} months, "
                    f"{row['hours']:,} hours from {row['first_date'].strftime('%b %d')} "
                    f"to {row['last_date'].strftime('%b %d')}) and should not be "
                    f"interpreted as a complete annual dataset."
                ),
            }

    metadata = {
        "total_raw_rows": total_raw_rows,
        "total_clean_rows": len(df),
        "initial_nulls": initial_nulls,
        "initial_duplicates": initial_duplicates,
        "negative_wind_count": negative_wind_count,
        "min_wind_val": min_wind_val,
        "date_range": (
            df["DateTime"].min().strftime("%Y-%m-%d %H:%M"),
            df["DateTime"].max().strftime("%Y-%m-%d %H:%M"),
        ),
        "incomplete_years": incomplete_years,
        "available_years": sorted(df["Year"].unique().tolist()),
    }

    return df, metadata


def get_available_years(df: pd.DataFrame) -> list:
    """Returns sorted list of distinct years present in the dataset."""
    return sorted(df["Year"].unique().tolist())


def check_incomplete_year(year: int, metadata: dict) -> tuple[bool, str]:
    """
    Checks if a given year is incomplete.
    
    Returns:
        (is_incomplete (bool), message (str))
    """
    incomplete_dict = metadata.get("incomplete_years", {})
    if year in incomplete_dict:
        return True, incomplete_dict[year]["note"]
    return False, ""
