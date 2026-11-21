"""Step 1 - Data cleaning & preprocessing for Ola Ride Insights.

Usage:  python clean_data.py path/to/OLA_dataset.csv
Output: ola_cleaned.csv  (for Power BI)  and  ola.db / table ola_rides  (for SQL + Streamlit)
"""
import sqlite3
import sys

import numpy as np
import pandas as pd

src = sys.argv[1] if len(sys.argv) > 1 else "OLA_DataSet.xlsx"
# The Excel file has 3 sheets; the data is in sheet "July" (103,024 rows)
df = pd.read_excel(src, sheet_name="July") if src.endswith(".xlsx") else pd.read_csv(src)

# --- 1. Standardise column names: "Booking ID" -> booking_id
df.columns = (
    df.columns.str.strip().str.lower()
    .str.replace(r"[^a-z0-9]+", "_", regex=True).str.strip("_")
)
df = df.rename(columns={"customer_rating": "customer_rating", "driver_ratings": "driver_ratings"})

# --- 2. Text clean-up: trim spaces, turn 'null'/'nan'/'' into real NaN
obj_cols = df.select_dtypes(include=["object", "string"]).columns
for c in obj_cols:
    df[c] = df[c].astype(str).str.strip().str.strip('"')
    df[c] = df[c].replace({"null": np.nan, "NULL": np.nan, "nan": np.nan, "None": np.nan, "": np.nan})

# --- 3. Data types
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["booking_datetime"] = pd.to_datetime(
    df["date"].dt.strftime("%Y-%m-%d") + " " + df["time"].astype(str), errors="coerce"
)
for c in ["booking_value", "ride_distance", "driver_ratings", "customer_rating", "v_tat", "c_tat"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# --- 4. Remove duplicates & rows with no booking id
df = df.drop_duplicates(subset="booking_id").dropna(subset=["booking_id"])

# --- 5. Missing-value strategy (NOT imputing: a cancelled ride genuinely has no
#        distance/value/rating, so filling them would distort averages)
# Booking_Value exists for every booking (value of the requested ride); Ride_Distance is 0 for rides never taken.
df["incomplete_rides"] = df["incomplete_rides"].fillna("Not Applicable")   # only completed bookings can be incomplete
df["payment_method"] = df["payment_method"].fillna("Not Applicable")       # no payment if ride did not happen
df["vehicle_type"] = df["vehicle_type"].replace({"eBike": "E-Bike"})


# --- 6. Derived features
df["hour"] = df["booking_datetime"].dt.hour
df["day_of_week"] = df["booking_datetime"].dt.day_name()
df["month"] = df["date"].dt.to_period("M").astype(str)
df["time_slot"] = pd.cut(
    df["hour"], bins=[-1, 5, 11, 16, 20, 23],
    labels=["Night", "Morning", "Afternoon", "Evening", "Late Night"],
).astype(str)
df["is_success"] = (df["booking_status"] == "Success").astype(int)
df["distance_completed"] = df["ride_distance"].where(df["is_success"] == 1)  # NaN for cancelled rides

# --- 7. Sanity checks (printed so you can screenshot them for your report)
print("Rows:", len(df))
print("\nMissing values per column:\n", df.isna().sum())
print("\nBooking status:\n", df["booking_status"].value_counts())
assert df["booking_id"].is_unique

# --- 8. Save
df.to_csv("ola_cleaned.csv", index=False)
with sqlite3.connect("ola.db") as con:
    df.assign(date=df["date"].dt.strftime("%Y-%m-%d"),
              booking_datetime=df["booking_datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")
              ).to_sql("ola_rides", con, if_exists="replace", index=False)
print("\nSaved ola_cleaned.csv and ola.db (table: ola_rides)")
