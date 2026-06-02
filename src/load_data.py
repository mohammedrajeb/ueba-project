"""
load_data.py

This file contains the functions used to load the CERT r4.2 log files.

It will be responsible for reading:
- logon.csv
- device.csv
- file.csv
- http.csv
- email.csv

The goal is to centralize data loading before preprocessing and feature engineering.
"""

import pandas as pd


def load_csv(file_path):
    """
    Load a CSV file and return it as a pandas DataFrame.

    Parameters:
        file_path: path to the CSV file

    Returns:
        pandas.DataFrame
    """
    return pd.read_csv(file_path)


def preview_dataframe(df, name="DataFrame"):
    """
    Display basic information about a DataFrame.

    Parameters:
        df: pandas DataFrame
        name: name of the DataFrame
    """
    print(f"\n===== {name} =====")
    print("Shape:", df.shape)
    print("Columns:", list(df.columns))
    print(df.head())