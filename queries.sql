-- Ola Ride Insights: SQL answers (table: ola_rides). Works on MySQL and SQLite.
-- Load into MySQL with: pandas.to_sql or MySQL Workbench Table Import Wizard on ola_cleaned.csv

-- Q1: Retrieve all successful bookings
SELECT * FROM ola_rides WHERE booking_status = 'Success';

-- Q2: Average ride distance for each vehicle type
-- (ride_distance is 0 for cancelled bookings, so we show both: all bookings and completed rides only)
SELECT vehicle_type,
       ROUND(AVG(ride_distance), 2)      AS avg_distance_all_bookings,
       ROUND(AVG(distance_completed), 2) AS avg_distance_completed_rides
FROM ola_rides
GROUP BY vehicle_type
ORDER BY avg_distance_all_bookings DESC;

-- Q3: Total number of cancelled rides by customers
SELECT COUNT(*) AS cancelled_by_customers
FROM ola_rides
WHERE booking_status = 'Canceled by Customer';

-- Q4: Top 5 customers with the highest number of rides
SELECT customer_id, COUNT(*) AS total_rides
FROM ola_rides
GROUP BY customer_id
ORDER BY total_rides DESC
LIMIT 5;

-- Q5: Rides cancelled by drivers due to personal and car-related issues
SELECT COUNT(*) AS driver_cancellations_personal_car
FROM ola_rides
WHERE booking_status = 'Canceled by Driver'
  AND canceled_rides_by_driver LIKE 'Personal%Car%';

-- Q6: Max and min driver ratings for Prime Sedan bookings
SELECT MAX(driver_ratings) AS max_driver_rating, MIN(driver_ratings) AS min_driver_rating
FROM ola_rides
WHERE vehicle_type = 'Prime Sedan';

-- Q7: All rides paid using UPI
SELECT * FROM ola_rides WHERE payment_method = 'UPI';

-- Q8: Average customer rating per vehicle type
SELECT vehicle_type, ROUND(AVG(customer_rating), 2) AS avg_customer_rating
FROM ola_rides
GROUP BY vehicle_type
ORDER BY avg_customer_rating DESC;

-- Q9: Total booking value of successfully completed rides
SELECT SUM(booking_value) AS total_booking_value
FROM ola_rides
WHERE booking_status = 'Success';

-- Q10: All incomplete rides along with the reason
SELECT booking_id, vehicle_type, incomplete_rides_reason
FROM ola_rides
WHERE incomplete_rides = 'Yes';
