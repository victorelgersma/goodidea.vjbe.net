import pandas as pd

file_path = "data/2026-08-03/results.csv"

df = pd.read_csv(file_path)

# filter out NaNs: 
print("names:", df["Q9"].unique())
# print("emails:", df["Q11"].unique())

