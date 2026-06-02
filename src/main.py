"""
main.py

Main entry point of the UEBA project.

Current step:
- Load samples from CERT r4.2 logs
- Apply preprocessing
- Build behavioral features by user and day
- Apply the rule-based UEBA risk engine
- Apply Isolation Forest anomaly detection
- Display anomalies detected by the AI model
"""

from src.config import DEVICE_FILE, FILE_FILE, LOGON_FILE
from src.load_data import preview_csv
from src.preprocessing import preprocess_log
from src.feature_engineering import (
    build_device_features,
    build_file_features,
    build_logon_features,
    merge_behavioral_features,
)
from src.rule_engine import apply_rule_engine
from src.isolation_forest_model import apply_isolation_forest


def build_sample_features(sample_size: int = 10000):
    """
    Load samples, preprocess logs and build behavioral features.
    """
    print("Loading samples...")
    logon_sample = preview_csv(LOGON_FILE, nrows=sample_size)
    device_sample = preview_csv(DEVICE_FILE, nrows=sample_size)
    file_sample = preview_csv(FILE_FILE, nrows=sample_size)

    print("Preprocessing samples...")
    logon_processed = preprocess_log(logon_sample)
    device_processed = preprocess_log(device_sample)
    file_processed = preprocess_log(file_sample)

    print("Building behavioral features...")
    logon_features = build_logon_features(logon_processed)
    device_features = build_device_features(device_processed)
    file_features = build_file_features(file_processed)

    ueba_features = merge_behavioral_features(
        logon_features,
        device_features,
        file_features
    )

    return ueba_features


def test_isolation_forest(sample_size: int = 10000):
    """
    Test the rule engine and Isolation Forest model on UEBA features.
    """
    print("UEBA project - Isolation Forest test")
    print(f"Sample size per file: {sample_size}")

    ueba_features = build_sample_features(sample_size=sample_size)

    print("\nApplying rule engine...")
    scored_features = apply_rule_engine(ueba_features)

    print("\nApplying Isolation Forest...")
    ml_scored_features, _, _ = apply_isolation_forest(
        scored_features,
        contamination=0.02
    )

    print("\nFinal scored features shape:")
    print(ml_scored_features.shape)

    print("\nAnomaly prediction distribution:")
    print(ml_scored_features["anomaly_prediction"].value_counts())

    print("\nNumber of AI anomalies:")
    print(ml_scored_features["is_anomaly"].sum())

    print("\nAnomaly score statistics:")
    print(ml_scored_features["anomaly_score"].describe())

    anomalies = ml_scored_features[ml_scored_features["is_anomaly"] == 1]

    print("\nTop AI anomalies:")
    print(
        anomalies.sort_values("anomaly_score", ascending=True)
        [
            [
                "user",
                "day",
                "rule_score",
                "rule_reasons",
                "anomaly_prediction",
                "anomaly_score",
                "is_anomaly",
                "logon_outside_hours",
                "usb_events",
                "usb_outside_hours",
                "file_copy_events",
                "file_copy_outside_hours",
                "unique_logon_pcs",
            ]
        ]
        .head(10)
    )


def main():
    """
    Run the current UEBA pipeline step.
    """
    test_isolation_forest(sample_size=10000)


if __name__ == "__main__":
    main()