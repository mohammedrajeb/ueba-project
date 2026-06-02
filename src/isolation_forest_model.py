"""
isolation_forest_model.py

This file contains the main machine learning model of the UEBA project:
Isolation Forest.

Isolation Forest is an unsupervised anomaly detection model.
It is suitable for UEBA because malicious behaviors are rare compared to normal behaviors.

The model will detect unusual user-day behaviors from behavioral features.
"""

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


def train_isolation_forest(features_df, metadata_columns=None):
    """
    Train an Isolation Forest model on behavioral features.

    Parameters:
        features_df: DataFrame containing UEBA features
        metadata_columns: columns not used for training, such as user and day

    Returns:
        features_df with anomaly predictions and scores
        trained model
        fitted scaler
    """
    if metadata_columns is None:
        metadata_columns = ["user", "day", "rule_reasons"]

    df = features_df.copy()

    X = df.drop(columns=[col for col in metadata_columns if col in df.columns], errors="ignore")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(
        n_estimators=100,
        contamination=0.02,
        random_state=42
    )

    df["anomaly_prediction"] = model.fit_predict(X_scaled)
    df["anomaly_score"] = model.decision_function(X_scaled)

    df["is_anomaly"] = df["anomaly_prediction"].apply(
        lambda value: 1 if value == -1 else 0
    )

    return df, model, scaler