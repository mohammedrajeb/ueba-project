"""
main.py

Main entry point of the UEBA project.

This script runs the complete UEBA pipeline:

1. Load samples from CERT r4.2 logs
2. Apply preprocessing
3. Build behavioral features by user and day
4. Optionally include HTTP/web behavior features
5. Apply the rule-based UEBA risk engine
6. Apply Isolation Forest anomaly detection
7. Optionally apply TensorFlow Autoencoder anomaly detection
8. Apply final risk analysis
9. Export local results:
    - data/processed/ueba_features.csv
    - data/alerts/alerts.csv
10. Optionally send alerts to Elasticsearch

Examples:
    python -m src.main --sample-size 10000
    python -m src.main --sample-size 50000
    python -m src.main --sample-size 10000 --include-http
    python -m src.main --sample-size 10000 --use-autoencoder
    python -m src.main --sample-size 10000 --include-http --use-autoencoder
    python -m src.main --sample-size 10000 --include-http --use-autoencoder --send-to-elasticsearch
"""

import argparse

from src.config import (
    ALERTS_DATA_DIR,
    ALERTS_FILE,
    DEVICE_FILE,
    FILE_FILE,
    HTTP_FILE,
    LOGON_FILE,
    PROCESSED_DATA_DIR,
    UEBA_FEATURES_FILE,
)
from src.autoencoder_model import apply_autoencoder
from src.elastic_connector import send_alerts_to_elasticsearch
from src.feature_engineering import (
    build_device_features,
    build_file_features,
    build_http_features,
    build_logon_features,
    merge_behavioral_features,
)
from src.isolation_forest_model import apply_isolation_forest
from src.load_data import preview_csv
from src.preprocessing import preprocess_log
from src.risk_analyzer import apply_risk_analysis
from src.rule_engine import apply_rule_engine


def build_sample_features(
    sample_size: int = 10000,
    include_http: bool = False,
):
    """
    Load samples, preprocess logs and build behavioral features.

    Parameters:
        sample_size: number of rows loaded from each CERT r4.2 log file
        include_http: if True, include HTTP/web behavior features from http.csv

    Returns:
        DataFrame containing UEBA behavioral features
    """
    print("Loading samples...")
    logon_sample = preview_csv(LOGON_FILE, nrows=sample_size)
    device_sample = preview_csv(DEVICE_FILE, nrows=sample_size)
    file_sample = preview_csv(FILE_FILE, nrows=sample_size)

    http_sample = None
    if include_http:
        print("Loading HTTP sample...")
        http_sample = preview_csv(HTTP_FILE, nrows=sample_size)

    print("Preprocessing samples...")
    logon_processed = preprocess_log(logon_sample)
    device_processed = preprocess_log(device_sample)
    file_processed = preprocess_log(file_sample)

    http_processed = None
    if include_http and http_sample is not None:
        http_processed = preprocess_log(http_sample)

    print("Building behavioral features...")
    logon_features = build_logon_features(logon_processed)
    device_features = build_device_features(device_processed)
    file_features = build_file_features(file_processed)

    http_features = None
    if include_http and http_processed is not None:
        print("Building HTTP behavior features...")
        http_features = build_http_features(http_processed)

    ueba_features = merge_behavioral_features(
        logon_features,
        device_features,
        file_features,
        http_features=http_features,
    )

    return ueba_features


def run_pipeline(
    sample_size: int = 10000,
    send_to_elasticsearch: bool = False,
    use_autoencoder: bool = False,
    include_http: bool = False,
):
    """
    Run the complete UEBA pipeline on a sample of the CERT r4.2 logs.

    Steps:
    1. Build behavioral features
    2. Optionally include HTTP behavior features
    3. Apply rule-based scoring
    4. Apply Isolation Forest
    5. Optionally apply TensorFlow Autoencoder
    6. Apply final risk analysis
    7. Export features and alerts locally
    8. Optionally send alerts to Elasticsearch

    Parameters:
        sample_size: number of rows loaded from each raw log file
        send_to_elasticsearch: if True, send generated alerts to Elasticsearch
        use_autoencoder: if True, apply TensorFlow Autoencoder anomaly detection
        include_http: if True, include HTTP/web behavior features
    """
    print("UEBA project - Full pipeline with local export")
    print(f"Sample size per file: {sample_size}")
    print(f"Include HTTP logs: {include_http}")
    print(f"Use TensorFlow Autoencoder: {use_autoencoder}")
    print(f"Send to Elasticsearch: {send_to_elasticsearch}")

    ueba_features = build_sample_features(
        sample_size=sample_size,
        include_http=include_http,
    )

    print("\nApplying rule engine...")
    rule_scored_features = apply_rule_engine(ueba_features)

    print("\nApplying Isolation Forest...")
    ml_scored_features, _, _ = apply_isolation_forest(
        rule_scored_features,
        contamination=0.02,
    )

    if use_autoencoder:
        print("\nApplying TensorFlow Autoencoder...")
        ml_scored_features, _, _ = apply_autoencoder(
            ml_scored_features,
            epochs=30,
            batch_size=32,
            threshold_percentile=98.0,
        )

        print("\nAutoencoder anomaly distribution:")
        print(ml_scored_features["autoencoder_is_anomaly"].value_counts())

        print("\nAutoencoder reconstruction error statistics:")
        print(ml_scored_features["autoencoder_reconstruction_error"].describe())

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

    top_alert_columns = [
        "user",
        "day",
        "risk_score",
        "risk_level",
        "alert_reason",
        "rule_score",
        "is_anomaly",
        "anomaly_score",
    ]

    if include_http:
        top_alert_columns.extend(
            [
                "http_events",
                "http_outside_hours",
                "unique_urls",
                "unique_domains",
            ]
        )

    if use_autoencoder:
        top_alert_columns.extend(
            [
                "autoencoder_is_anomaly",
                "autoencoder_reconstruction_error",
                "autoencoder_threshold",
            ]
        )

    existing_top_alert_columns = [
        column for column in top_alert_columns
        if column in alerts.columns
    ]

    print("\nTop alerts:")
    print(
        alerts.sort_values("risk_score", ascending=False)[existing_top_alert_columns]
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
        help="Number of rows to load from each raw log file. Default: 10000.",
    )

    parser.add_argument(
        "--send-to-elasticsearch",
        action="store_true",
        help="Send generated alerts to Elasticsearch.",
    )

    parser.add_argument(
        "--use-autoencoder",
        action="store_true",
        help="Apply TensorFlow Autoencoder anomaly detection.",
    )

    parser.add_argument(
        "--include-http",
        action="store_true",
        help="Include HTTP behavior features from http.csv.",
    )

    return parser.parse_args()


def main():
    """
    Run the UEBA pipeline with command-line parameters.
    """
    args = parse_arguments()

    run_pipeline(
        sample_size=args.sample_size,
        send_to_elasticsearch=args.send_to_elasticsearch,
        use_autoencoder=args.use_autoencoder,
        include_http=args.include_http,
    )


if __name__ == "__main__":
    main()