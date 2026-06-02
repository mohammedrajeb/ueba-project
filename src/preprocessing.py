"""
preprocessing.py

This file contains preprocessing functions for CERT r4.2 logs.

It is used to:
- convert date columns to datetime format
- extract day, hour, month and weekday
- detect activities outside working hours
- clean missing values
- standardize raw logs before feature engineering

The output of this module will be used to build behavioral UEBA features.
"""

import pandas as pd

from src.config import WORKING_HOUR_START, WORKING_HOUR_END


def convert_date_column(df: pd.DataFrame, date_column: str = "date") -> pd.DataFrame:
    """
    Convert the date column to pandas datetime format.

    Parameters:
        df: input DataFrame
        date_column: name of the date column

    Returns:
        DataFrame with converted date column
    """
    df = df.copy()
    df[date_column] = pd.to_datetime(df[date_column], errors="coerce")
    return df


def add_time_features(df: pd.DataFrame, date_column: str = "date") -> pd.DataFrame:
    """
    Add time-based features from the date column.

    Created features:
    - day
    - hour
    - month
    - weekday
    - is_weekend

    Parameters:
        df: input DataFrame
        date_column: name of the date column

    Returns:
        DataFrame with additional time features
    """
    df = df.copy()

    df["day"] = df[date_column].dt.date
    df["hour"] = df[date_column].dt.hour
    df["month"] = df[date_column].dt.month
    df["weekday"] = df[date_column].dt.day_name()
    df["is_weekend"] = df[date_column].dt.weekday.apply(
        lambda day: 1 if day >= 5 else 0
    )

    return df


def add_outside_working_hours_flag(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a binary flag indicating whether the activity occurred outside working hours.

    Returns:
        DataFrame with outside_working_hours column
    """
    df = df.copy()

    df["outside_working_hours"] = df["hour"].apply(
        lambda hour: 1 if hour < WORKING_HOUR_START or hour > WORKING_HOUR_END else 0
    )

    return df


def clean_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove rows with invalid or missing dates.

    Other missing values are kept for now because they may carry useful information
    depending on the log type.
    """
    df = df.copy()
    df = df.dropna(subset=["date"])
    return df


def preprocess_log(df: pd.DataFrame, date_column: str = "date") -> pd.DataFrame:
    """
    Apply the complete preprocessing pipeline to one log DataFrame.

    Steps:
    1. Convert date column
    2. Remove rows with invalid dates
    3. Add time-based features
    4. Add outside working hours flag

    Parameters:
        df: raw log DataFrame
        date_column: date column name

    Returns:
        preprocessed DataFrame
    """
    df = convert_date_column(df, date_column=date_column)
    df = clean_missing_values(df)
    df = add_time_features(df, date_column=date_column)
    df = add_outside_working_hours_flag(df)

    return df