"""EDA for Ola Ride Insights, following the GUVI EDA guide.
Run after clean_data.py:  python eda.py   (saves charts to ./eda_charts, prints findings)
"""
import os
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy import stats

os.makedirs("eda_charts", exist_ok=True)
df = pd.read_sql("SELECT * FROM ola_rides", sqlite3.connect("ola.db"), parse_dates=["date"])


def save(name):
    plt.tight_layout(); plt.savefig(f"eda_charts/{name}.png", dpi=120); plt.close()


# 1. Understand the dataset
print(df.shape, "\n", df.dtypes, "\n", df.isna().sum(), "\nDuplicates:", df.duplicated().sum())
print(df.describe().T)

# 2. Univariate
sns.countplot(data=df, y="booking_status", order=df["booking_status"].value_counts().index); save("status_count")
sns.countplot(data=df, y="vehicle_type", order=df["vehicle_type"].value_counts().index); save("vehicle_count")
for c in ["booking_value", "ride_distance", "driver_ratings", "customer_rating"]:
    sns.histplot(df[c].dropna(), kde=True); save(f"hist_{c}")
    print(f"{c}: skew={df[c].skew():.2f}")

# 3. Outliers (IQR)
for c in ["booking_value", "ride_distance"]:
    q1, q3 = df[c].quantile([.25, .75]); iqr = q3 - q1
    n = ((df[c] < q1 - 1.5 * iqr) | (df[c] > q3 + 1.5 * iqr)).sum()
    print(f"Outliers in {c}: {n}")
    sns.boxplot(x=df[c]); save(f"box_{c}")

# 4. Bivariate / time patterns
sns.barplot(data=df, x="vehicle_type", y="booking_value", estimator="mean"); plt.xticks(rotation=45); save("value_by_vehicle")
sns.countplot(data=df, x="hour"); save("demand_by_hour")
sns.heatmap(pd.crosstab(df["day_of_week"], df["hour"]), cmap="YlGnBu"); save("heatmap_day_hour")
sns.heatmap(df[["booking_value", "ride_distance", "driver_ratings", "customer_rating"]].corr(), annot=True, cmap="coolwarm"); save("corr")

# 5. Statistical tests (explain WHY in your presentation)
ct = pd.crosstab(df["vehicle_type"], df["booking_status"])
chi2, p, *_ = stats.chi2_contingency(ct)
print(f"Chi-square (vehicle_type vs booking_status): p={p:.4f} -> {'dependent' if p < .05 else 'independent'}")
s = df[df["booking_status"] == "Success"].dropna(subset=["ride_distance", "booking_value"])
r, p = stats.spearmanr(s["ride_distance"], s["booking_value"])
print(f"Spearman (distance vs value): rho={r:.2f}, p={p:.4f}")
