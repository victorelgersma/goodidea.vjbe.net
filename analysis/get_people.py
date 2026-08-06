import pandas as pd

file_path = "data/2026-08-03/results.csv"

df = pd.read_csv(file_path, header=1)

print(df.columns.tolist())

print("\n--- Names and emails ---")
print(df[[
    "(optional): What is your name?",
    "(optional) What is your e-mail address?"
]])