"""
main.py

Main entry point of the UEBA project.

Current step:
- Inspect the CERT r4.2 raw log files
- Verify that logon.csv, device.csv and file.csv are accessible
- Display file size, columns and first rows

This step validates the local data setup before building preprocessing
and feature engineering modules.
"""

from src.config import DEVICE_FILE, FILE_FILE, LOGON_FILE
from src.load_data import inspect_csv


def main():
    """
    Run the current UEBA pipeline step.
    """
    print("UEBA project - CERT r4.2 log inspection")

    inspect_csv(LOGON_FILE, "logon.csv")
    inspect_csv(DEVICE_FILE, "device.csv")
    inspect_csv(FILE_FILE, "file.csv")


if __name__ == "__main__":
    main()