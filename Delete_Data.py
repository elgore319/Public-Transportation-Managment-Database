import Create_Tables
import sqlite3

conn = sqlite3.connect('public_transportation.db')
cursor = conn.cursor()

def delete_route(route_number):
    conn = sqlite3.connect('public_transportation.db')
    c= conn.cursor()
    c.execute("DELETE FROM Routes WHERE route_number = ?", (route_number,))
    conn.commit()
    conn.close()

def delete_stop(stop_number):
    conn = sqlite3.connect('public_transportation.db')
    c= conn.cursor()
    c.execute("DELETE FROM Stops WHERE stop_number = ?", (stop_number,))
    conn.commit()
    conn.close()

def delete_schedules(schedule_ID):
    conn = sqlite3.connect('public_transportation.db')
    c= conn.cursor()
    c.execute("DELETE FROM Schedules WHERE schedule_ID = ?", (schedule_ID,))
    conn.commit()
    conn.close()

def delete_trips(trip_id):
    conn = sqlite3.connect('public_transportation.db')
    c= conn.cursor()
    c.execute("DELETE FROM Trips WHERE trip_id = ?", (trip_id,))
    conn.commit()
    conn.close()

def delete_tickets(ticket_id):
    conn = sqlite3.connect('public_transportation.db')
    c= conn.cursor()
    c.execute("DELETE FROM Tickets WHERE ticket_id = ?", (ticket_id,))
    conn.commit()
    conn.close()

def delete_vehicles(vehicle_id):
    conn = sqlite3.connect('public_transportation.db')
    c= conn.cursor()
    c.execute("DELETE FROM Vehicles WHERE vehicle_id = ?", (vehicle_id,))
    conn.commit()
    conn.close()

def delete_passenger(passenger_id):
    conn = sqlite3.connect('public_transportation.db')
    c= conn.cursor()
    c.execute("DELETE FROM Passengers WHERE passenger_id = ?", (passenger_id,))
    conn.commit()
    conn.close()

def delete_gps_records(gps_record_id):
    conn = sqlite3.connect('public_transportation.db')
    c= conn.cursor()
    c.execute("DELETE FROM GPS_Records WHERE gps_record_id = ?", (gps_record_id,))
    conn.commit()
    conn.close()