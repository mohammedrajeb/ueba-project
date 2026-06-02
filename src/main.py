"""
main.py

Main entry point of the UEBA project.

Current step:
- Load samples from CERT r4.2 logs
- Apply preprocessing
- Build behavioral features by user and day
- Apply the rule-based UEBA risk engine
- Apply Isolation Forest anomaly detection
- Apply final risk analysis
- Display final UEBA alerts
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
from src.risk_analyzer import apply_risk_analysis


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


def test_risk_analyzer(sample_size: int = 10000):
    """
    Test the full scoring pipeline:
    features -> rules -> Isolation Forest -> final risk analysis.
    """
    print("UEBA project - Final risk analyzer test")
    print(f"Sample size per file: {sample_size}")

    ueba_features = build_sample_features(sample_size=sample_size)

    print("\nApplying rule engine...")
    rule_scored_features = apply_rule_engine(ueba_features)

    print("\nApplying Isolation Forest...")
    ml_scored_features, _, _ = apply_isolation_forest(
        rule_scored_features,
        contamination=0.02
    )

    print("\nApplying final risk analysis...")
    final_alerts = apply_risk_analysis(ml_scored_features)

    print("\nFinal alerts shape:")
    print(final_alerts.shape)

    print("\nRisk level distribution:")
    print(final_alerts["risk_level"].value_counts())

    print("\nRisk score statistics:")
    print(final_alerts["risk_score"].describe())

    risky_alerts = final_alerts[final_alerts["risk_score"] > 0]

    print("\nNumber of alerts with risk_score > 0:")
    print(len(risky_alerts))

    print("\nTop critical alerts:")
    print(
        risky_alerts.sort_values("risk_score", ascending=False)
        [
            [
                "user",
                "day",
                "risk_score",
                "risk_level",
                "alert_reason",
                "rule_score",
                "is_anomaly",
                "anomaly_score",
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
    test_risk_analyzer(sample_size=10000)


if __name__ == "__main__":
    main()