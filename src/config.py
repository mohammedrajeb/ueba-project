"""
config.py

This file centralizes the main configuration of the UEBA project.

It contains:
- paths to raw data
- paths to processed data
- paths to generated alerts
- model parameters
- risk scoring thresholds
- Elasticsearch configuration

The goal is to avoid hardcoding paths and parameters in multiple scripts.
"""

from pathlib import Path


# Root directory of the project
ROOT_DIR = Path(__file__).resolve().parents[1]

# Data directories
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
ALERTS_DATA_DIR = DATA_DIR / "alerts"

# Model directory
MODELS_DIR = ROOT_DIR / "models"

# Main CERT r4.2 log files
LOGON_FILE = RAW_DATA_DIR / "logon.csv"
DEVICE_FILE = RAW_DATA_DIR / "device.csv"
FILE_FILE = RAW_DATA_DIR / "file.csv"
HTTP_FILE = RAW_DATA_DIR / "http.csv"
EMAIL_FILE = RAW_DATA_DIR / "email.csv"

# Output files
UEBA_FEATURES_FILE = PROCESSED_DATA_DIR / "ueba_features.csv"
ALERTS_FILE = ALERTS_DATA_DIR / "alerts.csv"

# Working hours used to detect abnormal activity
WORKING_HOUR_START = 7
WORKING_HOUR_END = 20

# Risk thresholds
LOW_RISK_THRESHOLD = 30
MEDIUM_RISK_THRESHOLD = 60
HIGH_RISK_THRESHOLD = 80

# Elasticsearch configuration
ELASTICSEARCH_HOST = "http://localhost:9200"
ELASTICSEARCH_INDEX = "ueba-alerts"