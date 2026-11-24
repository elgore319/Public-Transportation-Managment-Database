-- Public Transportation Management Database: views, indexes and queries (SQLite)
-- Run against public_transportation.db, e.g. in DB Browser for SQLite or the VS Code SQLite extension.
-- SQLite has no stored procedures. The Python functions in Insert_Data.py, Update_Data.py and
-- Delete_Data.py play that role: each one wraps a single parameterized INSERT, UPDATE or DELETE.


-- ============ Indexes ============

CREATE INDEX IF NOT EXISTS idx_gps_vehicle_time   ON GPS_Records (Vehicle_ID, TimeStamp);
CREATE INDEX IF NOT EXISTS idx_schedules_route    ON Schedules (Route_Number, Stop_Order);
CREATE INDEX IF NOT EXISTS idx_schedules_stop     ON Schedules (Stop_Number);
CREATE INDEX IF NOT EXISTS idx_trips_route        ON Trips (Route_Number);
CREATE INDEX IF NOT EXISTS idx_tickets_trip       ON Tickets (Trip_ID);
CREATE INDEX IF NOT EXISTS idx_tickets_passenger  ON Tickets (Passenger_ID);
CREATE INDEX IF NOT EXISTS idx_passengers_name    ON Passengers (Last_Name, First_Name);


-- ============ Views ============

DROP VIEW IF EXISTS v_trip_status;
CREATE VIEW v_trip_status AS
SELECT t.Trip_ID, t.Route_Number, t.Vehicle_ID,
       d.First_Name || ' ' || d.Last_Name AS Driver,
       t.Start_Time, t.Actual_Start_Time,
       CASE
           WHEN t.Actual_Start_Time IS NULL THEN 'Scheduled'
           WHEN t.Actual_Start_Time > t.Start_Time THEN 'Late'
           ELSE 'On Time'
       END AS Status
FROM Trips t
LEFT JOIN Drivers d ON d.Driver_ID = t.Driver_ID;

DROP VIEW IF EXISTS v_ticket_details;
CREATE VIEW v_ticket_details AS
SELECT k.Ticket_ID, p.First_Name || ' ' || p.Last_Name AS Passenger,
       t.Route_Number, t.Vehicle_ID, t.Start_Time, t.End_Time
FROM Tickets k
JOIN Passengers p ON p.Passenger_ID = k.Passenger_ID
JOIN Trips t ON t.Trip_ID = k.Trip_ID;

DROP VIEW IF EXISTS v_route_stops;
CREATE VIEW v_route_stops AS
SELECT DISTINCT sc.Route_Number, sc.Stop_Order, s.Stop_Number, s.Stop_Name
FROM Schedules sc
JOIN Stops s ON s.Stop_Number = sc.Stop_Number;


-- ============ Joins ============

-- Every ticket with passenger, route and bus
SELECT * FROM v_ticket_details ORDER BY Start_Time;

-- Route 1's stops in order
SELECT Stop_Order, Stop_Name FROM v_route_stops WHERE Route_Number = 1 ORDER BY Stop_Order;


-- ============ Aggregates ============

-- Tickets sold per passenger
SELECT p.First_Name || ' ' || p.Last_Name AS Passenger, COUNT(k.Ticket_ID) AS Tickets
FROM Passengers p
LEFT JOIN Tickets k ON k.Passenger_ID = p.Passenger_ID
GROUP BY p.Passenger_ID
ORDER BY Tickets DESC;

-- Trips and average delay per driver
SELECT Driver, COUNT(*) AS Trips,
       ROUND(AVG((strftime('%s', '2000-01-01 ' || Actual_Start_Time) -
                  strftime('%s', '2000-01-01 ' || Start_Time)) / 60.0), 1) AS Avg_Minutes_Late
FROM v_trip_status
WHERE Actual_Start_Time IS NOT NULL
GROUP BY Driver;


-- ============ Subqueries ============

-- Passengers with more tickets than the average passenger
SELECT p.First_Name, p.Last_Name
FROM Passengers p
WHERE (SELECT COUNT(*) FROM Tickets k WHERE k.Passenger_ID = p.Passenger_ID) >
      (SELECT COUNT(*) * 1.0 / (SELECT COUNT(*) FROM Passengers) FROM Tickets);

-- Routes that have never run late
SELECT r.Route_Number
FROM Routes r
WHERE NOT EXISTS (SELECT 1 FROM v_trip_status v WHERE v.Route_Number = r.Route_Number AND v.Status = 'Late');


-- ============ Advanced queries ============

-- Delayed buses
SELECT Trip_ID, Route_Number, Vehicle_ID, Driver, Start_Time, Actual_Start_Time,
       (strftime('%s', '2000-01-01 ' || Actual_Start_Time) -
        strftime('%s', '2000-01-01 ' || Start_Time)) / 60 AS Minutes_Late
