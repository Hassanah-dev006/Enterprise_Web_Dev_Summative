import pandas as pd
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

df = pd.read_csv("data/yellow_tripdata_2019-01.csv")

cols = ["passenger_count", "trip_distance", "RatecodeID",
        "fare_amount", "tip_amount", "tolls_amount", "total_amount"]
print(df[cols].describe())

print("exact duplicate rows:", df.duplicated().sum())
print(df["RatecodeID"].value_counts())
print(df["payment_type"].value_counts())
print(df["passenger_count"].value_counts().sort_index())
