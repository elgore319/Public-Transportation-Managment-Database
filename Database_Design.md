# Public Transportation Management Database: Design

## 1. Requirements

The system manages a city bus network and its riders.

**Data it must store**
- Routes, and the stops each route visits in order with scheduled arrival times
- Stops with their location and whether they are in service
- Buses (vehicles) and their seating capacity
- Drivers and their shifts
- Trips: a bus and driver running a route at a scheduled time, with the actual start and end times
- Passengers and the tickets they buy for trips
- GPS readings from each bus over time

**What users must be able to do**
- Log in (`login.py`), then reach search, data management and reports from a main menu
- Look up a ticket, a passenger's trips, a route's stops and times, or the buses serving a stop
- Create, read, update and delete tickets, routes, stops, trips, vehicles, drivers and GPS records
- See reports: delayed buses, busiest stops, passenger demand by route, vehicle utilization
- Find the shortest route and fastest trip between two stops (Reports screen and `Advanced_Queries.sql`)

**Rules**
- Every ticket belongs to one passenger and one trip; every trip runs one route with one bus and one driver
- A stop, bus, driver or trip that other records still use cannot be deleted
- IDs are assigned automatically

## 2. Entities and relationships (ER diagram: `Public Transportation Database (1).drawio`)

| Relationship | Cardinality | Through |
|---|---|---|
| Route visits Stop | many-to-many | Schedules (Stop_Order, arrival time) |
| Route has Trips | one-to-many | Trips.Route_Number |
| Vehicle runs Trips | one-to-many | Trips.Vehicle_ID |
| Driver drives Trips | one-to-many | Trips.Driver_ID |
| Trip has Tickets | one-to-many | Tickets.Trip_ID |
| Passenger buys Tickets | one-to-many | Tickets.Passenger_ID |
| Vehicle reports GPS Records | one-to-many | GPS_Records.Vehicle_ID |

## 3. Relational schema (`Create_Tables.py`)

Primary keys are **bold**, foreign keys are *italic*.

- **Routes**(**Route_Number**)
- **Stops**(**Stop_Number**, Stop_Name NOT NULL, Latitude, Longitude, Is_Active)
- **Schedules**(**Schedule_ID**, *Stop_Number* → Stops, *Route_Number* → Routes, Stop_Order, Schedule_Arrival_Time)
- **Vehicles**(**Vehicle_ID**, Capacity)
- **Drivers**(**Driver_ID**, First_Name NOT NULL, Last_Name NOT NULL, Shift_Start_Time, Shift_End_Time)
- **Trips**(**Trip_ID**, *Route_Number* → Routes, *Vehicle_ID* → Vehicles, *Driver_ID* → Drivers, Start_Time, End_Time, Actual_Start_Time, Actual_End_Time)
- **Passengers**(**Passenger_ID**, First_Name NOT NULL, Last_Name NOT NULL)
- **Tickets**(**Ticket_ID**, *Trip_ID* → Trips, *Passenger_ID* → Passengers)
- **GPS_Records**(**GPS_Record_ID**, *Vehicle_ID* → Vehicles, TimeStamp, Latitude, Longitude)

**Constraints:** NOT NULL on names and on a ticket's trip and passenger; CHECK constraints keep latitude between -90 and 90, longitude between -180 and 180, Is_Active 0 or 1, Stop_Order above 0, a trip's End_Time after its Start_Time, and Capacity above 0.

All primary keys are `INTEGER PRIMARY KEY`, so SQLite assigns the next number when one is not given (Routes uses `AUTOINCREMENT`). Foreign keys are declared on every relationship; the app checks them before deleting a record that others still use.

## 4. Normalization

**First normal form.** Every column holds one value: no lists of stops on a route, no repeating "passenger1, passenger2" columns on a trip. A route's stops are separate rows in Schedules, and a trip's riders are separate rows in Tickets. Every table has a primary key.

**Second normal form.** Every table has a single-column primary key, so no column can depend on only part of a key.

**Third normal form / BCNF.** No non-key column depends on another non-key column:
- A ticket stores only Trip_ID and Passenger_ID. The route, bus, times and passenger name are reached through joins rather than copied onto the ticket, so changing a trip's time or a passenger's name updates every ticket at once.
- A trip stores the IDs of its route, bus and driver, not the driver's name or the bus's capacity.
- Schedules stores Stop_Number, not the stop's name or location, which live only in Stops.
- The determinant of every dependency is a primary key, so the schema is also in BCNF.

**Why Schedules exists.** A route visits many stops and a stop is served by many routes. Putting stops on Routes (or routes on Stops) would break 1NF; Schedules resolves the many-to-many relationship and also holds the facts that belong to the pair: the stop's order on that route and its arrival time.

**Deliberate choice.** Delay is not stored. "Minutes late" is computed from Start_Time and Actual_Start_Time when queried (see the `v_trip_status` view), so it can never disagree with the times.

## 5. Indexes and views

See `Advanced_Queries.sql`: 7 indexes on the foreign keys and lookup columns, and 3 views (`v_trip_status`, `v_ticket_details`, `v_route_stops`). SQLite has no stored procedures; the functions in `Insert_Data.py`, `Update_Data.py` and `Delete_Data.py` fill that role, each wrapping one parameterized statement.
