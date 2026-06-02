"""
feature_engineering.py

This file builds behavioral UEBA features from preprocessed logs.

The features are aggregated by user and day, for example:
- number of logon events per day
- number of activities outside working hours
- number of different PCs used
- number of USB events
- number of file events
- number of unique files accessed

These features will be used by the anomaly detection model.
"""


def build_logon_features(logon_df):
    """
    Build daily logon features by user.
    """
    features = logon_df.groupby(["user", "day"]).agg(
        logon_events=("activity", "count"),
        logon_outside_hours=("outside_working_hours", "sum"),
        unique_logon_pcs=("pc", "nunique"),
    ).reset_index()

    return features


def build_device_features(device_df):
    """
    Build daily USB/device features by user.
    """
    features = device_df.groupby(["user", "day"]).agg(
        usb_events=("activity", "count"),
        usb_outside_hours=("outside_working_hours", "sum"),
        unique_usb_pcs=("pc", "nunique"),
    ).reset_index()

    return features


def build_file_features(file_df):
    """
    Build daily file activity features by user.
    """
    features = file_df.groupby(["user", "day"]).agg(
        file_events=("activity", "count"),
        file_outside_hours=("outside_working_hours", "sum"),
        unique_files=("filename", "nunique"),
    ).reset_index()

    return features


def merge_features(logon_features, device_features, file_features):
    """
    Merge all behavioral features into one UEBA feature table.
    """
    features = logon_features.merge(
        device_features,
        on=["user", "day"],
        how="outer"
    )

    features = features.merge(
        file_features,
        on=["user", "day"],
        how="outer"
    )

    features = features.fillna(0)

    return features