"""
context_enrichment.py

This file enriches UEBA results with contextual information.

Current enrichment:
- LDAP organizational data

LDAP data is not used directly to calculate the risk score.
It is used to add context to alerts, such as employee name, role,
business unit, department, team or supervisor when available.

This helps analysts understand who generated an alert and where the user
belongs in the organization.
"""

from pathlib import Path
from typing import List

import pandas as pd


def load_ldap_files(ldap_dir: Path) -> pd.DataFrame:
    """
    Load all LDAP CSV files from a directory and combine them.

    Parameters:
        ldap_dir: path to the LDAP directory

    Returns:
        Combined LDAP DataFrame
    """
    if not ldap_dir.exists():
        raise FileNotFoundError(f"LDAP directory not found: {ldap_dir}")

    ldap_files = sorted(ldap_dir.glob("*.csv"))

    if not ldap_files:
        raise FileNotFoundError(f"No LDAP CSV files found in: {ldap_dir}")

    frames = []

    for file_path in ldap_files:
        df = pd.read_csv(file_path)
        df["ldap_source_file"] = file_path.name
        frames.append(df)

    combined_ldap = pd.concat(frames, ignore_index=True)

    return combined_ldap


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize LDAP column names to make matching easier.

    Example:
        Employee Name -> employee_name
        user_id -> user_id
    """
    normalized_df = df.copy()

    normalized_df.columns = [
        str(column).strip().lower().replace(" ", "_")
        for column in normalized_df.columns
    ]

    return normalized_df


def find_user_id_column(df: pd.DataFrame) -> str:
    """
    Find the column that contains the CERT user identifier.

    In the CERT dataset, this is usually 'user_id'.
    This function is defensive in case the column name varies.
    """
    possible_columns = [
        "user_id",
        "userid",
        "user",
        "employee_id",
        "id",
    ]

    for column in possible_columns:
        if column in df.columns:
            return column

    raise KeyError(
        "Could not find a user identifier column in LDAP data. "
        "Expected one of: user_id, userid, user, employee_id, id."
    )


def select_context_columns(df: pd.DataFrame, user_id_column: str) -> List[str]:
    """
    Select useful LDAP columns if they exist.

    The function keeps only the columns that can help explain alerts.
    """
    useful_columns = [
        user_id_column,
        "employee_name",
        "name",
        "email",
        "role",
        "position",
        "business_unit",
        "functional_unit",
        "department",
        "team",
        "supervisor",
        "manager",
        "ldap_source_file",
    ]

    selected_columns = [
        column for column in useful_columns
        if column in df.columns
    ]

    return selected_columns


def build_latest_ldap_context(ldap_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build one LDAP context row per user.

    Since the LDAP directory contains monthly snapshots, this function keeps
    the last available record for each user based on the source filename order.

    Returns:
        DataFrame with one row per user
    """
    df = normalize_column_names(ldap_df)

    user_id_column = find_user_id_column(df)

    selected_columns = select_context_columns(df, user_id_column)

    df = df[selected_columns].copy()

    df = df.sort_values("ldap_source_file")

    latest_context = df.drop_duplicates(
        subset=[user_id_column],
        keep="last"
    ).copy()

    latest_context = latest_context.rename(columns={user_id_column: "user"})

    if "employee_name" not in latest_context.columns and "name" in latest_context.columns:
        latest_context = latest_context.rename(columns={"name": "employee_name"})

    if "manager" in latest_context.columns and "supervisor" not in latest_context.columns:
        latest_context = latest_context.rename(columns={"manager": "supervisor"})

    return latest_context


def enrich_with_ldap_context(
    ueba_df: pd.DataFrame,
    ldap_dir: Path,
) -> pd.DataFrame:
    """
    Enrich UEBA results with LDAP user context.

    Parameters:
        ueba_df: DataFrame containing UEBA features, scores and alerts
        ldap_dir: path to LDAP directory

    Returns:
        Enriched DataFrame
    """
    df = ueba_df.copy()

    ldap_df = load_ldap_files(ldap_dir)
    ldap_context = build_latest_ldap_context(ldap_df)

    enriched_df = df.merge(
        ldap_context,
        on="user",
        how="left",
    )

    return enriched_df