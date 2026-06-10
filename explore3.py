import pandas as pd
df = pd.read_csv("data/yellow_tripdata_2019-01.csv")
print(df[["trip_distance", "fare_amount", "total_amount"]].quantile([0.99, 0.999, 0.9999]))
print("zero-distance trips:", (df["trip_distance"] == 0).sum())
print("out-of-month pickups:", (~df["tpep_pickup_datetime"].str.startswith("2019-01")).sum())
