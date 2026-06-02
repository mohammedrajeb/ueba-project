"""
feature_engineering.py

This file builds behavioral UEBA features from preprocessed CERT r4.2 logs.

The goal is to aggregate raw events by user and day.

Main feature groups:
- Logon behavior
- USB/device behavior
- File copy behavior
- HTTP/web behavior

The resulting feature table will be used by:
- the rule-based risk engine
- the Isolation Forest anomaly detection model
- the TensorFlow Autoencoder anomaly detection model
"""

import pandas as pd


def build_logon_features(logon_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build daily logon features by user.

    Features created:
    - logon_events: number of Logon events
    - logoff_events: number of Logoff events
    - logon_outside_hours: number of logon/logoff events outside working hours
    - unique_logon_pcs: number of different PCs used by the user
    """
    df = logon_df.copy()

    features = df.groupby(["user", "day"]).agg(
        logon_events=("activity", lambda x: (x == "Logon").sum()),
        logoff_events=("activity", lambda x: (x == "Logoff").sum()),
        logon_outside_hours=("outside_working_hours", "sum"),
        unique_logon_pcs=("pc", "nunique"),
    ).reset_index()

    return features


def build_device_features(device_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build daily USB/device features by user.

    Features created:
    - usb_events: total number of device events
    - usb_connect_events: number of Connect events
    - usb_disconnect_events: number of Disconnect events
    - usb_outside_hours: number of USB events outside working hours
    - unique_usb_pcs: number of different PCs where USB activity occurred
    """
    df = device_df.copy()

    features = df.groupby(["user", "day"]).agg(
        usb_events=("activity", "count"),
        usb_connect_events=("activity", lambda x: (x == "Connect").sum()),
        usb_disconnect_events=("activity", lambda x: (x == "Disconnect").sum()),
        usb_outside_hours=("outside_working_hours", "sum"),
        unique_usb_pcs=("pc", "nunique"),
    ).reset_index()

    return features


def build_file_features(file_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build daily file copy features by user.

    In CERT r4.2, each row in file.csv represents a file copy
    to a removable media device.

    Features created:
    - file_copy_events: total number of copied files
    - file_copy_outside_hours: number of file copies outside working hours
    - unique_files_copied: number of unique filenames copied
    - unique_file_pcs: number of different PCs used for file copies
    """
    df = file_df.copy()

    features = df.groupby(["user", "day"]).agg(
        file_copy_events=("filename", "count"),
        file_copy_outside_hours=("outside_working_hours", "sum"),
        unique_files_copied=("filename", "nunique"),
        unique_file_pcs=("pc", "nunique"),
    ).reset_index()

    return features


def extract_domain(url: str) -> str:
    """
    Extract a simple domain from a URL.

    This function keeps the implementation lightweight and avoids adding
    external dependencies.

    Example:
        http://example.com/page -> example.com
    """
    if not isinstance(url, str):
        return "unknown"

    cleaned_url = url.replace("http://", "").replace("https://", "")
    domain = cleaned_url.split("/")[0]

    return domain if domain else "unknown"


def build_http_features(http_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build daily HTTP behavior features by user.

    Features created:
    - http_events: total number of HTTP events
    - http_outside_hours: number of HTTP events outside working hours
    - unique_urls: number of unique visited URLs
    - unique_domains: number of unique visited domains
    - unique_http_pcs: number of PCs used for HTTP activity
    """
    df = http_df.copy()

    if "url" not in df.columns:
        raise KeyError("The HTTP log must contain a 'url' column.")

    df["domain"] = df["url"].apply(extract_domain)

    features = df.groupby(["user", "day"]).agg(
        http_events=("url", "count"),
        http_outside_hours=("outside_working_hours", "sum"),
        unique_urls=("url", "nunique"),
        unique_domains=("domain", "nunique"),
        unique_http_pcs=("pc", "nunique"),
    ).reset_index()

    return features


def merge_behavioral_features(
    logon_features: pd.DataFrame,
    device_features: pd.DataFrame,
    file_features: pd.DataFrame,
    http_features: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """
    Merge logon, device, file copy and optional HTTP features
    into one UEBA feature table.

    The merge is done using:
    - user
    - day

    Missing values are replaced with 0 because absence of activity
    means no event was recorded for that feature on that day.
    """
    features = logon_features.merge(
        device_features,
        on=["user", "day"],
        how="outer",
    )

    features = features.merge(
        file_features,
        on=["user", "day"],
        how="outer",
    )

    if http_features is not None:
        features = features.merge(
            http_features,
            on=["user", "day"],
            how="outer",
        )

    features = features.fillna(0)

    return features