-- Run in MySQL Workbench (File > Open SQL Script > Execute).
CREATE DATABASE IF NOT EXISTS ola_db;
USE ola_db;

DROP TABLE IF EXISTS ola_rides;
CREATE TABLE ola_rides (
    date                        DATE,
    time                        TIME,
    booking_id                  VARCHAR(20) PRIMARY KEY,
    booking_status              VARCHAR(30),
    customer_id                 VARCHAR(15),
    vehicle_type                VARCHAR(20),
    pickup_location             VARCHAR(50),
    drop_location               VARCHAR(50),
    v_tat                       DECIMAL(8,2),
    c_tat                       DECIMAL(8,2),
    canceled_rides_by_customer  VARCHAR(60),
    canceled_rides_by_driver    VARCHAR(60),
    incomplete_rides            VARCHAR(20),
    incomplete_rides_reason     VARCHAR(40),
    booking_value               INT,
    payment_method              VARCHAR(20),
    ride_distance               INT,
    driver_ratings              DECIMAL(3,1),
    customer_rating             DECIMAL(3,1),
    vehicle_images              VARCHAR(200),
    booking_datetime            DATETIME,
    hour                        TINYINT,
    day_of_week                 VARCHAR(12),
    month                       VARCHAR(8),
    time_slot                   VARCHAR(12),
    is_success                  TINYINT,
    distance_completed          DECIMAL(8,2)
);

-- Load the data (pick ONE):
--  A) Easiest: python load_to_mysql.py   (see README)
--  B) Workbench: right-click table ola_rides > Table Data Import Wizard > ola_cleaned.csv
--  C) SQL (needs local_infile=1 enabled):
-- LOAD DATA LOCAL INFILE 'C:/path/to/ola_cleaned.csv' INTO TABLE ola_rides
--   FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' LINES TERMINATED BY '\n' IGNORE 1 ROWS;

-- Sanity check after loading: should return 103024
SELECT COUNT(*) FROM ola_rides;

-- Handy views for Power BI
CREATE OR REPLACE VIEW v_vehicle_summary AS
SELECT vehicle_type,
       SUM(booking_value)                                                AS total_booking_value,
       SUM(CASE WHEN booking_status='Success' THEN booking_value END)    AS success_booking_value,
       ROUND(AVG(ride_distance),2)                                       AS avg_distance,
       SUM(ride_distance)                                                AS total_distance
FROM ola_rides GROUP BY vehicle_type;

CREATE OR REPLACE VIEW v_cancellations AS
SELECT booking_status, COALESCE(canceled_rides_by_customer, canceled_rides_by_driver) AS reason, COUNT(*) AS rides
FROM ola_rides WHERE booking_status IN ('Canceled by Customer','Canceled by Driver')
GROUP BY booking_status, reason;