FROM v_trip_status
WHERE Status = 'Late'
ORDER BY Minutes_Late DESC;

-- Busiest stops (scheduled arrivals and routes served)
SELECT s.Stop_Name, COUNT(sc.Schedule_ID) AS Arrivals, COUNT(DISTINCT sc.Route_Number) AS Routes
FROM Stops s
JOIN Schedules sc ON sc.Stop_Number = s.Stop_Number
WHERE s.Is_Active = 1
GROUP BY s.Stop_Number
ORDER BY Arrivals DESC, Routes DESC;

-- Passenger demand by route
SELECT r.Route_Number,
       (SELECT COUNT(*) FROM Trips t WHERE t.Route_Number = r.Route_Number) AS Trips,
       COUNT(k.Ticket_ID) AS Tickets_Sold
FROM Routes r
LEFT JOIN Trips t ON t.Route_Number = r.Route_Number
LEFT JOIN Tickets k ON k.Trip_ID = t.Trip_ID
GROUP BY r.Route_Number
ORDER BY Tickets_Sold DESC;

-- Vehicle utilization (percent of seats filled across a bus's trips)
SELECT v.Vehicle_ID, v.Capacity, COUNT(DISTINCT t.Trip_ID) AS Trips, COUNT(k.Ticket_ID) AS Tickets,
       ROUND(COUNT(k.Ticket_ID) * 100.0 / NULLIF(COUNT(DISTINCT t.Trip_ID) * v.Capacity, 0), 1) AS Seats_Filled_Pct
FROM Vehicles v
LEFT JOIN Trips t ON t.Vehicle_ID = v.Vehicle_ID
LEFT JOIN Tickets k ON k.Trip_ID = t.Trip_ID
GROUP BY v.Vehicle_ID
ORDER BY Seats_Filled_Pct DESC;

-- Shortest route (fewest stops, transfers allowed) from University Center to Hospital.
-- Change the two stop names at the bottom to search between other stops.
WITH RECURSIVE
legs AS (
    SELECT DISTINCT a.Route_Number, a.Stop_Number AS From_Stop, b.Stop_Number AS To_Stop
    FROM v_route_stops a
    JOIN v_route_stops b ON b.Route_Number = a.Route_Number AND b.Stop_Order = a.Stop_Order + 1
),
paths (Stop_Number, Hops, Path, Routes) AS (
    SELECT Stop_Number, 0, '/' || Stop_Number || '/', ''
    FROM Stops WHERE Stop_Name = 'University Center'
    UNION ALL
    SELECT l.To_Stop, p.Hops + 1, p.Path || l.To_Stop || '/', p.Routes || ' ' || l.Route_Number
    FROM paths p
    JOIN legs l ON l.From_Stop = p.Stop_Number
    WHERE p.Path NOT LIKE '%/' || l.To_Stop || '/%' AND p.Hops < 10
)
SELECT p.Hops AS Stops_Travelled, p.Path AS Stop_Numbers, p.Routes AS Routes_Taken
FROM paths p
JOIN Stops s ON s.Stop_Number = p.Stop_Number
WHERE s.Stop_Name = 'Hospital'
ORDER BY p.Hops
LIMIT 1;

-- Fastest direct trip between two stops (earliest arrival after each departure, same route)
SELECT o.Route_Number, o.Schedule_Arrival_Time AS Departs, MIN(d.Schedule_Arrival_Time) AS Arrives,
       (strftime('%s', '2000-01-01 ' || MIN(d.Schedule_Arrival_Time)) -
        strftime('%s', '2000-01-01 ' || o.Schedule_Arrival_Time)) / 60 AS Minutes
FROM Schedules o
JOIN Schedules d ON d.Route_Number = o.Route_Number
                AND d.Stop_Order > o.Stop_Order
                AND d.Schedule_Arrival_Time > o.Schedule_Arrival_Time
WHERE o.Stop_Number = (SELECT Stop_Number FROM Stops WHERE Stop_Name = 'Downtown Transit Center')
  AND d.Stop_Number = (SELECT Stop_Number FROM Stops WHERE Stop_Name = 'Library')
GROUP BY o.Schedule_ID
ORDER BY Minutes, Departs;

-- GPS: latest position of each bus (uses idx_gps_vehicle_time)
SELECT g.Vehicle_ID, g.TimeStamp, g.Latitude, g.Longitude
FROM GPS_Records g
WHERE g.TimeStamp = (SELECT MAX(TimeStamp) FROM GPS_Records x WHERE x.Vehicle_ID = g.Vehicle_ID);
