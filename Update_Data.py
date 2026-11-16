import Create_Tables
import sqlite3

conn = sqlite3.connect('public_transportation.db')
cursor = conn.cursor()


def update_route(route_number):
    conn = sqlite3.connect('public_transportation.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE contacts SET route_number = ? WHERE id = ?", (route_number))
    conn.commit()
    conn.close()

def update_stop(stop_number,stop_name,latitude,longitude,is_active):
    conn = sqlite3.connect('public_transportation.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE contacts SET stop_number = ? stop_name = ? latitude = ? longitude = ? is_active = ? WHERE id = ?", 
              (stop_number,stop_name,latitude,longitude,is_active))
    conn.commit()
    conn.close()

def update_schedules(schedule_ID, stop_number, route_number, stop_order, schedule_arrival_time):
    conn = sqlite3.connect('public_transportation.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE contacts SET schedule_ID = ? stop_number = ? route_number = ? stop_order = ? schedule_arrival_time = ? WHERE id = ?", 
              (schedule_ID, stop_number, route_number, stop_order, schedule_arrival_time))
    conn.commit()
    conn.close()

def update_trips(trip_id, route_number, vehicle_id, driver_id, start_time, end_time, actual_start_time, actual_end_time):
    conn = sqlite3.connect('public_transportation.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE contacts SET trip_id= ? route_number = ? vehicle_id = ? driver_id = ? start_time = ? end_time = ? actual_start_time = ? actual_end_time = ? WHERE id = ?", 
              (trip_id, route_number, vehicle_id, driver_id, start_time, end_time, actual_start_time, actual_end_time))
    conn.commit()
    conn.close()

def update_tickets(ticket_id, trip_id, passenger_id):
    conn = sqlite3.connect('public_transportation.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE contacts SET ticket_id = ? trip_id = ? passenger_id = ? WHERE id = ?", (ticket_id, trip_id, passenger_id))
    conn.commit()
    conn.close()

def update_vehicles(vehicle_id, capacity):
    conn = sqlite3.connect('public_transportation.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE contacts SET vehicle_id = ? capacity = ? WHERE id = ?", (vehicle_id, capacity))
    conn.commit()
    conn.close()

def update_drivers(driver_id, first_name, last_name, shift_start_time, shift_end_time):
    conn = sqlite3.connect('public_transportation.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE contacts SET driver_id = ? first_name = ? last_name = ? shift_start_time = ? shift_end_time = ? WHERE id = ?", 
                   (driver_id, first_name, last_name, shift_start_time, shift_end_time))
    conn.commit()
    conn.close()

def update_passengers(passenger_id, first_name, last_name):
    conn = sqlite3.connect('public_transportation.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE contacts SET passenger_id = ? first_name = ? last_name = ? WHERE id = ?", 
                   (passenger_id, first_name, last_name))
    conn.commit()
    conn.close()

def update_gps_records(gps_record_id, vehicle_id, timeStamp, latitude, longitude):
    conn = sqlite3.connect('public_transportation.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE contacts SET gps_record_id = ? vehicle_id = ? timeStamp = ? latitude = ? longtiude =? WHERE id = ?", 
                   (gps_record_id, vehicle_id, timeStamp, latitude, longitude))
    conn.commit()
    conn.close()