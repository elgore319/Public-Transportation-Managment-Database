import sqlite3
import os

# The database file sits in the same folder as this file
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public_transportation.db")


def run_query(sql, params=()):
    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return rows


# Ticket searches join Tickets -> Trips (route, bus, times) and Tickets -> Passengers (name)
TICKET_SQL = """
    SELECT k.Ticket_ID,
           p.First_Name || ' ' || p.Last_Name,
           t.Route_Number,
           t.Vehicle_ID,
           t.Start_Time,
           t.End_Time,
           CASE
               WHEN t.Actual_Start_Time IS NULL THEN 'Scheduled'
               WHEN t.Actual_Start_Time > t.Start_Time THEN 'Late'
               ELSE 'On Time'
           END
    FROM Tickets k
    JOIN Trips t ON t.Trip_ID = k.Trip_ID
    JOIN Passengers p ON p.Passenger_ID = k.Passenger_ID
"""
TICKET_HEADINGS = ["Ticket #", "Passenger", "Route", "Bus", "Departs", "Arrives", "Status"]


def search_ticket(ticket_id):
    rows = run_query(TICKET_SQL + " WHERE k.Ticket_ID = ?", (ticket_id,))
    return TICKET_HEADINGS, rows


def search_passenger(name):
    # Matches first name, last name, or "first last"
    text = "%" + name + "%"
    rows = run_query(TICKET_SQL + """
        WHERE p.First_Name LIKE ? OR p.Last_Name LIKE ?
           OR p.First_Name || ' ' || p.Last_Name LIKE ?
        ORDER BY t.Start_Time
    """, (text, text, text))
    return TICKET_HEADINGS, rows


def search_route(route_number):
    # Every stop on a route with its scheduled arrival times
    rows = run_query("""
        SELECT sc.Stop_Order, s.Stop_Name, sc.Schedule_Arrival_Time
        FROM Schedules sc
        JOIN Stops s ON s.Stop_Number = sc.Stop_Number
        WHERE sc.Route_Number = ?
        ORDER BY sc.Schedule_Arrival_Time, sc.Stop_Order
    """, (route_number,))
    return ["Stop #", "Stop", "Arrives"], rows


def search_stop(stop_name):
    # Every bus that comes to stops matching the name, in time order
    rows = run_query("""
        SELECT s.Stop_Name, sc.Schedule_Arrival_Time, sc.Route_Number
        FROM Schedules sc
        JOIN Stops s ON s.Stop_Number = sc.Stop_Number
        WHERE s.Stop_Name LIKE ?
        ORDER BY sc.Schedule_Arrival_Time
    """, ("%" + stop_name + "%",))
    return ["Stop", "Arrives", "Route"], rows


# The "Search by" dropdown in the GUI uses these names
SEARCHES = {
    "Ticket #": search_ticket,
    "Passenger Name": search_passenger,
    "Route #": search_route,
    "Stop Name": search_stop,
}