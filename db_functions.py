import sqlite3
import os

# The database file sits in the same folder as this file
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public_transportation.db")
TABLES = (
    "Routes",
    "Stops",
    "Schedules",
    "Trips",
    "Tickets",
    "Vehicles",
    "Drivers",
    "Passengers",
    "GPS_Records",
)


def run_query(sql, params=()):
    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def _get_table_info(table_name):
    if table_name not in TABLES:
        raise ValueError("Unknown table: " + table_name)

    conn = sqlite3.connect(DB_FILE)
    try:
        return conn.execute('PRAGMA table_info("' + table_name + '")').fetchall()
    finally:
        conn.close()


def get_table_schema(table_name):
    """Return each table column's name, declared type, and primary-key flag."""
    return [(row[1], row[2], bool(row[5])) for row in _get_table_info(table_name)]


def get_table_rows(table_name):
    schema = get_table_schema(table_name)
    columns = [column[0] for column in schema]
    quoted_table = '"' + table_name + '"'
    conn = sqlite3.connect(DB_FILE)
    try:
        rows = conn.execute("SELECT * FROM " + quoted_table).fetchall()
        return columns, rows
    finally:
        conn.close()


def insert_record(table_name, values):
    columns = [column[0] for column in get_table_schema(table_name)]
    if any(column not in columns for column in values):
        raise ValueError("An insert field is not part of " + table_name)

    quoted_table = '"' + table_name + '"'
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        if values:
            column_names = ", ".join('"' + column + '"' for column in values)
            placeholders = ", ".join("?" for _ in values)
            cursor = conn.execute(
                "INSERT INTO " + quoted_table + " (" + column_names + ") "
                "VALUES (" + placeholders + ")",
                tuple(values.values()),
            )
        else:
            cursor = conn.execute("INSERT INTO " + quoted_table + " DEFAULT VALUES")
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update_record(table_name, primary_key, primary_key_value, values):
    schema = get_table_schema(table_name)
    columns = [column[0] for column in schema]
    primary_keys = [column[0] for column in schema if column[2]]
    if primary_key not in primary_keys:
        raise ValueError("Invalid primary key for " + table_name)
    if any(column not in columns or column == primary_key for column in values):
        raise ValueError("An update field is not editable in " + table_name)
    if not values:
        raise ValueError("Enter at least one field to update")

    assignments = ", ".join('"' + column + '" = ?' for column in values)
    quoted_table = '"' + table_name + '"'
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.execute(
            "UPDATE " + quoted_table + " SET " + assignments +
            ' WHERE "' + primary_key + '" = ?',
            tuple(values.values()) + (primary_key_value,),
        )
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def delete_record(table_name, primary_key, primary_key_value):
    schema = get_table_schema(table_name)
    primary_keys = [column[0] for column in schema if column[2]]
    if primary_key not in primary_keys:
        raise ValueError("Invalid primary key for " + table_name)

    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.execute(
            'DELETE FROM "' + table_name + '" WHERE "' + primary_key + '" = ?',
            (primary_key_value,),
        )
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


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