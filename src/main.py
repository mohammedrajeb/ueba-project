"""
main.py

Main entry point of the UEBA project.

Current step:
- Load samples from CERT r4.2 logs
- Apply preprocessing
- Build behavioral features by user and day
- Apply the rule-based UEBA risk engine
- Display risky behaviors detected by rules
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


def test_rule_engine(sample_size: int = 10000):
    """
    Test the rule-based UEBA scoring engine.
    """
    print("UEBA project - Rule engine test")
    print(f"Sample size per file: {sample_size}")

    ueba_features = build_sample_features(sample_size=sample_size)

    print("\nApplying rule engine...")
    scored_features = apply_rule_engine(ueba_features)

    print("\nScored UEBA features shape:")
    print(scored_features.shape)

    print("\nRule score distribution:")
    print(scored_features["rule_score"].describe())

    risky_behaviors = scored_features[scored_features["rule_score"] > 0]

    print("\nNumber of risky behaviors detected by rules:")
    print(len(risky_behaviors))

    print("\nTop risky behaviors:")
    print(
        risky_behaviors.sort_values("rule_score", ascending=False)
        [
            [
                "user",
                "day",
                "rule_score",
                "rule_reasons",
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
    test_rule_engine(sample_size=10000)


if __name__ == "__main__":
    main()