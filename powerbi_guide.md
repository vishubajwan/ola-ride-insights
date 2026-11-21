# Power BI Dashboard Guide (Ola Ride Insights)

**Load data:** Home → Get Data → Text/CSV → `ola_cleaned.csv` (or MySQL: Get Data → MySQL database → table `ola_rides`).
Set types in Power Query: `date` = Date, `booking_value`, `ride_distance` = Decimal, ratings = Decimal.

## DAX measures (Modeling → New measure)
```DAX
Total Bookings   = COUNTROWS(ola_rides)
Successful Rides = CALCULATE(COUNTROWS(ola_rides), ola_rides[booking_status] = "Success")
Success Rate %   = DIVIDE([Successful Rides], [Total Bookings])
Total Revenue    = CALCULATE(SUM(ola_rides[booking_value]), ola_rides[booking_status] = "Success")
Avg Booking Value = DIVIDE([Total Revenue], [Successful Rides])
Cancelled Rides  = CALCULATE(COUNTROWS(ola_rides), ola_rides[booking_status] IN {"Canceled by Customer","Canceled by Driver"})
Cancellation Rate % = DIVIDE([Cancelled Rides], [Total Bookings])
Avg Driver Rating   = AVERAGE(ola_rides[driver_ratings])
Avg Customer Rating = AVERAGE(ola_rides[customer_rating])
Avg Ride Distance   = AVERAGE(ola_rides[ride_distance])
```

## Pages (matches "Segregation of the views" in your brief)
| Page | Visuals | Build |
|---|---|---|
| **1. Overall** | Ride Volume Over Time | Line chart: Axis `date`, Values `Total Bookings` |
| | Booking Status Breakdown | Donut: Legend `booking_status`, Values `Total Bookings` |
| | KPI cards | Total Bookings, Success Rate %, Total Revenue, Cancellation Rate % |
| **2. Vehicle Type** | Top 5 Vehicle Types by Ride Distance | Bar: `vehicle_type` vs Sum of `ride_distance`; Filters pane → Top N = 5 by that value |
| | Avg Customer Rating by Vehicle Type | Clustered bar with `Avg Customer Rating` |
| **3. Revenue** | Revenue by Payment Method | Column chart: `payment_method` vs `Total Revenue` |
| | Top 5 Customers by Booking Value | Bar: `customer_id` vs `Total Revenue`, Top N = 5 |
| | Ride Distance Distribution Per Day | Column/area: `date` vs `Avg Ride Distance` (or Sum) |
| **4. Cancellation** | Customer cancel reasons | Bar: `canceled_rides_by_customer` vs count (filter out blanks) |
| | Driver cancel reasons | Bar: `canceled_rides_by_driver` vs count (filter out blanks) |
| **5. Ratings** | Driver Ratings distribution | Column chart: bin `driver_ratings` (Group → Bin size 0.5) vs count |
| | Customer vs Driver Ratings | Scatter: X `customer_rating`, Y `driver_ratings`, Details `booking_id` or Vehicle Type |

**Slicers on every page (sync via View → Sync slicers):** Date, Vehicle Type, Booking Status, Payment Method.
**Tips:** consistent colour theme (Ola green/yellow), titles on all visuals, tooltips, a navigation bar with page buttons.

## Publish & embed in Streamlit
Home → Publish → Power BI Service → open report → File → Embed report → *Publish to web (public)* → copy the link →
paste into `POWERBI_URL` in `app.py`. (A free personal account may not allow this; use a work/school account, or screenshot pages and show them with `st.image` as a fallback.)
