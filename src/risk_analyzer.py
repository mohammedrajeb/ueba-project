"""
risk_analyzer.py

This file combines the rule-based score, the Isolation Forest anomaly result,
and the TensorFlow Autoencoder anomaly result.

It produces:
- risk_score: final risk score between 0 and 100
- risk_level: low, medium, high, critical
- alert_reason: explanation of the alert

This module transforms technical detections into actionable UEBA alerts.
"""


def get_risk_level(score: float) -> str:
    """
    Convert a numeric risk score into a risk level.

    Parameters:
        score: final risk score

    Returns:
        risk level as a string
    """
    if score <= 30:
        return "low"
    elif score <= 60:
        return "medium"
    elif score <= 80:
        return "high"
    else:
        return "critical"


def calculate_final_risk(row) -> float:
    """
    Combine rule-based score, Isolation Forest and Autoencoder results
    into a final risk score.

    Logic:
    - Start from the rule_score
    - Add 40 points if Isolation Forest detects an anomaly
    - Add 30 points if TensorFlow Autoencoder detects an anomaly
    - Limit the final score to 100

    Parameters:
        row: one row from the scored UEBA table

    Returns:
        final risk score
    """
    score = row.get("rule_score", 0)

    if row.get("is_anomaly", 0) == 1:
        score += 40

    if row.get("autoencoder_is_anomaly", 0) == 1:
        score += 30

    return min(score, 100)


def build_alert_reason(row) -> str:
    """
    Build a human-readable explanation for the alert.

    Parameters:
        row: one row from the scored UEBA table

    Returns:
        alert reason string
    """
    reasons = []

    rule_reasons = row.get("rule_reasons", "")

    if rule_reasons:
        reasons.append(rule_reasons)

    if row.get("is_anomaly", 0) == 1:
        reasons.append("AI anomaly detected by Isolation Forest")

    if row.get("autoencoder_is_anomaly", 0) == 1:
        reasons.append("AI anomaly detected by TensorFlow Autoencoder")

    if not reasons:
        return "No suspicious behavior detected"

    return "; ".join(reasons)


def apply_risk_analysis(df):
    """
    Apply final risk scoring and generate risk levels.

    Parameters:
        df: DataFrame containing rule, Isolation Forest and Autoencoder scores

    Returns:
        DataFrame with risk_score, risk_level and alert_reason
    """
    scored_df = df.copy()

    scored_df["risk_score"] = scored_df.apply(calculate_final_risk, axis=1)
    scored_df["risk_level"] = scored_df["risk_score"].apply(get_risk_level)
    scored_df["alert_reason"] = scored_df.apply(build_alert_reason, axis=1)

    return scored_df