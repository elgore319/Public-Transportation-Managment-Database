# Ticket, route and stop page. Needs the GUI-Integration db_functions.py.
import tkinter
import sqlite3
from tkinter import messagebox
from tkinter.ttk import *
import db_functions as db
import Insert_Data as ins
import Update_Data as upd
import Delete_Data as dele


def open_manage():
    
    

    NEW_ROUTE = "New route"
    
    root = tkinter.Tk()
    root.title("Transit Manager")
    root.geometry("360x640")
    
    top = Frame(root, padding=10)
    top.pack(fill="x")
    Label(top, text="Change:", font=("Arial", 12)).grid(row=0, column=0, sticky="w")
    choice = Combobox(top, values=["Ticket", "Route", "Stop", "Trip", "Vehicle", "Driver", "GPS Record"], state="readonly", width=28)
    choice.grid(row=1, column=0, sticky="ew")
    top.columnconfigure(0, weight=1)
    
    status = Label(root, wraplength=320)
    buttons = Frame(root, padding=10)
    buttons.pack(side="bottom", fill="x")
    status.pack(side="bottom", pady=10)
    
    
    def add_field(frame, row, text, widget):
        Label(frame, text=text).grid(row=row * 2, column=0, sticky="w")
        widget.grid(row=row * 2 + 1, column=0, sticky="ew", pady=(0, 10))
        frame.columnconfigure(0, weight=1)
        return widget
    
    
    def set_entry(field, value):
        field.delete(0, "end")
        field.insert(0, "" if value is None else value)
    
    
    def error(title, err):
        messagebox.showerror(title, str(err), parent=root)
    
    
    def need_read(thing):
        messagebox.showinfo("Read first", "Use Read to load the " + thing + " first.", parent=root)
    
    
    def route_numbers():
        return [row[0] for row in db.run_query("SELECT Route_Number FROM Routes ORDER BY Route_Number")]
    
    
    def stop_names():
        return {name: number for number, name in
                db.run_query("SELECT Stop_Number, Stop_Name FROM Stops ORDER BY Stop_Name")}
    
    
    # ---------------- Ticket ----------------
    ticket_frame = Frame(root, padding=10)
    t_first = add_field(ticket_frame, 0, "First Name:", Entry(ticket_frame, width=30))
    t_last = add_field(ticket_frame, 1, "Last Name:", Entry(ticket_frame, width=30))
    t_route = add_field(ticket_frame, 2, "Route:", Combobox(ticket_frame, state="readonly", width=28))
    ticket_id = None
    
    
    def ticket_show():
        t_route["values"] = route_numbers()
    
    
    def ticket_name():
        first, last = t_first.get().strip(), t_last.get().strip()
        if not first or not last:
            raise ValueError("Please enter the passenger's first and last name")
        return first, last
    
    
    def ticket_route():
        if not t_route.get():
            raise ValueError("Please choose a route")
        return int(t_route.get())
    
    
    def passenger_id(first, last):
        rows = db.run_query("SELECT Passenger_ID FROM Passengers WHERE First_Name = ? AND Last_Name = ? "
                            "ORDER BY Passenger_ID", (first, last))
        if rows:
            return rows[0][0]
        return ins.insert_passengers(None, first, last)
    
    
    def first_trip(route_number):
        rows = db.run_query("SELECT Trip_ID FROM Trips WHERE Route_Number = ? ORDER BY Start_Time, Trip_ID",
                            (route_number,))
        if not rows:
            raise ValueError("Route " + str(route_number) + " has no trips")
        return rows[0][0]
    
    
    def ticket_create():
        nonlocal ticket_id
        try:
            first, last = ticket_name()
            trip = first_trip(ticket_route())
            ticket_id = ins.insert_tickets(None, trip, passenger_id(first, last))
            status.configure(text="Ticket " + str(ticket_id) + " created for " + first + " " + last)
        except (sqlite3.Error, ValueError) as err:
            error("Could not create ticket", err)
    
    
    def ticket_read():
        nonlocal ticket_id
        try:
            first, last = ticket_name()
            sql = """
                SELECT k.Ticket_ID, t.Route_Number
                FROM Tickets k
                JOIN Passengers p ON p.Passenger_ID = k.Passenger_ID
                JOIN Trips t ON t.Trip_ID = k.Trip_ID
                WHERE p.First_Name = ? AND p.Last_Name = ?
            """
            params = (first, last)
            if t_route.get():
                sql += " AND t.Route_Number = ?"
                params += (int(t_route.get()),)
            rows = db.run_query(sql + " ORDER BY k.Ticket_ID DESC", params)
        except (sqlite3.Error, ValueError) as err:
            error("Could not read ticket", err)
            return
        if not rows:
            ticket_id = None
            status.configure(text="No ticket found for " + first + " " + last)
            return
        ticket_id = rows[0][0]
        t_route.set(rows[0][1])
        text = "Ticket " + str(ticket_id) + " loaded (Route " + str(rows[0][1]) + ")"
        if len(rows) > 1:
            text += ". " + str(len(rows)) + " tickets found, showing the newest"
        status.configure(text=text)
    
    
    def ticket_update():
        if ticket_id is None:
            return need_read("ticket")
        try:
            first, last = ticket_name()
            old = db.run_query("SELECT k.Trip_ID, t.Route_Number FROM Tickets k JOIN Trips t ON t.Trip_ID = k.Trip_ID "
                               "WHERE k.Ticket_ID = ?", (ticket_id,))
            if not old:
                raise ValueError("Ticket no longer exists")
            new_route = ticket_route()
            trip = old[0][0] if old[0][1] == new_route else first_trip(new_route)
            upd.update_tickets(ticket_id, trip, passenger_id(first, last))
            status.configure(text="Ticket " + str(ticket_id) + " updated")
        except (sqlite3.Error, ValueError) as err:
            error("Could not update ticket", err)
    
    
    def ticket_delete():
        nonlocal ticket_id
        if ticket_id is None:
            return need_read("ticket")
        if not messagebox.askyesno("Confirm delete", "Delete ticket " + str(ticket_id) + "?", parent=root):
            return
        try:
            dele.delete_tickets(ticket_id)
            status.configure(text="Ticket " + str(ticket_id) + " deleted")
            ticket_id = None
            t_first.delete(0, "end")
            t_last.delete(0, "end")
            t_route.set("")
        except sqlite3.Error as err:
            error("Could not delete ticket", err)
    
    
    # ---------------- Route ----------------
    route_frame = Frame(root, padding=10)
    r_route = add_field(route_frame, 0, "Route #:", Combobox(route_frame, state="readonly", width=28))
    r_stop = add_field(route_frame, 1, "Stop:", Combobox(route_frame, state="readonly", width=28))
    r_order = add_field(route_frame, 2, "Stop Order:", Entry(route_frame, width=30))
    r_time = add_field(route_frame, 3, "Arrival Time (HH:MM):", Entry(route_frame, width=30))
    stops = {}
    schedule_id = None
    
    
    def route_show():
        nonlocal stops
        stops = stop_names()
        r_route["values"] = [NEW_ROUTE] + route_numbers()
        r_stop["values"] = list(stops)
    
    
    def route_fields():
        if not r_stop.get():
            raise ValueError("Please choose a stop")
        order, time = r_order.get().strip(), r_time.get().strip()
        if not order or not time:
            raise ValueError("Please enter the stop order and arrival time")
        return {"Stop_Number": stops[r_stop.get()], "Stop_Order": int(order), "Schedule_Arrival_Time": time}
    
    
    def route_clear():
        nonlocal schedule_id
        schedule_id = None
        r_route.set("")
        r_stop.set("")
        r_order.delete(0, "end")
        r_time.delete(0, "end")
    
    
    def route_create():
        nonlocal schedule_id
        try:
            if not r_route.get():
                raise ValueError("Please choose a route, or New route")
            values = route_fields()
            if r_route.get() == NEW_ROUTE:
                route_number = ins.insert_route(None)
            else:
                route_number = int(r_route.get())
            schedule_id = ins.insert_schedules(None, values["Stop_Number"], route_number, values["Stop_Order"],
                                               values["Schedule_Arrival_Time"])
            route_show()
            r_route.set(route_number)
            status.configure(text="Stop added to Route " + str(route_number))
        except (sqlite3.Error, ValueError) as err:
            error("Could not create route", err)
    
    
    def route_read():
        nonlocal schedule_id
        if not r_route.get() or r_route.get() == NEW_ROUTE:
            messagebox.showinfo("Choose a route", "Choose a route to read.", parent=root)
            return
        sql = """
            SELECT sc.Schedule_ID, s.Stop_Name, sc.Stop_Order, sc.Schedule_Arrival_Time
            FROM Schedules sc
            JOIN Stops s ON s.Stop_Number = sc.Stop_Number
            WHERE sc.Route_Number = ?
        """
        params = (int(r_route.get()),)
        if r_stop.get():
            sql += " AND sc.Stop_Number = ?"
            params += (stops[r_stop.get()],)
        if r_order.get().strip():
            sql += " AND sc.Stop_Order = ?"
            params += (r_order.get().strip(),)
        if r_time.get().strip():
            sql += " AND sc.Schedule_Arrival_Time = ?"
            params += (r_time.get().strip(),)
        try:
            rows = db.run_query(sql + " ORDER BY sc.Schedule_Arrival_Time, sc.Stop_Order", params)
        except sqlite3.Error as err:
            error("Could not read route", err)
            return
        if not rows:
            schedule_id = None
            status.configure(text="No stops found on Route " + r_route.get())
            return
        schedule_id, name, order, time = rows[0]
        r_stop.set(name)
        set_entry(r_order, order)
        set_entry(r_time, time)
        text = "Loaded " + name + " on Route " + r_route.get()
        if len(rows) > 1:
            text += ". " + str(len(rows)) + " stops match, showing the first"
        status.configure(text=text)
    
    
    def route_update():
        if schedule_id is None:
            return need_read("stop on the route")
        try:
            values = route_fields()
            if not r_route.get() or r_route.get() == NEW_ROUTE:
                raise ValueError("Please choose a route")
            upd.update_schedules(schedule_id, values["Stop_Number"], int(r_route.get()), values["Stop_Order"],
                                 values["Schedule_Arrival_Time"])
            status.configure(text="Stop updated")
        except (sqlite3.Error, ValueError) as err:
            error("Could not update route", err)
    
    
    def route_delete():
        if schedule_id is None:
            return need_read("stop on the route")
        if not messagebox.askyesno("Confirm delete", "Delete " + r_stop.get() + " from Route " + r_route.get() + "?",
                                   parent=root):
            return
        route_number = int(r_route.get())
        try:
            dele.delete_schedules(schedule_id)
            text = "Stop deleted from Route " + str(route_number)
            if not db.run_query("SELECT 1 FROM Schedules WHERE Route_Number = ?", (route_number,)):
                if db.run_query("SELECT 1 FROM Trips WHERE Route_Number = ?", (route_number,)):
                    text += ". The route has no stops left but trips still use it"
                else:
                    dele.delete_route(route_number)
                    text = "Route " + str(route_number) + " deleted (it had no stops left)"
            route_clear()
            route_show()
            status.configure(text=text)
        except sqlite3.Error as err:
            error("Could not delete route", err)
    
    
    # ---------------- Stop ----------------
    stop_frame = Frame(root, padding=10)
    s_name = add_field(stop_frame, 0, "Stop Name:", Entry(stop_frame, width=30))
    s_lat = add_field(stop_frame, 1, "Latitude:", Entry(stop_frame, width=30))
    s_lon = add_field(stop_frame, 2, "Longitude:", Entry(stop_frame, width=30))
    s_active = add_field(stop_frame, 3, "Active:", Combobox(stop_frame, values=["Yes", "No"], state="readonly", width=28))
    s_active.current(0)
    stop_number = None
    
    
    def stop_show():
        pass
    
    
    def stop_name():
        name = s_name.get().strip()
        if not name:
            raise ValueError("Please enter a stop name")
        return name
    
    
    def stop_fields():
        lat, lon = s_lat.get().strip(), s_lon.get().strip()
        return {
            "Stop_Name": stop_name(),
            "Latitude": float(lat) if lat else None,
            "Longitude": float(lon) if lon else None,
            "Is_Active": 1 if s_active.get() == "Yes" else 0,
        }
    
    
    def stop_create():
        nonlocal stop_number
        try:
            values = stop_fields()
            stop_number = ins.insert_stop(None, values["Stop_Name"], values["Latitude"], values["Longitude"],
                                          values["Is_Active"])
            status.configure(text="Stop " + str(stop_number) + " created")
        except (sqlite3.Error, ValueError) as err:
            error("Could not create stop", err)
    
    
    def stop_read():
        nonlocal stop_number
        try:
            rows = db.run_query("SELECT Stop_Number, Stop_Name, Latitude, Longitude, Is_Active FROM Stops "
                                "WHERE Stop_Name LIKE ? ORDER BY Stop_Name", ("%" + stop_name() + "%",))
        except (sqlite3.Error, ValueError) as err:
            error("Could not read stop", err)
            return
        if not rows:
            stop_number = None
            status.configure(text="No stop found")
            return
        stop_number, name, lat, lon, is_active = rows[0]
        set_entry(s_name, name)
        set_entry(s_lat, lat)
        set_entry(s_lon, lon)
        s_active.set("Yes" if is_active else "No")
        text = "Loaded " + name
        if len(rows) > 1:
            text += ". " + str(len(rows)) + " stops match, showing the first"
        status.configure(text=text)
    
    
    def stop_update():
        if stop_number is None:
            return need_read("stop")
        try:
            values = stop_fields()
            upd.update_stop(stop_number, values["Stop_Name"], values["Latitude"], values["Longitude"],
                            values["Is_Active"])
            status.configure(text="Stop updated")
        except (sqlite3.Error, ValueError) as err:
            error("Could not update stop", err)
    
    
    def stop_delete():
        nonlocal stop_number
        if stop_number is None:
            return need_read("stop")
        if not messagebox.askyesno("Confirm delete", "Delete " + s_name.get() + "?", parent=root):
            return
        try:
            if db.run_query("SELECT 1 FROM Schedules WHERE Stop_Number = ?", (stop_number,)):
                raise sqlite3.IntegrityError
            dele.delete_stop(stop_number)
            stop_number = None
            for field in (s_name, s_lat, s_lon):
                field.delete(0, "end")
            s_active.current(0)
            status.configure(text="Stop deleted")
        except sqlite3.IntegrityError:
            error("Could not delete stop", "Routes still use this stop. Remove it from those routes first, "
                                           "or set Active to No.")
        except sqlite3.Error as err:
            error("Could not delete stop", err)
    
    
    def vehicle_ids():
        return [row[0] for row in db.run_query("SELECT Vehicle_ID FROM Vehicles ORDER BY Vehicle_ID")]
    
    
    def driver_names():
        rows = db.run_query("SELECT Driver_ID, First_Name, Last_Name FROM Drivers ORDER BY Last_Name, First_Name")
        return [str(d) + " - " + first + " " + last for d, first, last in rows]
    
    
    def picked_id(box, name):
        if not box.get():
            raise ValueError("Please choose a " + name)
        return int(str(box.get()).split(" - ")[0])
    
    
    def blank_none(field):
        return field.get().strip() or None
    
    
    # ---------------- Trip ----------------
    trip_frame = Frame(root, padding=10)
    tr_route = add_field(trip_frame, 0, "Route #:", Combobox(trip_frame, state="readonly", width=28))
    tr_vehicle = add_field(trip_frame, 1, "Vehicle #:", Combobox(trip_frame, state="readonly", width=28))
    tr_driver = add_field(trip_frame, 2, "Driver:", Combobox(trip_frame, state="readonly", width=28))
    tr_start = add_field(trip_frame, 3, "Start Time (HH:MM):", Entry(trip_frame, width=30))
    tr_end = add_field(trip_frame, 4, "End Time (HH:MM):", Entry(trip_frame, width=30))
    tr_actual_start = add_field(trip_frame, 5, "Actual Start Time (blank = not left yet):", Entry(trip_frame, width=30))
    tr_actual_end = add_field(trip_frame, 6, "Actual End Time:", Entry(trip_frame, width=30))
    trip_id = None
    
    
    def trip_show():
        tr_route["values"] = route_numbers()
        tr_vehicle["values"] = vehicle_ids()
        tr_driver["values"] = driver_names()
    
    
    def trip_fields():
        start, end = tr_start.get().strip(), tr_end.get().strip()
        if not start or not end:
            raise ValueError("Please enter the start and end time")
        return (picked_id(tr_route, "route"), picked_id(tr_vehicle, "vehicle"), picked_id(tr_driver, "driver"),
                start, end, blank_none(tr_actual_start), blank_none(tr_actual_end))
    
    
    def trip_create():
        nonlocal trip_id
        try:
            trip_id = ins.insert_trips(None, *trip_fields())
            status.configure(text="Trip " + str(trip_id) + " created")
        except (sqlite3.Error, ValueError) as err:
            error("Could not create trip", err)
    
    
    def trip_read():
        nonlocal trip_id
        sql = """
            SELECT Trip_ID, Route_Number, Vehicle_ID, Driver_ID, Start_Time, End_Time, Actual_Start_Time, Actual_End_Time
            FROM Trips WHERE 1 = 1
        """
        params = ()
        try:
            if tr_route.get():
                sql += " AND Route_Number = ?"
                params += (picked_id(tr_route, "route"),)
            if tr_vehicle.get():
                sql += " AND Vehicle_ID = ?"
                params += (picked_id(tr_vehicle, "vehicle"),)
            if tr_driver.get():
                sql += " AND Driver_ID = ?"
                params += (picked_id(tr_driver, "driver"),)
            if tr_start.get().strip():
                sql += " AND Start_Time = ?"
                params += (tr_start.get().strip(),)
            if not params:
                raise ValueError("Choose a route, vehicle or driver, or enter a start time to read")
            rows = db.run_query(sql + " ORDER BY Start_Time, Trip_ID", params)
        except (sqlite3.Error, ValueError) as err:
            error("Could not read trip", err)
            return
        if not rows:
            trip_id = None
            status.configure(text="No trip found")
            return
        trip_id, route, vehicle, driver, start, end, actual_start, actual_end = rows[0]
        tr_route.set(route)
        tr_vehicle.set(vehicle)
        tr_driver.set(next((d for d in driver_names() if d.split(" - ")[0] == str(driver)), ""))
        for field, value in ((tr_start, start), (tr_end, end), (tr_actual_start, actual_start), (tr_actual_end, actual_end)):
            set_entry(field, value)
        text = "Trip " + str(trip_id) + " loaded"
        if len(rows) > 1:
            text += ". " + str(len(rows)) + " trips match, showing the first"
        status.configure(text=text)
    
    
    def trip_update():
        if trip_id is None:
            return need_read("trip")
        try:
            upd.update_trips(trip_id, *trip_fields())
            status.configure(text="Trip " + str(trip_id) + " updated")
        except (sqlite3.Error, ValueError) as err:
            error("Could not update trip", err)
    
    
    def trip_delete():
        nonlocal trip_id
        if trip_id is None:
            return need_read("trip")
        if db.run_query("SELECT 1 FROM Tickets WHERE Trip_ID = ?", (trip_id,)):
            return error("Could not delete trip", "Tickets are still on this trip.")
        if not messagebox.askyesno("Confirm delete", "Delete trip " + str(trip_id) + "?", parent=root):
            return
        try:
            dele.delete_trips(trip_id)
            status.configure(text="Trip " + str(trip_id) + " deleted")
            trip_id = None
            for box in (tr_route, tr_vehicle, tr_driver):
                box.set("")
            for field in (tr_start, tr_end, tr_actual_start, tr_actual_end):
                field.delete(0, "end")
        except sqlite3.Error as err:
            error("Could not delete trip", err)
    
    
    # ---------------- Vehicle ----------------
    vehicle_frame = Frame(root, padding=10)
    v_id = add_field(vehicle_frame, 0, "Vehicle # (blank = next number):", Entry(vehicle_frame, width=30))
    v_capacity = add_field(vehicle_frame, 1, "Capacity:", Entry(vehicle_frame, width=30))
    vehicle_id = None
    
    
    def vehicle_show():
        pass
    
    
    def vehicle_capacity():
        text = v_capacity.get().strip()
        if not text:
            raise ValueError("Please enter the capacity")
        return int(text)
    
    
    def vehicle_create():
        nonlocal vehicle_id
        try:
            typed = v_id.get().strip()
            vehicle_id = ins.insert_vehicles(int(typed) if typed else None, vehicle_capacity())
            set_entry(v_id, vehicle_id)
            status.configure(text="Vehicle " + str(vehicle_id) + " created")
        except (sqlite3.Error, ValueError) as err:
            error("Could not create vehicle", err)
    
    
    def vehicle_read():
        nonlocal vehicle_id
        try:
            typed = v_id.get().strip()
            if not typed:
                raise ValueError("Please enter a vehicle number")
            rows = db.run_query("SELECT Vehicle_ID, Capacity FROM Vehicles WHERE Vehicle_ID = ?", (int(typed),))
        except (sqlite3.Error, ValueError) as err:
            error("Could not read vehicle", err)
            return
        if not rows:
            vehicle_id = None
            status.configure(text="No vehicle " + typed)
            return
        vehicle_id = rows[0][0]
        set_entry(v_capacity, rows[0][1])
        status.configure(text="Vehicle " + str(vehicle_id) + " loaded")
    
    
    def vehicle_update():
        if vehicle_id is None:
            return need_read("vehicle")
        try:
            upd.update_vehicles(vehicle_id, vehicle_capacity())
            set_entry(v_id, vehicle_id)
            status.configure(text="Vehicle " + str(vehicle_id) + " updated")
        except (sqlite3.Error, ValueError) as err:
            error("Could not update vehicle", err)
    
    
    def vehicle_delete():
        nonlocal vehicle_id
        if vehicle_id is None:
            return need_read("vehicle")
        if db.run_query("SELECT 1 FROM Trips WHERE Vehicle_ID = ? UNION SELECT 1 FROM GPS_Records WHERE Vehicle_ID = ?",
                        (vehicle_id, vehicle_id)):
            return error("Could not delete vehicle", "Trips or GPS records still use this vehicle.")
        if not messagebox.askyesno("Confirm delete", "Delete vehicle " + str(vehicle_id) + "?", parent=root):
            return
        try:
            dele.delete_vehicles(vehicle_id)
            status.configure(text="Vehicle " + str(vehicle_id) + " deleted")
            vehicle_id = None
            v_id.delete(0, "end")
            v_capacity.delete(0, "end")
        except sqlite3.Error as err:
            error("Could not delete vehicle", err)
    
    
    # ---------------- Driver ----------------
    driver_frame = Frame(root, padding=10)
    d_first = add_field(driver_frame, 0, "First Name:", Entry(driver_frame, width=30))
    d_last = add_field(driver_frame, 1, "Last Name:", Entry(driver_frame, width=30))
    d_shift_start = add_field(driver_frame, 2, "Shift Start (HH:MM):", Entry(driver_frame, width=30))
    d_shift_end = add_field(driver_frame, 3, "Shift End (HH:MM):", Entry(driver_frame, width=30))
    driver_id = None
    
    
    def driver_show():
        pass
    
    
    def driver_name():
        first, last = d_first.get().strip(), d_last.get().strip()
        if not first or not last:
            raise ValueError("Please enter the driver's first and last name")
        return first, last
    
    
    def driver_create():
        nonlocal driver_id
        try:
            first, last = driver_name()
            driver_id = ins.insert_drivers(None, first, last, blank_none(d_shift_start), blank_none(d_shift_end))
            status.configure(text="Driver " + str(driver_id) + " created")
        except (sqlite3.Error, ValueError) as err:
            error("Could not create driver", err)
    
    
    def driver_read():
        nonlocal driver_id
        try:
            first, last = driver_name()
            rows = db.run_query("SELECT Driver_ID, Shift_Start_Time, Shift_End_Time FROM Drivers "
                                "WHERE First_Name = ? AND Last_Name = ? ORDER BY Driver_ID", (first, last))
        except (sqlite3.Error, ValueError) as err:
            error("Could not read driver", err)
            return
        if not rows:
            driver_id = None
            status.configure(text="No driver named " + first + " " + last)
            return
        driver_id = rows[0][0]
        set_entry(d_shift_start, rows[0][1])
        set_entry(d_shift_end, rows[0][2])
        status.configure(text="Driver " + str(driver_id) + " loaded")
    
    
    def driver_update():
        if driver_id is None:
            return need_read("driver")
        try:
            first, last = driver_name()
            upd.update_drivers(driver_id, first, last, blank_none(d_shift_start), blank_none(d_shift_end))
            status.configure(text="Driver " + str(driver_id) + " updated")
        except (sqlite3.Error, ValueError) as err:
            error("Could not update driver", err)
    
    
    def driver_delete():
        nonlocal driver_id
        if driver_id is None:
            return need_read("driver")
        if db.run_query("SELECT 1 FROM Trips WHERE Driver_ID = ?", (driver_id,)):
            return error("Could not delete driver", "Trips still use this driver.")
        if not messagebox.askyesno("Confirm delete", "Delete driver " + str(driver_id) + "?", parent=root):
            return
        try:
            dele.delete_drivers(driver_id)
            status.configure(text="Driver " + str(driver_id) + " deleted")
            driver_id = None
            for field in (d_first, d_last, d_shift_start, d_shift_end):
                field.delete(0, "end")
        except sqlite3.Error as err:
            error("Could not delete driver", err)
    
    
    # ---------------- GPS Record ----------------
    gps_frame = Frame(root, padding=10)
    g_vehicle = add_field(gps_frame, 0, "Vehicle #:", Combobox(gps_frame, state="readonly", width=28))
    g_time = add_field(gps_frame, 1, "Time Stamp (HH:MM):", Entry(gps_frame, width=30))
    g_lat = add_field(gps_frame, 2, "Latitude:", Entry(gps_frame, width=30))
    g_lon = add_field(gps_frame, 3, "Longitude:", Entry(gps_frame, width=30))
    gps_id = None
    
    
    def gps_show():
        g_vehicle["values"] = vehicle_ids()
    
    
    def gps_fields():
        time, lat, lon = g_time.get().strip(), g_lat.get().strip(), g_lon.get().strip()
        if not time or not lat or not lon:
            raise ValueError("Please enter the time stamp, latitude and longitude")
        return picked_id(g_vehicle, "vehicle"), time, float(lat), float(lon)
    
    
    def gps_create():
        nonlocal gps_id
        try:
            gps_id = ins.insert_gps_records(None, *gps_fields())
            status.configure(text="GPS record " + str(gps_id) + " created")
        except (sqlite3.Error, ValueError) as err:
            error("Could not create GPS record", err)
    
    
    def gps_read():
        nonlocal gps_id
        try:
            sql = "SELECT GPS_Record_ID, TimeStamp, Latitude, Longitude FROM GPS_Records WHERE Vehicle_ID = ?"
            params = (picked_id(g_vehicle, "vehicle"),)
            if g_time.get().strip():
                sql += " AND TimeStamp = ?"
                params += (g_time.get().strip(),)
            rows = db.run_query(sql + " ORDER BY TimeStamp DESC", params)
        except (sqlite3.Error, ValueError) as err:
            error("Could not read GPS record", err)
            return
        if not rows:
            gps_id = None
            status.configure(text="No GPS record found")
            return
        gps_id, time, lat, lon = rows[0]
        set_entry(g_time, time)
        set_entry(g_lat, lat)
        set_entry(g_lon, lon)
        text = "GPS record " + str(gps_id) + " loaded"
        if len(rows) > 1:
            text += ". " + str(len(rows)) + " records match, showing the newest"
        status.configure(text=text)
    
    
    def gps_update():
        if gps_id is None:
            return need_read("GPS record")
        try:
            upd.update_gps_records(gps_id, *gps_fields())
            status.configure(text="GPS record " + str(gps_id) + " updated")
        except (sqlite3.Error, ValueError) as err:
            error("Could not update GPS record", err)
    
    
    def gps_delete():
        nonlocal gps_id
        if gps_id is None:
            return need_read("GPS record")
        if not messagebox.askyesno("Confirm delete", "Delete GPS record " + str(gps_id) + "?", parent=root):
            return
        try:
            dele.delete_gps_records(gps_id)
            status.configure(text="GPS record " + str(gps_id) + " deleted")
            gps_id = None
            for field in (g_time, g_lat, g_lon):
                field.delete(0, "end")
        except sqlite3.Error as err:
            error("Could not delete GPS record", err)
    
    
    # ---------------- Switching and buttons ----------------
    PAGES = {
        "Ticket": (ticket_frame, ticket_show, ticket_create, ticket_read, ticket_update, ticket_delete),
        "Route": (route_frame, route_show, route_create, route_read, route_update, route_delete),
        "Stop": (stop_frame, stop_show, stop_create, stop_read, stop_update, stop_delete),
        "Trip": (trip_frame, trip_show, trip_create, trip_read, trip_update, trip_delete),
        "Vehicle": (vehicle_frame, vehicle_show, vehicle_create, vehicle_read, vehicle_update, vehicle_delete),
        "Driver": (driver_frame, driver_show, driver_create, driver_read, driver_update, driver_delete),
        "GPS Record": (gps_frame, gps_show, gps_create, gps_read, gps_update, gps_delete),
    }
    
    
    def show_page(event=None):
        for page in PAGES.values():
            page[0].pack_forget()
        page = PAGES[choice.get()]
        page[0].pack(fill="x")
        page[1]()
        status.configure(text="")
    
    
    def press(index):
        PAGES[choice.get()][index]()
    
    
    Button(buttons, text="Create", command=lambda: press(2)).grid(row=0, column=0, padx=3, sticky="ew")
    Button(buttons, text="Read", command=lambda: press(3)).grid(row=0, column=1, padx=3, sticky="ew")
    Button(buttons, text="Update", command=lambda: press(4)).grid(row=0, column=2, padx=3, sticky="ew")
    Button(buttons, text="Delete", command=lambda: press(5)).grid(row=0, column=3, padx=3, sticky="ew")
    for column in range(4):
        buttons.columnconfigure(column, weight=1)
    
    choice.bind("<<ComboboxSelected>>", show_page)
    choice.current(0)
    show_page()
    root.mainloop()
