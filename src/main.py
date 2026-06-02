"""
main.py

Main entry point of the UEBA project.

Current step:
- Inspect CERT r4.2 logs
- Load small samples from logon.csv, device.csv and file.csv
- Apply preprocessing
- Verify generated time-based features
"""

from src.config import DEVICE_FILE, FILE_FILE, LOGON_FILE
from src.load_data import inspect_csv, preview_csv
from src.preprocessing import preprocess_log


def inspect_raw_logs():
    """
    Inspect raw CERT r4.2 log files.
    """
    print("UEBA project - CERT r4.2 raw log inspection")

    inspect_csv(LOGON_FILE, "logon.csv")
    inspect_csv(DEVICE_FILE, "device.csv")
    inspect_csv(FILE_FILE, "file.csv")


def test_preprocessing():
    """
    Test preprocessing on small samples of the three main logs.
    """
    print("\n" + "#" * 80)
    print("Testing preprocessing on log samples")
    print("#" * 80)

    logon_sample = preview_csv(LOGON_FILE, nrows=5)
    device_sample = preview_csv(DEVICE_FILE, nrows=5)
    file_sample = preview_csv(FILE_FILE, nrows=5)

    logon_processed = preprocess_log(logon_sample)
    device_processed = preprocess_log(device_sample)
    file_processed = preprocess_log(file_sample)

    print("\nProcessed logon sample:")
    print(logon_processed[["date", "day", "hour", "month", "weekday", "is_weekend", "outside_working_hours"]])

    print("\nProcessed device sample:")
    print(device_processed[["date", "day", "hour", "month", "weekday", "is_weekend", "outside_working_hours"]])

    print("\nProcessed file sample:")
    print(file_processed[["date", "day", "hour", "month", "weekday", "is_weekend", "outside_working_hours"]])


def main():
    """
    Run the current UEBA pipeline step.
    """
    inspect_raw_logs()
    test_preprocessing()


if __name__ == "__main__":
    main()