"""
rule_engine.py

This file contains the rule-based UEBA risk scoring engine.

The goal is to apply simple and explainable cybersecurity rules
on behavioral features.

The rule engine is the first detection layer before applying machine learning.

It produces:
- rule_score: numeric risk score
- rule_reasons: explanation of why the behavior is considered risky
"""


def calculate_rule_score(row):
    """
    Calculate a rule-based risk score for one user-day behavior.

    Parameters:
        row: one row from the UEBA behavioral feature table

    Returns:
        tuple: risk score and list of reasons
    """
    score = 0
    reasons = []

    # Rule 1: logon activity outside working hours
    if row.get("logon_outside_hours", 0) > 0:
        score += 20
        reasons.append("Logon activity outside working hours")

    # Rule 2: USB usage
    if row.get("usb_events", 0) > 0:
        score += 15
        reasons.append("USB activity detected")

    # Rule 3: USB usage outside working hours
    if row.get("usb_outside_hours", 0) > 0:
        score += 25
        reasons.append("USB activity outside working hours")

    # Rule 4: high number of file copies to removable media
    if row.get("file_copy_events", 0) > 20:
        score += 30
        reasons.append("High file copy activity")

    # Rule 5: file copies outside working hours
    if row.get("file_copy_outside_hours", 0) > 0:
        score += 25
        reasons.append("File copy activity outside working hours")

    # Rule 6: user logged into multiple PCs
    if row.get("unique_logon_pcs", 0) > 2:
        score += 15
        reasons.append("Multiple PCs used for logon")

    # Rule 7: dangerous combination for possible exfiltration
    if (
        row.get("logon_outside_hours", 0) > 0
        and row.get("usb_events", 0) > 0
        and row.get("file_copy_events", 0) > 20
    ):
        score += 30
        reasons.append("Possible data exfiltration pattern")

    # Keep the score between 0 and 100
    score = min(score, 100)

    return score, reasons


def apply_rule_engine(features_df):
    """
    Apply the rule engine to the full UEBA feature table.

    Parameters:
        features_df: UEBA feature DataFrame

    Returns:
        DataFrame with rule_score and rule_reasons
    """
    df = features_df.copy()

    results = df.apply(calculate_rule_score, axis=1)

    df["rule_score"] = results.apply(lambda result: result[0])
    df["rule_reasons"] = results.apply(lambda result: "; ".join(result[1]))

    return df