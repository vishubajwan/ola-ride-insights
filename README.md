# Ola Ride Insights

SQL + Power BI + Streamlit analytics project on Ola ride-booking data.

## Folder
| File | Purpose |
|---|---|
| `clean_data.py` | Cleans raw CSV → `ola_cleaned.csv` + SQLite `ola.db` |
| `queries.sql` | The 10 SQL questions from the brief (MySQL/SQLite compatible) |
| `app.py` | Streamlit app (overview charts, SQL results, search, Power BI embed) |
| `eda.py` | EDA charts + chi-square / Spearman tests |
| `mysql_setup.sql`, `load_to_mysql.py` | Create the MySQL table/views and load the cleaned data |
| `powerbi_guide.md` | DAX measures + page-by-page dashboard build steps |
| `Ola_Dashboard_Preview.pptx` | Your Ola-Slides template filled with real numbers and charts (use as PPT + Power BI design reference) |
| `ola_cleaned.csv`, `ola.db` | Cleaned data for Power BI / MySQL / Streamlit |

## Run it
```bash
pip install -r requirements.txt
python clean_data.py OLA_DataSet.xlsx   # creates ola.db + ola_cleaned.csv
streamlit run app.py
```
Deploy: push to GitHub (include `ola.db`) → share.streamlit.io → New app → select `app.py`.

## SQL / MySQL setup
1. Open MySQL Workbench and run `mysql_setup.sql` (creates `ola_db`, table `ola_rides` and two views).
2. Load the data: `python load_to_mysql.py root YOUR_PASSWORD` (should print `Rows in MySQL: 103024`).
3. Open `queries.sql`, run Q1-Q10 in Workbench and take a screenshot of each result for your report.
4. Power BI: Get Data > MySQL database > server `localhost`, database `ola_db` > select `ola_rides` (and the views).
5. Streamlit on MySQL: set env var `MYSQL_URL=mysql+pymysql://root:PASSWORD@localhost/ola_db` before `streamlit run app.py`
   (without it, the app uses the bundled SQLite `ola.db`, which gives identical results).

## Cleaning decisions (for your report)
- Column names standardised to snake_case; `"null"` strings converted to real NULLs.
- Date + Time merged into `booking_datetime`; numeric columns coerced to numbers.
- Duplicate Booking IDs removed.
- Ratings, distance and booking value are **not imputed** for cancelled rides - they genuinely don't exist, and filling them would bias averages.
- Derived features: `hour`, `day_of_week`, `month`, `time_slot`, `is_success`.

## Key insights (July 2024, 103,024 bookings)
1. **Only 62.1% of bookings complete.** 17.9% are cancelled by drivers, 10.2% by customers, 9.8% "driver not found". About Rs 2.15 Cr of booking value (38% of Rs 5.65 Cr) was lost this way; completed rides earned Rs 3.51 Cr.
2. **Drivers cancel more than customers.** Top driver reasons: personal & car issues (35.5%), customer-related issue (29.4%). Top customer reasons: driver not moving towards pickup (30.2%) and driver asked to cancel (25.4%). So about 55% of customer cancellations are caused by driver behaviour; only 9.6% are "wrong address".
3. **Payments:** Cash 54.8% and UPI 40.5% of completed rides; cards under 5%. Cash brings Rs 1.93 Cr, UPI Rs 1.42 Cr.
4. **Demand is flat.** Each hour has about 4,200-4,400 bookings (peak 12:00, 15:00, 08:00, 17:00) and each day about 3,300 bookings, so there is no sharp peak window in this data.
5. **Vehicle types perform alike** (success rate 61.4-63.0%, ratings about 4.0). Auto has the shortest trips (avg 6.2 km vs about 15.5 km for others). Prime Sedan has the highest revenue (Rs 52.2 L) and success rate (63.0%).
6. **Incomplete rides:** 3,926 (6.1% of completed). Causes: Customer Demand 40.8%, Vehicle Breakdown 40.5%, Other 18.7%.
7. **Statistics:** Chi-square shows booking status is independent of vehicle type (p = 0.35); distance and booking value are uncorrelated (Spearman about 0.00). The data looks synthetic, so say this honestly in the presentation.

## Business suggestions
- Cut driver cancellations: penalties/incentives, better driver-pickup tracking, vehicle checks (breakdowns, car issues).
- Fix "driver not found": more drivers or surge incentives where requests go unmatched.
- Push UPI/digital payment with offers (cash is still over half of rides).
- Reduce incomplete rides with vehicle maintenance checks.

## 10-day plan
Day 1-2 explore + clean · 3-4 SQL · 5-7 Power BI · 8 Streamlit · 9 deploy + GitHub · 10 documentation + presentation.
