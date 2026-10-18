import pandas as pd
import numpy as np
import json

pd.set_option("display.width",200)

df=pd.read_csv("data.csv")

df.info


df["date_time"]=pd.to_datetime(df["date_time"])

df["year"]=df["date_time"].dt.year

df["hour"]=df["date_time"].dt.hour

df["weekday"]=df["date_time"].dt.day_name()

harm = ['number_of_cyclist_injured',
       'number_of_cyclist_killed', 'number_of_motorist_injured',
       'number_of_motorist_killed', 'number_of_pedestrian_injured',
       'number_of_pedestrian_killed', 'number_of_persons_injured',
       'number_of_persons_killed']

df["intersection"]=(df["on_street_name"].str.strip() + " and " +  df["cross_street_name"].str.strip())

byborough = (df.groupby("borough")[harm].sum().sort_values("number_of_persons_injured",ascending=False))

#print(byborough)

print(f"Rows:    {len(df):,}")
print(f"Columns: {df.shape[1]}")
print(f"Date range: {df['date_time'].min()}  to  {df['date_time'].max()}")
print("Boroughs:", ", ".join(df["borough"].dropna().unique()))
df.info()

#injury summary

stats = df[harm].describe().T
stats["median"] = df[harm].median()
stats["range"] = stats["max"] - stats["min"]
stats["total"] = df[harm].sum()
stats["percent"] = stats["total"] / stats["total"].sum() * 100
print(stats[["mean", "total", "percent"]].round(3))

#borough sum summary

stats = df.groupby("borough")["number_of_persons_injured"].agg(
    ["count", "min", "max", "mean", "sum"])
stats["largest_crash"] = stats["max"] - stats["min"]
stats["percent"] = stats["sum"] / stats["sum"].sum() * 100
print(stats.round(3))

# year and hour summary

print(df.groupby("year")[harm].sum())

print(df.groupby("hour")["crash_count"].sum())

#contributing factor/vehicle type summary 

for col in ["contributing_factors", "vehicle_types"]:
    values = (df[col].dropna().str.split(r"\s*[,;|]\s*").explode()
                .str.strip().str.lower())
    values = values[~values.isin(["", "unspecified", "nan"])]
    print(f"\n{col} ({values.nunique()} unique values):")
    print(values.value_counts().head(10))

# factors and vehicles by boro

for col in ["contributing_factors", "vehicle_types"]:
    split = df[["borough", col]].dropna().copy()
    split[col] = split[col].str.split(r"\s*[,;|]\s*")
    split = split.explode(col)
    split[col] = split[col].str.strip().str.lower()
    split = split[~split[col].isin(["", "unspecified", "nan"])]

    for boro, group in split.groupby("borough"):
        print(f"\n{col} in {boro}:")
        print(group[col].value_counts().head(5))

def top_values(col, boro, n):
    values = df.loc[df["borough"] == boro, col].dropna().str.split(r"\s*[,;|]\s*").explode()
    values = values.str.strip().str.lower()
    values = values[~values.isin(["", "unspecified", "nan"])]
    return ", ".join(values.value_counts().head(n).index)

chart = []
for boro, row in stats.sort_values("sum", ascending=False).iterrows():
    chart.append({
        "borough": boro.lower(),
        "crashes": int(row["count"]),
        "injured": int(row["sum"]),
        "mean": round(row["mean"], 3),
        "max": int(row["max"]),
        "percent": round(row["percent"], 1),
        "factor": top_values("contributing_factors", boro, 1),
        "vehicles": top_values("vehicle_types", boro, 3),
    })

# for html file

with open("borough_data.json", "w") as f:
    json.dump(chart, f, indent=1)
print("\nsaved borough_data.json")