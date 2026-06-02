# UEBA Security Project

> **User and Entity Behavior Analytics (UEBA)** — CERT Insider Threat Dataset r4.2
> **Stack :** Python · Scikit-learn · TensorFlow · Elasticsearch · Grafana · Docker

This project implements a full UEBA pipeline, from raw log ingestion to alert visualization and context enrichment.

---

## Project Structure

```
ueba-project/
│
├── data/
│   ├── raw/                        # Raw CERT logs : logon, device, file, http, email, LDAP
│   ├── processed/                  # Processed UEBA features
│   └── alerts/                     # Generated UEBA alerts
│
├── dashboards/
│   └── grafana_dashboard.json      # Exported Grafana dashboard
│
├── reports/
│   ├── rapport_analytique.md       # Project analytical report
│   └── figures/
│       └── Dashboard.png           # Grafana dashboard screenshot
│
├── src/
│   ├── config.py                   # Central configuration and paths
│   ├── load_data.py                # Secure CSV file loading
│   ├── preprocessing.py            # Date parsing and temporal features
│   ├── feature_engineering.py      # Logon, device, file, HTTP, email features
│   ├── rule_engine.py              # Rule-based risk scoring
│   ├── isolation_forest_model.py   # Isolation Forest anomaly detection
│   ├── autoencoder_model.py        # TensorFlow Autoencoder anomaly detection
│   ├── risk_analyzer.py            # Final risk score computation
│   ├── context_enrichment.py       # LDAP context enrichment
│   ├── elastic_connector.py        # Elasticsearch indexing
│   └── main.py                     # Pipeline entry point
│
└── README.md
```

---

## Pipeline Overview

```
Logs CERT r4.2
      ↓
Prétraitement
      ↓
Feature Engineering (logon · device · file · http · email)
      ↓
Rule Engine
      ↓
Isolation Forest
      ↓
TensorFlow Autoencoder
      ↓
Risk Analyzer
      ↓
LDAP Context Enrichment
      ↓
Export CSV  →  Elasticsearch  →  Grafana Dashboard
```

---

## Features

### 1. Behavioral Feature Engineering

Features aggregated per `user + day` from five log sources :

| Source       | Features extracted                                          |
|--------------|-------------------------------------------------------------|
| `logon.csv`  | Logon/logoff events, outside-hours activity, unique PCs     |
| `device.csv` | USB connect/disconnect events, outside-hours, unique PCs    |
| `file.csv`   | File copy events, outside-hours copies, unique files/PCs    |
| `http.csv`   | HTTP events, outside-hours, unique URLs/domains/PCs         |
| `email.csv`  | Email volume, attachments, BCC usage, outside-hours, size   |

### 2. Rule-Based Risk Scoring

Generates a preliminary `rule_score` based on domain rules covering outside-hours activity, USB usage, file copies, multi-PC usage, and dangerous combinations.

### 3. Anomaly Detection

| Model                    | Approach                                          |
|--------------------------|---------------------------------------------------|
| Isolation Forest         | Unsupervised anomaly detection (`contamination=0.02`) |
| TensorFlow Autoencoder   | Reconstruction-error anomaly detection (threshold: 98th percentile) |

### 4. LDAP Context Enrichment

Maps user attributes from LDAP snapshots : `department`, `team`, `role`, `position`, `supervisor`, `functional_unit`.

### 5. Final Risk Analysis

Combines rule score and anomaly signals to compute :

| Output         | Description                            |
|----------------|----------------------------------------|
| `risk_score`   | Final score from 0 to 100              |
| `risk_level`   | `low` / `medium` / `high` / `critical` |
| `alert_reason` | Human-readable explanation             |

Risk level thresholds :

| Score      | Level      |
|------------|------------|
| 0 à 30     | `low`      |
| 31 à 60    | `medium`   |
| 61 à 80    | `high`     |
| 81 à 100   | `critical` |

---

## Running the Pipeline

```bash
# Activate your environment
conda activate ueba_env

# Full pipeline with all features
python -m src.main \
  --sample-size 10000 \
  --include-http \
  --include-email \
  --include-ldap \
  --use-autoencoder \
  --send-to-elasticsearch
```

| Flag                      | Description                              |
|---------------------------|------------------------------------------|
| `--sample-size N`         | Number of rows per file to process       |
| `--include-http`          | Include HTTP log features                |
| `--include-email`         | Include email log features               |
| `--include-ldap`          | Enable LDAP context enrichment           |
| `--use-autoencoder`       | Apply TensorFlow Autoencoder             |
| `--send-to-elasticsearch` | Push alerts to Elasticsearch             |

Output files :

```
data/processed/ueba_features.csv   →  All analyzed behaviors
data/alerts/alerts.csv             →  Alerts with risk_score > 0
```

---

## Grafana Dashboard

The dashboard provides **9 panels** to monitor UEBA alerts, connected to Elasticsearch index `ueba-alerts`.

| Panel                              | Description                                    |
|------------------------------------|------------------------------------------------|
| Total Alerts                       | Total number of indexed alerts                 |
| Critical Alerts                    | Alerts classified as critical                  |
| Alerts by Risk Level               | Distribution of alerts by risk level           |
| Top Risky Users                    | Users generating the most alerts               |
| Recent Alerts                      | Detailed alert table sorted by risk score      |
| Alerts by Department               | Alerts grouped by LDAP department              |
| Top Supervisors by Alerts          | Alerts grouped by supervisor                   |
| TensorFlow Autoencoder Anomalies   | Anomalies detected by the Autoencoder          |
| Alerts with Email Activity         | Alerts containing email activity               |

![UEBA Grafana Dashboard](reports/figures/Dashboard.png)

---

## Results — Sample Run (10 000 rows/file)

| Metric                              | Value  |
|-------------------------------------|-------:|
| Behaviors analyzed (user/day)       |  4 816 |
| Total alerts generated              |  1 704 |
| Critical alerts                     |     93 |
| Alerts with email activity          |    366 |
| TensorFlow Autoencoder anomalies    |     97 |
| Final feature columns               |     50 |

Distribution by risk level :

| Level      | Count  |
|------------|-------:|
| `low`      |  4 388 |
| `medium`   |    307 |
| `high`     |     28 |
| `critical` |     93 |

---

## Status

- [x] Pipeline functional for logon, device, file, HTTP, and email features
- [x] Isolation Forest integrated
- [x] TensorFlow Autoencoder integrated and visualized in Grafana
- [x] LDAP context enrichment added
- [x] Elasticsearch indexing and Grafana dashboard fully connected
- [x] Dashboard exported to `dashboards/grafana_dashboard.json`

---

*Projet UEBA — EMSI 4CIR Anfa*