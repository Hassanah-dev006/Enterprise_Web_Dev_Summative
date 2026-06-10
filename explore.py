import pandas as pd

df = pd.read_csv("data/yellow_tripdata_2019-01.csv")

print("shape:", df.shape)
print(df.dtypes)
print(df.describe(include="all"))
print(df.isna().sum())
print(df.head())
