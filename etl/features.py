"""Feature engineering — derived features (assignment requires ≥3, justified).

1. duration_min   — trip duration; base unit for speed & congestion analysis.
2. avg_speed_mph  — distance/duration; proxy for road congestion by hour/zone.
3. fare_per_mile  — economic efficiency of a trip; exposes flat-rate routes.
4. tip_pct        — tipping behaviour (card payments only; cash tips unrecorded).
5. pickup_hour / pickup_dow / is_weekend — temporal keys for demand patterns.
"""
import numpy as np
import pandas as pd


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    pu, do = df["tpep_pickup_datetime"], df["tpep_dropoff_datetime"]

    df["duration_min"] = (do - pu).dt.total_seconds() / 60.0
    df["avg_speed_mph"] = df["trip_distance"] / (df["duration_min"] / 60.0)
    df["fare_per_mile"] = df["fare_amount"] / df["trip_distance"]

    # Tip % only meaningful for credit-card trips (cash tips not recorded)
    df["tip_pct"] = np.where(
        (df["payment_type"] == 1) & (df["fare_amount"] > 0),
        df["tip_amount"] / df["fare_amount"] * 100.0,
        np.nan,
    )

    df["pickup_hour"] = pu.dt.hour.astype("int16")
    df["pickup_dow"] = pu.dt.dayofweek.astype("int16")  # 0=Mon
    df["is_weekend"] = df["pickup_dow"] >= 5
    return df
