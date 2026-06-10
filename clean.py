import pandas as pd
import json

RAW = "data/yellow_tripdata_2019-01.csv"

# --- load ---
df = pd.read_csv(RAW)
rows_start = len(df)

# --- transforms (not exclusions) ---
df["congestion_surcharge"] = df["congestion_surcharge"].fillna(0)
df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"])

# --- exclusion logging ---
exclusion_log = []

def drop_and_log(df, keep_mask, rule, reason):
    removed = int(len(df) - keep_mask.sum())
    exclusion_log.append({"rule": rule, "rows_removed": removed, "reason": reason})
    return df[keep_mask].copy()


df = drop_and_log(
    df,
    df["fare_amount"] >= 0,
    rule="non_negative_fare",
    reason="Negative fare = refund/void, not a passenger trip",
)

df = drop_and_log(
    df,
    df["tip_amount"] >= 0,
    rule="non_negative_tip",
    reason="Negative tip = refund/void, not a passenger trip",
)

df = drop_and_log (
    df,
    df["tolls_amount"] >= 0,
    rule="non_negative_tolls",
    reason="Negative tolls = refund/void, not a passenger trip",
)

df = drop_and_log (
    df,
    df["total amount"] >= 0,
    rule="non_negative_total_amount",
    reason="Negative total amount = refund/void, not a passenger trip",
)

df = drop_and_log (
    df,
    df["total_amount"] <=300,
    rule="reasonable_total_amount",
    reason="Total amount > $300 is likely a data error, not a passenger trip",
)

df = drop_and_log (
    df,
    df["trip_distance"] > 0 & df["trip_distance"] <= 100,
    rule="reasonable_trip_distance",
    reason="Trip distance is outside the reasonable range",
)

df = drop_and_log (
    df,
    df["passenger_count"] >= 1 & df["passenger_count"] <= 6, 
    rule="reasonable_passenger_count",
    reason="Passenger count is outside the reasonable range"
)

df = drop_and_log (
    df,
    df["RatecodeID"] != 99,
    rule="exclude_unknown_ratecode",
)

df = drop_and_log (
    df,
    df["tpep_pickup_datetime"] >= "2019-01-01" & df["tpep_pickup_datetime"] < "2019-02-01",
    rule="pickup_before_dropoff",
    reason="Pickup datetime is after dropoff datetime, which is not possible for a passenger trip",
)

df = drop_and_log (
    df,
    df["tpep_dropoff_datetime"] > df["tpep_pickup_datetime"],
    rule="dropoff_before_pickup",
    reason="Dropoff datetime is before pickup datetime, which is not possible for a passenger trip",
)

# --- outputs ---
rows_end = len(df)
print(f"kept {rows_end:,} of {rows_start:,} rows ({rows_start - rows_end:,} removed)")
for entry in exclusion_log:
    print(entry)

df.to_parquet("data/yellow_tripdata_clean.parquet", index=False)
with open("data/exclusion_log.json", "w") as f:
    json.dump(exclusion_log, f, indent=2)