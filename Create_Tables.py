import sqlite3


conn = sqlite3.connect('public_transportation.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Routes (
        Route_Number INTEGER PRIMARY KEY
);
''')
conn.commit()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Stops (
        Stop_Number INTEGER PRIMARY KEY,
        Stop_Name TEXT NOT NULL,
        Latitude REAL,
        Longitude REAL,
        Is_Active NUMERIC
);
''')
conn.commit()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Schedules (
        Schedule_ID INTEGER PRIMARY KEY,
        Stop_Number INTEGER,
        Route_Number INTEGER,
        Stop_Order INTEGER,
        Schedule_Arrival_Time NUMERIC,
        FOREIGN KEY (Stop_Number) REFERENCES Stops(Stop_Number),
        FOREIGN KEY (Route_Number) REFERENCES Routes(Route_Number)
 );
   ''' )
conn.commit()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Trips (
        Trip_ID INTEGER PRIMARY KEY,
        Route_Number INTEGER,
        Vehicle_ID INTEGER,
        Driver_ID INTEGER,
        Start_Time NUMERIC,
        End_Time NUMERIC,
        Actual_Start_Time NUMERIC,
        Actual_End_Time NUMERIC,
        FOREIGN KEY (Route_Number) REFERENCES Routes(Route_Number),
        FOREIGN KEY (Vehicle_ID) REFERENCES Vehicles(Vehicle_ID),
        FOREIGN KEY (Driver_ID) REFERENCES Drivers(Driver_ID)
);
''')
conn.commit()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Tickets (
        Ticket_ID INTEGER PRIMARY KEY,
        Trip_ID INTEGER,
        Passenger_ID INTEGER,
        FOREIGN KEY (Trip_ID) REFERENCES Trips(Trip_ID),
        FOREIGN KEY (Passenger_ID) REFERENCES Passengers(Passenger_ID)
);
''')
conn.commit()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Vehicles (
        Vehicle_ID INTEGER PRIMARY KEY,
        Capacity INTEGER
);
''')
conn.commit()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Drivers (
        Driver_ID INTEGER PRIMARY KEY,
        First_Name TEXT NOT NULL,
        Last_Name TEXT NOT NULL,
        Shift_Start_Time NUMERIC,
        Shift_End_Time NUMERIC
);
''')
conn.commit()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Passengers (
        Passenger_ID INTEGER PRIMARY KEY,
        First_Name TEXT NOT NULL,
        Last_Name TEXT NOT NULL
);
''')
conn.commit()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS GPS_Records (
        GPS_Record_ID INTEGER PRIMARY KEY,
        Vehicle_ID INTEGER,
        TimeStamp NUMERIC,
        Latitude REAL,
        Longitude REAL,
        FOREIGN KEY (Vehicle_ID) REFERENCES Vehicles(Vehicle_ID)
);
''')
conn.commit()


