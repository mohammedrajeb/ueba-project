"""
rule_engine.py

This file contains the rule-based UEBA risk scoring engine.

It applies simple and explainable cybersecurity rules such as:
- activity outside working hours
- USB usage
- high number of file accesses
- multiple PCs used by the same user
- abnormal number of logon events

This rule engine provides a first risk score before applying machine learning.
"""


def calculate_rule_score(row):
    """
    Calculate a rule-based risk score for one user-day behavior.
    """
    score = 0
    reasons = []

    if row.get("logon_outside_hours", 0) > 0:
        score += 20
        reasons.append("Logon outside working hours")

    if row.get("usb_events", 0) > 0:
        score += 15
        reasons.append("USB device usage")

    if row.get("usb_outside_hours", 0) > 0:
        score += 20
        reasons.append("USB usage outside working hours")

    if row.get("file_events", 0) > 100:
        score += 30
        reasons.append("High number of file accesses")

    if row.get("file_outside_hours", 0) > 0:
        score += 20
        reasons.append("File activity outside working hours")

    if row.get("unique_logon_pcs", 0) > 2:
        score += 15
        reasons.append("Multiple PCs used")

    return score, reasons


def apply_rule_engine(features_df):
    """
    Apply the rule engine to the full UEBA feature table.
    """
    features_df = features_df.copy()

    results = features_df.apply(calculate_rule_score, axis=1)

    features_df["rule_score"] = results.apply(lambda x: x[0])
    features_df["rule_reasons"] = results.apply(lambda x: "; ".join(x[1]))

    return features_df