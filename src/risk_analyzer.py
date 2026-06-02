"""
risk_analyzer.py

This file combines the rule-based score and the machine learning anomaly result.

It produces:
- a final risk score
- a risk level: low, medium, high, critical
- an alert explanation

This module transforms anomalies into actionable UEBA alerts.
"""


def get_risk_level(score):
    """
    Convert a numeric risk score into a risk level.
    """
    if score <= 30:
        return "low"
    elif score <= 60:
        return "medium"
    elif score <= 80:
        return "high"
    else:
        return "critical"


def calculate_final_risk(row):
    """
    Combine rule score and ML anomaly flag into one final risk score.
    """
    score = row.get("rule_score", 0)

    if row.get("is_anomaly", 0) == 1:
        score += 40

    return min(score, 100)


def apply_risk_analysis(df):
    """
    Apply final risk scoring and generate risk levels.
    """
    df = df.copy()

    df["risk_score"] = df.apply(calculate_final_risk, axis=1)
    df["risk_level"] = df["risk_score"].apply(get_risk_level)

    return df