"""
main.py

Main entry point of the UEBA project.

Current step:
- Load samples from CERT r4.2 logs
- Apply preprocessing
- Build behavioral features by user and day
- Display the generated UEBA feature table

This step validates the feature engineering logic before processing
larger parts of the dataset.
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


def test_feature_engineering(sample_size: int = 10000):
    """
    Test feature engineering on log samples.

    A sample is used first to avoid loading very large files during testing.
    """
    print("UEBA project - Feature engineering test")
    print(f"Sample size per file: {sample_size}")

    print("\nLoading samples...")
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

    print("\nLogon features preview:")
    print(logon_features.head())

    print("\nDevice features preview:")
    print(device_features.head())

    print("\nFile copy features preview:")
    print(file_features.head())

    print("\nMerging all behavioral features...")
    ueba_features = merge_behavioral_features(
        logon_features,
        device_features,
        file_features
    )

    print("\nFinal UEBA features shape:")
    print(ueba_features.shape)

    print("\nFinal UEBA features preview:")
    print(ueba_features.head())

    print("\nFinal UEBA feature columns:")
    print(list(ueba_features.columns))


def main():
    """
    Run the current UEBA pipeline step.
    """
    test_feature_engineering(sample_size=10000)


if __name__ == "__main__":
    main()