import pandas as pd

from .config import RULES

def clean_chunk(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int], pd.DataFrame]:
    """Apply all integrity rules to one chunk.

    Returns (clean_df, counts_by_rule, sample_of_excluded_rows).
    """
    counts: dict[str, int] = {}
    excluded_samples = []

    def exclude(mask: pd.Series, rule: str) -> pd.Series:
        """Record rows matching `mask` as excluded under `rule`."""
        n = int(mask.sum())
        if n:
            counts[rule] = counts.get(rule, 0) + n
            sample = df.loc[mask].head(5).copy()
            sample["exclusion_rule"] = rule
            excluded_samples.append(sample)
        return mask

    r = RULES
    pu, do = df["tpep_pickup_datetime"], df["tpep_dropoff_datetime"]
    duration_min = (do - pu).dt.total_seconds() / 60.0
    speed = df["trip_distance"] / (duration_min / 60.0)

    bad = exclude(df.duplicated(), "duplicate_row")
    bad |= exclude(
        df[["tpep_pickup_datetime", "tpep_dropoff_datetime",
            "trip_distance", "fare_amount", "total_amount",
            "PULocationID", "DOLocationID"]].isna().any(axis=1),
        "missing_critical_field",
    )
    bad |= exclude(
        (pu < r["month_start"]) | (pu >= r["month_end"]), "pickup_outside_month"
    )
    bad |= exclude(
        (duration_min < r["min_duration_min"]) | (duration_min > r["max_duration_min"]),
        "implausible_duration",
    )
    bad |= exclude(
        (df["trip_distance"] < r["min_distance_mi"])
        | (df["trip_distance"] > r["max_distance_mi"]),
        "implausible_distance",
    )
    bad |= exclude(
        (df["fare_amount"] < r["min_fare"]) | (df["fare_amount"] > r["max_fare"]),
        "implausible_fare",
    )
    bad |= exclude(df["total_amount"] > r["max_total"], "implausible_total")
    bad |= exclude(speed > r["max_speed_mph"], "implausible_speed")
    bad |= exclude(
        ~df["PULocationID"].isin(r["valid_location_ids"])
        | ~df["DOLocationID"].isin(r["valid_location_ids"]),
        "unknown_location_id",
    )
    bad |= exclude(
        (df["passenger_count"] < r["min_passengers"])
        | (df["passenger_count"] > r["max_passengers"]),
        "implausible_passenger_count",
    )

    clean = df.loc[~bad].copy()

    # Non-fatal normalization
    clean["store_and_fwd_flag"] = clean["store_and_fwd_flag"].map(
        {"Y": True, "N": False}
    )
    clean["congestion_surcharge"] = clean["congestion_surcharge"].fillna(0.0)

    
    for col, valid in (
        ("VendorID", r["valid_vendor_ids"]),
        ("RatecodeID", r["valid_rate_codes"]),
        ("payment_type", r["valid_payment_types"]),
    ):
        clean.loc[~clean[col].isin(valid), col] = pd.NA

    samples = (
        pd.concat(excluded_samples, ignore_index=True)
        if excluded_samples
        else pd.DataFrame()
    )
    return clean, counts, samples
