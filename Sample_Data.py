# Sample data for testing the GUI.
# Fills the 9 tables from Create_Tables.py in public_transportation.db.
# Run Create_Tables.py first, then run this file once: python Sample_Data.py
#
# Every row has a fixed ID and uses INSERT OR IGNORE, so running this
# file again skips rows that are already there instead of making duplicates.
# Times are stored as "HH:MM" text.

import sqlite3
import os

# The database file sits in the same folder as this file
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public_transportation.db")

conn = sqlite3.connect(DB_FILE)
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()

# Routes (Route_Number)
routes = [(1,), (2,), (3,)]
cursor.executemany("INSERT OR IGNORE INTO Routes VALUES (?)", routes)

# Stops (Stop_Number, Stop_Name, Latitude, Longitude, Is_Active)
stops = [
    (1, "Downtown Transit Center", 36.6103, -88.3148, 1),
    (2, "Main St & 4th St", 36.6121, -88.3172, 1),
    (3, "University Center", 36.6162, -88.3221, 1),
    (4, "Library", 36.6150, -88.3250, 1),
    (5, "Hospital", 36.6050, -88.3080, 1),
    (6, "Walmart Plaza", 36.5985, -88.3010, 1),
    (7, "Old Depot", 36.6090, -88.3300, 0),   # closed stop
]
cursor.executemany("INSERT OR IGNORE INTO Stops VALUES (?, ?, ?, ?, ?)", stops)

# Schedules (Schedule_ID, Stop_Number, Route_Number, Stop_Order, Schedule_Arrival_Time)
schedules = [
    # Route 1: Downtown -> Main St -> University Center -> Library
    (1, 1, 1, 1, "08:00"), (2, 2, 1, 2, "08:08"), (3, 3, 1, 3, "08:15"), (4, 4, 1, 4, "08:20"),
    (5, 1, 1, 1, "12:00"), (6, 2, 1, 2, "12:08"), (7, 3, 1, 3, "12:15"), (8, 4, 1, 4, "12:20"),
    # Route 2: Downtown -> Hospital -> Walmart Plaza
    (9, 1, 2, 1, "09:00"), (10, 5, 2, 2, "09:12"), (11, 6, 2, 3, "09:25"),
    (12, 1, 2, 1, "15:00"), (13, 5, 2, 2, "15:12"), (14, 6, 2, 3, "15:25"),
    # Route 3: University Center -> Main St -> Hospital
    (15, 3, 3, 1, "10:30"), (16, 2, 3, 2, "10:40"), (17, 5, 3, 3, "10:55"),
]
cursor.executemany("INSERT OR IGNORE INTO Schedules VALUES (?, ?, ?, ?, ?)", schedules)

# Vehicles (Vehicle_ID, Capacity)
vehicles = [(101, 40), (102, 40), (205, 30), (310, 25)]
cursor.executemany("INSERT OR IGNORE INTO Vehicles VALUES (?, ?)", vehicles)

# Drivers (Driver_ID, First_Name, Last_Name, Shift_Start_Time, Shift_End_Time)
drivers = [
    (1, "Maria", "Lopez", "06:00", "14:00"),
    (2, "James", "Carter", "07:00", "15:00"),
    (3, "Aisha", "Brown", "12:00", "20:00"),
]
cursor.executemany("INSERT OR IGNORE INTO Drivers VALUES (?, ?, ?, ?, ?)", drivers)

# Trips (Trip_ID, Route_Number, Vehicle_ID, Driver_ID,
#        Start_Time, End_Time, Actual_Start_Time, Actual_End_Time)
trips = [
    (1, 1, 101, 1, "08:00", "08:20", "08:00", "08:21"),   # on time
    (2, 1, 102, 3, "12:00", "12:20", "12:09", "12:31"),   # late
    (3, 2, 205, 2, "09:00", "09:25", "09:00", "09:24"),   # on time
    (4, 2, 205, 3, "15:00", "15:25", None, None),         # has not left yet
    (5, 3, 310, 2, "10:30", "10:55", "10:42", "11:05"),   # late
]
cursor.executemany("INSERT OR IGNORE INTO Trips VALUES (?, ?, ?, ?, ?, ?, ?, ?)", trips)

# Passengers (Passenger_ID, First_Name, Last_Name)
passengers = [
    (1, "Emma", "Smith"),
    (2, "Liam", "Johnson"),
    (3, "Olivia", "Williams"),
    (4, "Noah", "Davis"),
    (5, "Ava", "Smith"),
    (6, "Lucas", "Miller"),
]
cursor.executemany("INSERT OR IGNORE INTO Passengers VALUES (?, ?, ?)", passengers)

# Tickets (Ticket_ID, Trip_ID, Passenger_ID)
tickets = [
    (1001, 1, 1), (1002, 1, 2), (1003, 2, 3), (1004, 2, 1),
    (1005, 3, 4), (1006, 4, 5), (1007, 5, 6), (1008, 5, 2),
]
cursor.executemany("INSERT OR IGNORE INTO Tickets VALUES (?, ?, ?)", tickets)

# GPS_Records (GPS_Record_ID, Vehicle_ID, TimeStamp, Latitude, Longitude)
gps_records = [
    (1, 101, "08:00", 36.6103, -88.3148),
    (2, 101, "08:08", 36.6121, -88.3172),
    (3, 101, "08:16", 36.6162, -88.3221),
    (4, 101, "08:21", 36.6150, -88.3250),
    (5, 205, "09:01", 36.6103, -88.3148),
    (6, 205, "09:12", 36.6050, -88.3080),
    (7, 205, "09:24", 36.5985, -88.3010),
]
cursor.executemany("INSERT OR IGNORE INTO GPS_Records VALUES (?, ?, ?, ?, ?)", gps_records)

conn.commit()
conn.close()
print("Sample data added to " + DB_FILE)
