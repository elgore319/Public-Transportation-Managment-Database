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
    root.geometry("360x520")
    
    top = Frame(root, padding=10)
    top.pack(fill="x")
    Label(top, text="Change:", font=("Arial", 12)).grid(row=0, column=0, sticky="w")
    choice = Combobox(top, values=["Ticket", "Route", "Stop"], state="readonly", width=28)
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
    
    
    # ---------------- Switching and buttons ----------------
    PAGES = {
        "Ticket": (ticket_frame, ticket_show, ticket_create, ticket_read, ticket_update, ticket_delete),
        "Route": (route_frame, route_show, route_create, route_read, route_update, route_delete),
        "Stop": (stop_frame, stop_show, stop_create, stop_read, stop_update, stop_delete),
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
