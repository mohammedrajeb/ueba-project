"""
main.py

Main entry point of the UEBA project.

This script runs the complete UEBA pipeline:

1. Load samples from CERT r4.2 logs
2. Apply preprocessing
3. Build behavioral features by user and day
4. Apply the rule-based UEBA risk engine
5. Apply Isolation Forest anomaly detection
6. Apply final risk analysis
7. Export local results:
    - data/processed/ueba_features.csv
    - data/alerts/alerts.csv
8. Optionally send alerts to Elasticsearch

Examples:
    python -m src.main --sample-size 10000
    python -m src.main --sample-size 50000 --send-to-elasticsearch
"""

import argparse

from src.config import (
    ALERTS_FILE,
    DEVICE_FILE,
    FILE_FILE,
    LOGON_FILE,
    PROCESSED_DATA_DIR,
    ALERTS_DATA_DIR,
    UEBA_FEATURES_FILE,
)
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
from src.elastic_connector import send_alerts_to_elasticsearch


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


def run_pipeline(sample_size: int = 10000, send_to_elasticsearch: bool = False):
    """
    Run the complete UEBA pipeline on a sample of the CERT r4.2 logs.

    Steps:
    1. Build behavioral features
    2. Apply rule-based scoring
    3. Apply Isolation Forest
    4. Apply final risk analysis
    5. Export features and alerts locally
    6. Optionally send alerts to Elasticsearch
    """
    print("UEBA project - Full pipeline with local export")
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
    final_results = apply_risk_analysis(ml_scored_features)

    print("\nFiltering alerts with risk_score > 0...")
    alerts = final_results[final_results["risk_score"] > 0].copy()

    print("\nCreating output directories if needed...")
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    ALERTS_DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("\nExporting UEBA features...")
    final_results.to_csv(UEBA_FEATURES_FILE, index=False)

    print("\nExporting UEBA alerts...")
    alerts.to_csv(ALERTS_FILE, index=False)

    if send_to_elasticsearch:
        print("\nSending alerts to Elasticsearch...")
        send_alerts_to_elasticsearch(alerts, reset=True)

    print("\nExport completed successfully.")
    print(f"Features saved to: {UEBA_FEATURES_FILE}")
    print(f"Alerts saved to: {ALERTS_FILE}")

    print("\nFinal results shape:")
    print(final_results.shape)

    print("\nAlerts shape:")
    print(alerts.shape)

    print("\nRisk level distribution:")
    print(final_results["risk_level"].value_counts())

    print("\nTop alerts:")
    print(
        alerts.sort_values("risk_score", ascending=False)
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
            ]
        ]
        .head(10)
    )


def parse_arguments():
    """
    Parse command-line arguments for the UEBA pipeline.

    Returns:
        argparse.Namespace containing the selected options
    """
    parser = argparse.ArgumentParser(
        description="Run the UEBA pipeline on CERT r4.2 logs."
    )

    parser.add_argument(
        "--sample-size",
        type=int,
        default=10000,
        help="Number of rows to load from each raw log file. Default: 10000."
    )

    parser.add_argument(
        "--send-to-elasticsearch",
        action="store_true",
        help="Send generated alerts to Elasticsearch."
    )

    return parser.parse_args()


def main():
    """
    Run the UEBA pipeline with command-line parameters.
    """
    args = parse_arguments()

    run_pipeline(
        sample_size=args.sample_size,
        send_to_elasticsearch=args.send_to_elasticsearch
    )


if __name__ == "__main__":
    main()