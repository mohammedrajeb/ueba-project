"""
preprocessing.py

This file contains preprocessing functions for CERT r4.2 logs.

It will be used to:
- convert date columns to datetime format
- extract hour, day, month, and weekday
- detect activities outside working hours
- clean missing values
- standardize columns before feature engineering

Preprocessing transforms raw logs into usable structured data.
"""

import pandas as pd

from src.config import WORKING_HOUR_START, WORKING_HOUR_END


def preprocess_dates(df, date_column="date"):
    """
    Convert the date column to datetime and extract useful time features.

    Parameters:
        df: pandas DataFrame
        date_column: name of the date column

    Returns:
        pandas.DataFrame with new time-related columns
    """
    df = df.copy()

    df[date_column] = pd.to_datetime(df[date_column], errors="coerce")

    df["day"] = df[date_column].dt.date
    df["hour"] = df[date_column].dt.hour
    df["month"] = df[date_column].dt.month
    df["weekday"] = df[date_column].dt.day_name()

    return df


def add_outside_working_hours_flag(df):
    """
    Add a binary flag indicating whether the activity occurred outside working hours.

    Returns:
        pandas.DataFrame
    """
    df = df.copy()

    df["outside_working_hours"] = df["hour"].apply(
        lambda hour: 1 if hour < WORKING_HOUR_START or hour > WORKING_HOUR_END else 0
    )

    return df