"""Load ola_cleaned.csv into MySQL.  Usage:
   pip install pymysql sqlalchemy pandas
   python load_to_mysql.py <user> <password> [host] [database]
First run mysql_setup.sql so the table exists.
"""
import sys
import pandas as pd
from sqlalchemy import create_engine, text

user, pwd = sys.argv[1], sys.argv[2]
host = sys.argv[3] if len(sys.argv) > 3 else "localhost"
db = sys.argv[4] if len(sys.argv) > 4 else "ola_db"
engine = create_engine(f"mysql+pymysql://{user}:{pwd}@{host}/{db}")

df = pd.read_csv("ola_cleaned.csv")
df = df.where(df.notna(), None)  # NaN -> NULL
with engine.begin() as con:
    con.execute(text("TRUNCATE TABLE ola_rides"))
df.to_sql("ola_rides", engine, if_exists="append", index=False, chunksize=5000, method="multi")
with engine.connect() as con:
    print("Rows in MySQL:", con.execute(text("SELECT COUNT(*) FROM ola_rides")).scalar())
