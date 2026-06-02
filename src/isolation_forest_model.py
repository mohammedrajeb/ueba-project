"""
isolation_forest_model.py

This file contains the main machine learning model of the UEBA project:
Isolation Forest.

Isolation Forest is an unsupervised anomaly detection model.
It is useful for UEBA because suspicious insider behaviors are rare compared
to normal daily user behaviors.

The model uses behavioral features such as:
- logon activity
- USB activity
- file copy activity
- outside working hours activity
"""

from typing import List, Tuple

import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


def get_training_columns(features_df: pd.DataFrame, excluded_columns: List[str]) -> List[str]:
    """
    Select numeric columns used for model training.

    Parameters:
        features_df: UEBA feature DataFrame
        excluded_columns: columns to exclude from training

    Returns:
        List of numeric feature column names
    """
    candidate_columns = [
        column for column in features_df.columns
        if column not in excluded_columns
    ]

    numeric_columns = features_df[candidate_columns].select_dtypes(
        include=["number"]
    ).columns.tolist()

    return numeric_columns


def apply_isolation_forest(
    features_df: pd.DataFrame,
    contamination: float = 0.02,
    random_state: int = 42
) -> Tuple[pd.DataFrame, IsolationForest, StandardScaler]:
    """
    Train and apply Isolation Forest on UEBA behavioral features.

    Parameters:
        features_df: DataFrame containing behavioral features
        contamination: expected proportion of anomalies
        random_state: random seed for reproducibility

    Returns:
        scored_df: DataFrame with anomaly predictions and scores
        model: trained Isolation Forest model
        scaler: fitted StandardScaler
    """
    df = features_df.copy()

    excluded_columns = [
        "user",
        "day",
        "rule_reasons",
    ]

    training_columns = get_training_columns(df, excluded_columns)

    if not training_columns:
        raise ValueError("No numeric columns available for Isolation Forest training.")

    X = df[training_columns]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=random_state
    )

    df["anomaly_prediction"] = model.fit_predict(X_scaled)

    # decision_function: higher values are more normal, lower values are more abnormal
    df["anomaly_score"] = model.decision_function(X_scaled)

    df["is_anomaly"] = df["anomaly_prediction"].apply(
        lambda value: 1 if value == -1 else 0
    )

    return df, model, scaler