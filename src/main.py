"""
main.py

Main entry point of the UEBA project.

This script runs the complete UEBA pipeline:

1. Load samples from CERT r4.2 logs
2. Apply preprocessing
3. Build behavioral features by user and day
4. Optionally include HTTP/web behavior features
5. Optionally include email behavior features
6. Apply the rule-based UEBA risk engine
7. Apply Isolation Forest anomaly detection
8. Optionally apply TensorFlow Autoencoder anomaly detection
9. Apply final risk analysis
10. Optionally enrich results with LDAP context
11. Export local results:
    - data/processed/ueba_features.csv
    - data/alerts/alerts.csv
12. Optionally send alerts to Elasticsearch
13. Optionally save trained models in the models/ directory

Examples:
    python -m src.main --sample-size 10000
    python -m src.main --sample-size 10000 --include-http
    python -m src.main --sample-size 10000 --include-email
    python -m src.main --sample-size 10000 --include-ldap
    python -m src.main --sample-size 10000 --include-http --include-email --include-ldap
    python -m src.main --sample-size 10000 --include-http --include-email --include-ldap --use-autoencoder
    python -m src.main --sample-size 10000 --include-http --include-email --include-ldap --use-autoencoder --send-to-elasticsearch
    python -m src.main --sample-size 10000 --include-http --include-email --include-ldap --use-autoencoder --send-to-elasticsearch --save-models
"""

import argparse
import json
from datetime import datetime

import joblib

