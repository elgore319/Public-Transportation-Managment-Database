import Create_Tables
import sqlite3
from db_functions import DB_FILE

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()


def update_route(route_number):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE Routes SET route_number = ? WHERE route_number = ?", (route_number, route_number))
    conn.commit()
    conn.close()

def update_stop(stop_number,stop_name,latitude,longitude,is_active):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE Stops SET stop_name = ?, latitude = ?, longitude = ?, is_active = ? WHERE stop_number = ?", 
              (stop_name,latitude,longitude,is_active,stop_number))
    conn.commit()
    conn.close()

def update_schedules(schedule_ID, stop_number, route_number, stop_order, schedule_arrival_time):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE Schedules SET stop_number = ?, route_number = ?, stop_order = ?, schedule_arrival_time = ? WHERE schedule_ID = ?", 
              (stop_number, route_number, stop_order, schedule_arrival_time, schedule_ID))
    conn.commit()
    conn.close()

def update_trips(trip_id, route_number, vehicle_id, driver_id, start_time, end_time, actual_start_time, actual_end_time):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE Trips SET route_number = ?, vehicle_id = ?, driver_id = ?, start_time = ?, end_time = ?, actual_start_time = ?, actual_end_time = ? WHERE trip_id = ?", 
              (route_number, vehicle_id, driver_id, start_time, end_time, actual_start_time, actual_end_time, trip_id))
    conn.commit()
    conn.close()

def update_tickets(ticket_id, trip_id, passenger_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE Tickets SET trip_id = ?, passenger_id = ? WHERE ticket_id = ?", (trip_id, passenger_id, ticket_id))
    conn.commit()
    conn.close()

def update_vehicles(vehicle_id, capacity):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE Vehicles SET capacity = ? WHERE vehicle_id = ?", (capacity, vehicle_id))
    conn.commit()
    conn.close()

def update_drivers(driver_id, first_name, last_name, shift_start_time, shift_end_time):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE Drivers SET first_name = ?, last_name = ?, shift_start_time = ?, shift_end_time = ? WHERE driver_id = ?", 
                   (first_name, last_name, shift_start_time, shift_end_time, driver_id))
    conn.commit()
    conn.close()

def update_passengers(passenger_id, first_name, last_name):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE Passengers SET first_name = ?, last_name = ? WHERE passenger_id = ?", 
                   (first_name, last_name, passenger_id))
    conn.commit()
    conn.close()

def update_gps_records(gps_record_id, vehicle_id, timeStamp, latitude, longitude):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE GPS_Records SET vehicle_id = ?, timeStamp = ?, latitude = ?, longitude = ? WHERE gps_record_id = ?", 
                   (vehicle_id, timeStamp, latitude, longitude, gps_record_id))
    conn.commit()
    conn.close()