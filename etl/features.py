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