from src.config import (
    ALERTS_DATA_DIR,
    ALERTS_FILE,
    AUTOENCODER_BATCH_SIZE,
    AUTOENCODER_EPOCHS,
    AUTOENCODER_MODEL_FILE,
    AUTOENCODER_SCALER_FILE,
    AUTOENCODER_THRESHOLD_PERCENTILE,
    DEVICE_FILE,
    EMAIL_FILE,
    FILE_FILE,
    HTTP_FILE,
    ISOLATION_FOREST_CONTAMINATION,
    ISOLATION_FOREST_MODEL_FILE,
    ISOLATION_FOREST_SCALER_FILE,
    LDAP_DIR,
    LOGON_FILE,
    MODEL_METADATA_FILE,
    MODELS_DIR,
    PROCESSED_DATA_DIR,
    UEBA_FEATURES_FILE,
)
from src.autoencoder_model import apply_autoencoder
from src.context_enrichment import enrich_with_ldap_context
from src.elastic_connector import send_alerts_to_elasticsearch
from src.feature_engineering import (
    build_device_features,
    build_email_features,
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
    include_email: bool = False,
):
    """
    Load samples, preprocess logs and build behavioral features.

    Parameters:
        sample_size: number of rows loaded from each CERT r4.2 log file
        include_http: if True, include HTTP/web behavior features from http.csv
        include_email: if True, include email behavior features from email.csv

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

    email_sample = None
    if include_email:
        print("Loading Email sample...")
        email_sample = preview_csv(EMAIL_FILE, nrows=sample_size)

    print("Preprocessing samples...")
    logon_processed = preprocess_log(logon_sample)
    device_processed = preprocess_log(device_sample)
    file_processed = preprocess_log(file_sample)

    http_processed = None
    if include_http and http_sample is not None:
        http_processed = preprocess_log(http_sample)

    email_processed = None
    if include_email and email_sample is not None:
        email_processed = preprocess_log(email_sample)

    print("Building behavioral features...")
    logon_features = build_logon_features(logon_processed)
    device_features = build_device_features(device_processed)
    file_features = build_file_features(file_processed)

    http_features = None
    if include_http and http_processed is not None:
        print("Building HTTP behavior features...")
        http_features = build_http_features(http_processed)

    email_features = None
    if include_email and email_processed is not None:
        print("Building Email behavior features...")
        email_features = build_email_features(email_processed)

    ueba_features = merge_behavioral_features(
        logon_features,
        device_features,
        file_features,
        http_features=http_features,
        email_features=email_features,
    )

    return ueba_features


def save_trained_models(
    isolation_forest_model,
    isolation_forest_scaler,
    autoencoder_model=None,
    autoencoder_scaler=None,
    metadata: dict | None = None,
):
    """
    Save trained models and scalers in the models/ directory.

    Files saved:
    - isolation_forest_model.pkl
    - isolation_forest_scaler.pkl
    - autoencoder_model.keras, if Autoencoder is enabled
    - autoencoder_scaler.pkl, if Autoencoder is enabled
    - model_metadata.json
    """
    print("\nSaving trained models...")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(isolation_forest_model, ISOLATION_FOREST_MODEL_FILE)
    joblib.dump(isolation_forest_scaler, ISOLATION_FOREST_SCALER_FILE)

    print(f"Isolation Forest model saved to: {ISOLATION_FOREST_MODEL_FILE}")
    print(f"Isolation Forest scaler saved to: {ISOLATION_FOREST_SCALER_FILE}")

    if autoencoder_model is not None and autoencoder_scaler is not None:
        autoencoder_model.save(AUTOENCODER_MODEL_FILE)
        joblib.dump(autoencoder_scaler, AUTOENCODER_SCALER_FILE)

        print(f"Autoencoder model saved to: {AUTOENCODER_MODEL_FILE}")
        print(f"Autoencoder scaler saved to: {AUTOENCODER_SCALER_FILE}")

    if metadata is None:
        metadata = {}

    metadata["saved_at"] = datetime.now().isoformat(timespec="seconds")
    metadata["isolation_forest_model_file"] = str(ISOLATION_FOREST_MODEL_FILE)
    metadata["isolation_forest_scaler_file"] = str(ISOLATION_FOREST_SCALER_FILE)

    if autoencoder_model is not None:
        metadata["autoencoder_model_file"] = str(AUTOENCODER_MODEL_FILE)
        metadata["autoencoder_scaler_file"] = str(AUTOENCODER_SCALER_FILE)

    with open(MODEL_METADATA_FILE, "w", encoding="utf-8") as metadata_file:
        json.dump(metadata, metadata_file, indent=4)

    print(f"Model metadata saved to: {MODEL_METADATA_FILE}")


def run_pipeline(
    sample_size: int = 10000,
    send_to_elasticsearch: bool = False,
    use_autoencoder: bool = False,
    include_http: bool = False,
    include_email: bool = False,
    include_ldap: bool = False,
    save_models: bool = False,
):
    """
    Run the complete UEBA pipeline on a sample of the CERT r4.2 logs.

    Parameters:
        sample_size: number of rows loaded from each raw log file
        send_to_elasticsearch: if True, send generated alerts to Elasticsearch
        use_autoencoder: if True, apply TensorFlow Autoencoder anomaly detection
        include_http: if True, include HTTP/web behavior features
        include_email: if True, include email behavior features
        include_ldap: if True, enrich final results with LDAP context
        save_models: if True, save trained models in the models/ directory
    """
    print("UEBA project - Full pipeline with local export")
    print(f"Sample size per file: {sample_size}")
    print(f"Include HTTP logs: {include_http}")
    print(f"Include Email logs: {include_email}")
    print(f"Include LDAP context: {include_ldap}")
    print(f"Use TensorFlow Autoencoder: {use_autoencoder}")
    print(f"Send to Elasticsearch: {send_to_elasticsearch}")
    print(f"Save trained models: {save_models}")

    ueba_features = build_sample_features(
        sample_size=sample_size,
        include_http=include_http,
        include_email=include_email,
    )

    print("\nApplying rule engine...")
    rule_scored_features = apply_rule_engine(ueba_features)

    print("\nApplying Isolation Forest...")
    ml_scored_features, isolation_forest_model, isolation_forest_scaler = (
        apply_isolation_forest(
            rule_scored_features,
            contamination=ISOLATION_FOREST_CONTAMINATION,
        )
    )

    autoencoder_model = None
    autoencoder_scaler = None

    if use_autoencoder:
        print("\nApplying TensorFlow Autoencoder...")
        ml_scored_features, autoencoder_model, autoencoder_scaler = apply_autoencoder(
            ml_scored_features,
            epochs=AUTOENCODER_EPOCHS,
            batch_size=AUTOENCODER_BATCH_SIZE,
            threshold_percentile=AUTOENCODER_THRESHOLD_PERCENTILE,
        )

        print("\nAutoencoder anomaly distribution:")
        print(ml_scored_features["autoencoder_is_anomaly"].value_counts())

        print("\nAutoencoder reconstruction error statistics:")
        print(ml_scored_features["autoencoder_reconstruction_error"].describe())

    print("\nApplying final risk analysis...")
    final_results = apply_risk_analysis(ml_scored_features)

    if include_ldap:
        print("\nEnriching results with LDAP context...")
        final_results = enrich_with_ldap_context(
            final_results,
            ldap_dir=LDAP_DIR,
        )

    print("\nFiltering alerts with risk_score > 0...")
    alerts = final_results[final_results["risk_score"] > 0].copy()

    print("\nCreating output directories if needed...")
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    ALERTS_DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("\nExporting UEBA features...")
    final_results.to_csv(UEBA_FEATURES_FILE, index=False)

    print("\nExporting UEBA alerts...")
    alerts.to_csv(ALERTS_FILE, index=False)

    if save_models:
        model_metadata = {
            "sample_size": sample_size,
            "include_http": include_http,
            "include_email": include_email,
            "include_ldap": include_ldap,
            "use_autoencoder": use_autoencoder,
            "send_to_elasticsearch": send_to_elasticsearch,
            "features_shape": list(final_results.shape),
            "alerts_shape": list(alerts.shape),
            "risk_level_distribution": final_results["risk_level"]
            .value_counts()
            .to_dict(),
            "isolation_forest_contamination": ISOLATION_FOREST_CONTAMINATION,
            "autoencoder_epochs": AUTOENCODER_EPOCHS if use_autoencoder else None,
            "autoencoder_batch_size": AUTOENCODER_BATCH_SIZE
            if use_autoencoder
            else None,
            "autoencoder_threshold_percentile": AUTOENCODER_THRESHOLD_PERCENTILE
            if use_autoencoder
            else None,
        }

        save_trained_models(
            isolation_forest_model=isolation_forest_model,
            isolation_forest_scaler=isolation_forest_scaler,
            autoencoder_model=autoencoder_model,
            autoencoder_scaler=autoencoder_scaler,
            metadata=model_metadata,
        )

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

    if include_email:
        top_alert_columns.extend(
            [
                "email_events",
                "email_outside_hours",
                "total_email_size",
                "avg_email_size",
                "total_attachments",
                "emails_with_attachments",
                "bcc_recipients_count",
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

    if include_ldap:
        top_alert_columns.extend(
            [
                "employee_name",
                "role",
                "position",
                "business_unit",
                "functional_unit",
                "department",
                "team",
                "supervisor",
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

    parser.add_argument(
        "--include-email",
        action="store_true",
        help="Include email behavior features from email.csv.",
    )

    parser.add_argument(
        "--include-ldap",
        action="store_true",
        help="Enrich UEBA results with LDAP organizational context.",
    )

    parser.add_argument(
        "--save-models",
        action="store_true",
        help="Save trained models and scalers in the models/ directory.",
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
        include_email=args.include_email,
        include_ldap=args.include_ldap,
        save_models=args.save_models,
    )


if __name__ == "__main__":
    main()