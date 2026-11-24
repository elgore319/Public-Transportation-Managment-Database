import Create_Tables
import sqlite3

conn = sqlite3.connect('public_transportation.db')
cursor = conn.cursor()

def insert_route(route_number):
    conn = sqlite3.connect('public_transportation.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Routes (Route_Number) VALUES (?)", (route_number,))
    conn.commit()
    conn.close()
    return cursor.lastrowid

def insert_stop(stop_number,stop_name,latitude,longitude,is_active):
    conn = sqlite3.connect('public_transportation.db')
    cursor  = conn.cursor()
    cursor.execute("INSERT INTO Stops (stop_number,stop_name,latitude,longitude,is_active) VALUES (?, ?, ?, ?, ?)", 
              (stop_number,stop_name,latitude,longitude,is_active))
    conn.commit()
    conn.close()
    return cursor.lastrowid

def insert_schedules(schedule_ID, stop_number, route_number, stop_order, schedule_arrival_time):
    conn = sqlite3.connect('public_transportation.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Schedules (schedule_ID, stop_number, route_number, stop_order, schedule_arrival_time) VALUES (?, ?, ?, ?, ?)",
                    (schedule_ID, stop_number, route_number, stop_order, schedule_arrival_time))
    conn.commit()
    conn.close()
    return cursor.lastrowid

def insert_trips(trip_id, route_number, vehicle_id, driver_id, start_time, end_time, actual_start_time, actual_end_time):
    conn = sqlite3.connect('public_transportation.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Trips (trip_id, route_number, vehicle_id, driver_id, start_time, end_time, actual_start_time, actual_end_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (trip_id, route_number, vehicle_id, driver_id, start_time, end_time, actual_start_time, actual_end_time))
    conn.commit()
    conn.close()
    return cursor.lastrowid

def insert_tickets(ticket_id, trip_id, passenger_id):
    conn = sqlite3.connect('public_transportation.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Tickets (ticket_id, trip_id, passenger_id) VALUES (?, ?, ?)", (ticket_id, trip_id, passenger_id))
    conn.commit()
    conn.close()
    return cursor.lastrowid

def insert_vehicles(vehicle_id, capacity):
    conn = sqlite3.connect('public_transportation.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Vehicles (vehicle_id, capacity) VALUES (?, ?)", (vehicle_id, capacity))
    conn.commit()
    conn.close()
    return cursor.lastrowid

def insert_drivers(driver_id, first_name, last_name, shift_start_time, shift_end_time):
    conn = sqlite3.connect('public_transportation.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Drivers (driver_id, first_name, last_name, shift_start_time, shift_end_time) VALUES (?, ?, ?, ?, ?)", 
                   (driver_id, first_name, last_name, shift_start_time, shift_end_time))
    conn.commit()
    conn.close()
    return cursor.lastrowid

def insert_passengers(passenger_id, first_name, last_name):
    conn = sqlite3.connect('public_transportation.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Passengers (passenger_id, first_name, last_name) VALUES (?, ?, ?)", 
                   (passenger_id, first_name, last_name))
    conn.commit()
    conn.close()
    return cursor.lastrowid

def insert_gps_records(gps_record_id, vehicle_id, timeStamp, latitude, longitude):
    conn = sqlite3.connect('public_transportation.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO GPS_Records (gps_record_id, vehicle_id, timeStamp, latitude, longitude) VALUES (?, ?, ?, ?, ?)", 
                   (gps_record_id, vehicle_id, timeStamp, latitude, longitude))
    conn.commit()
    conn.close()
    return cursor.lastrowid




