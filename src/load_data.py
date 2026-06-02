"""
load_data.py

This file contains the functions used to load and inspect the CERT r4.2 log files.

The first goal is not to load the full dataset immediately, because some files
are large. Instead, this module provides safe preview functions to inspect:
- file existence
- file size
- columns
- first rows

Main CERT r4.2 logs used in version 1:
- logon.csv
- device.csv
- file.csv
"""

from pathlib import Path

import pandas as pd


def get_file_size_mb(file_path: Path) -> float:
    """
    Return the size of a file in megabytes.

    Parameters:
        file_path: path to the file

    Returns:
        File size in MB
    """
    return file_path.stat().st_size / (1024 * 1024)


def preview_csv(file_path: Path, nrows: int = 5) -> pd.DataFrame:
    """
    Read only the first rows of a CSV file.

    This is useful for large log files because it avoids loading
    the entire dataset into memory.

    Parameters:
        file_path: path to the CSV file
        nrows: number of rows to preview

    Returns:
        pandas DataFrame containing the first rows
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return pd.read_csv(file_path, nrows=nrows)


def inspect_csv(file_path: Path, name: str, nrows: int = 5) -> None:
    """
    Display basic information about a CSV file.

    Parameters:
        file_path: path to the CSV file
        name: display name of the dataset
        nrows: number of rows to preview
    """
    print("\n" + "=" * 80)
    print(f"Inspecting: {name}")
    print("=" * 80)

    if not file_path.exists():
        print(f"File not found: {file_path}")
        return

    print(f"Path: {file_path}")
    print(f"Size: {get_file_size_mb(file_path):.2f} MB")

    df_preview = preview_csv(file_path, nrows=nrows)

    print(f"Columns: {list(df_preview.columns)}")
    print(f"Preview rows: {len(df_preview)}")
    print(df_preview.head(nrows))