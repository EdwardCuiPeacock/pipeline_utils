SELECT pickup_community_area,
    fare,
    EXTRACT(
        MONTH
        FROM trip_start_timestamp
    ) AS trip_start_month,
    EXTRACT(
        HOUR
        FROM trip_start_timestamp
    ) AS trip_start_hour,
    EXTRACT(
        DAYOFWEEK
        FROM trip_start_timestamp
    ) AS trip_start_day,
    UNIX_SECONDS(trip_start_timestamp) AS trip_start_timestamp,
    pickup_latitude,
    pickup_longitude,
    dropoff_latitude,
    dropoff_longitude,
    trip_miles,
    pickup_census_tract,
    dropoff_census_tract,
    payment_type,
    company,
    trip_seconds,
    dropoff_community_area,
    tips,
    IF(tips > fare * 0.2, 1, 0) AS big_tipper
FROM `bigquery-public-data.chicago_taxi_trips.taxi_trips`
WHERE (
        ABS(FARM_FINGERPRINT(unique_key)) / 0x7FFFFFFFFFFFFFFF
    ) < { { query_sample_rate } }