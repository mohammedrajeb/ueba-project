"""
autoencoder_model.py

This file contains an advanced anomaly detection model based on TensorFlow.

The selected model is an Autoencoder.

The Autoencoder learns to reconstruct normal user behavior.
If the reconstruction error is high, the behavior is considered suspicious.

This model is used as an additional AI layer after Isolation Forest.
"""

from typing import List, Tuple

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import StandardScaler


def get_training_columns(features_df: pd.DataFrame, excluded_columns: List[str]) -> List[str]:
    """
    Select numeric columns used for Autoencoder training.
    """
    candidate_columns = [
        column for column in features_df.columns
        if column not in excluded_columns
    ]

    numeric_columns = features_df[candidate_columns].select_dtypes(
        include=["number"]
    ).columns.tolist()

    return numeric_columns


def build_autoencoder(input_dim: int) -> tf.keras.Model:
    """
    Build a simple Autoencoder model.

    Parameters:
        input_dim: number of input features

    Returns:
        compiled TensorFlow Autoencoder model
    """
    input_layer = tf.keras.layers.Input(shape=(input_dim,))

    encoded = tf.keras.layers.Dense(16, activation="relu")(input_layer)
    encoded = tf.keras.layers.Dense(8, activation="relu")(encoded)

    decoded = tf.keras.layers.Dense(16, activation="relu")(encoded)
    decoded = tf.keras.layers.Dense(input_dim, activation="linear")(decoded)

    autoencoder = tf.keras.Model(inputs=input_layer, outputs=decoded)

    autoencoder.compile(
        optimizer="adam",
        loss="mse"
    )

    return autoencoder


def apply_autoencoder(
    features_df: pd.DataFrame,
    epochs: int = 30,
    batch_size: int = 32,
    threshold_percentile: float = 98.0,
) -> Tuple[pd.DataFrame, tf.keras.Model, StandardScaler]:
    """
    Train and apply a TensorFlow Autoencoder on UEBA behavioral features.

    Parameters:
        features_df: DataFrame containing UEBA features and previous scores
        epochs: number of training epochs
        batch_size: training batch size
        threshold_percentile: percentile used to define anomaly threshold

    Returns:
        scored_df: DataFrame with Autoencoder anomaly columns
        model: trained Autoencoder model
        scaler: fitted StandardScaler
    """
    df = features_df.copy()

    excluded_columns = [
        "user",
        "day",
        "rule_reasons",
        "alert_reason",
        "risk_level",
    ]

    training_columns = get_training_columns(df, excluded_columns)

    if not training_columns:
        raise ValueError("No numeric columns available for Autoencoder training.")

    X = df[training_columns]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = build_autoencoder(input_dim=X_scaled.shape[1])

    model.fit(
        X_scaled,
        X_scaled,
        epochs=epochs,
        batch_size=batch_size,
        shuffle=True,
        verbose=0,
    )

    reconstructed = model.predict(X_scaled, verbose=0)

    reconstruction_errors = np.mean(
        np.square(X_scaled - reconstructed),
        axis=1
    )

    threshold = np.percentile(reconstruction_errors, threshold_percentile)

    df["autoencoder_reconstruction_error"] = reconstruction_errors
    df["autoencoder_threshold"] = threshold
    df["autoencoder_is_anomaly"] = (
        df["autoencoder_reconstruction_error"] > threshold
    ).astype(int)

    return df, model, scaler