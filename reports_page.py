import tkinter
import sqlite3
from tkinter import messagebox
from tkinter.ttk import *
import db_functions as db

MINUTES = "(strftime('%s', '2000-01-01 ' || {0}) - strftime('%s', '2000-01-01 ' || {1})) / 60"

REPORTS = {
    "Delayed Buses": (
        ["Trip", "Route", "Bus", "Driver", "Scheduled", "Actual", "Minutes Late"],
        """
        SELECT t.Trip_ID, t.Route_Number, t.Vehicle_ID, d.First_Name || ' ' || d.Last_Name,
               t.Start_Time, t.Actual_Start_Time, """ + MINUTES.format("t.Actual_Start_Time", "t.Start_Time") + """
        FROM Trips t
        LEFT JOIN Drivers d ON d.Driver_ID = t.Driver_ID
        WHERE t.Actual_Start_Time > t.Start_Time
        ORDER BY 7 DESC
        """,
    ),
    "Busiest Stops": (
        ["Stop", "Scheduled Arrivals", "Routes Served"],
        """
        SELECT s.Stop_Name, COUNT(sc.Schedule_ID), COUNT(DISTINCT sc.Route_Number)
        FROM Stops s
        JOIN Schedules sc ON sc.Stop_Number = s.Stop_Number
        WHERE s.Is_Active = 1
        GROUP BY s.Stop_Number
        ORDER BY 2 DESC, 3 DESC
        """,
    ),
    "Passenger Demand by Route": (
        ["Route", "Trips", "Tickets Sold", "Tickets per Trip"],
        """
        SELECT r.Route_Number,
               (SELECT COUNT(*) FROM Trips t WHERE t.Route_Number = r.Route_Number),
               COUNT(k.Ticket_ID),
               ROUND(COUNT(k.Ticket_ID) * 1.0 /
                     NULLIF((SELECT COUNT(*) FROM Trips t WHERE t.Route_Number = r.Route_Number), 0), 2)
        FROM Routes r
        LEFT JOIN Trips t ON t.Route_Number = r.Route_Number
        LEFT JOIN Tickets k ON k.Trip_ID = t.Trip_ID
        GROUP BY r.Route_Number
        ORDER BY 3 DESC
        """,
    ),
    "Vehicle Utilization": (
        ["Bus", "Capacity", "Trips", "Tickets", "Seats Filled %"],
        """
        SELECT v.Vehicle_ID, v.Capacity, COUNT(DISTINCT t.Trip_ID), COUNT(k.Ticket_ID),
               ROUND(COUNT(k.Ticket_ID) * 100.0 / NULLIF(COUNT(DISTINCT t.Trip_ID) * v.Capacity, 0), 1)
        FROM Vehicles v
        LEFT JOIN Trips t ON t.Vehicle_ID = v.Vehicle_ID
        LEFT JOIN Tickets k ON k.Trip_ID = t.Trip_ID
        GROUP BY v.Vehicle_ID
        ORDER BY 5 DESC
        """,
    ),
    "Shortest Route (fewest stops)": (
        ["Stops Travelled", "Path", "Routes Taken"],
        """
        WITH RECURSIVE
        route_stops AS (
            SELECT DISTINCT sc.Route_Number, sc.Stop_Order, sc.Stop_Number FROM Schedules sc
        ),
        legs AS (
            SELECT DISTINCT a.Route_Number, a.Stop_Number AS From_Stop, b.Stop_Number AS To_Stop
            FROM route_stops a
            JOIN route_stops b ON b.Route_Number = a.Route_Number AND b.Stop_Order = a.Stop_Order + 1
        ),
        paths (Stop_Number, Hops, Path, Names, Routes) AS (
            SELECT Stop_Number, 0, '/' || Stop_Number || '/', Stop_Name, ''
            FROM Stops WHERE Stop_Name = ?
            UNION ALL
            SELECT l.To_Stop, p.Hops + 1, p.Path || l.To_Stop || '/',
                   p.Names || ' > ' || (SELECT Stop_Name FROM Stops WHERE Stop_Number = l.To_Stop),
                   p.Routes || CASE WHEN p.Routes LIKE '%' || l.Route_Number THEN '' ELSE ' ' || l.Route_Number END
            FROM paths p
            JOIN legs l ON l.From_Stop = p.Stop_Number
            WHERE p.Path NOT LIKE '%/' || l.To_Stop || '/%' AND p.Hops < 10
        )
        SELECT p.Hops, p.Names, TRIM(p.Routes)
        FROM paths p
        JOIN Stops s ON s.Stop_Number = p.Stop_Number
        WHERE s.Stop_Name = ? AND p.Hops > 0
        ORDER BY p.Hops
        LIMIT 1
        """,
    ),
    "Fastest Trip (direct)": (
        ["Route", "Departs", "Arrives", "Minutes"],
        """
        SELECT o.Route_Number, o.Schedule_Arrival_Time, MIN(d.Schedule_Arrival_Time),
               """ + MINUTES.format("MIN(d.Schedule_Arrival_Time)", "o.Schedule_Arrival_Time") + """
        FROM Schedules o
        JOIN Schedules d ON d.Route_Number = o.Route_Number
                        AND d.Stop_Order > o.Stop_Order
                        AND d.Schedule_Arrival_Time > o.Schedule_Arrival_Time
        WHERE o.Stop_Number = (SELECT Stop_Number FROM Stops WHERE Stop_Name = ?)
          AND d.Stop_Number = (SELECT Stop_Number FROM Stops WHERE Stop_Name = ?)
        GROUP BY o.Schedule_ID
        ORDER BY 4, 2
        """,
    ),
}
NEEDS_STOPS = ("Shortest Route (fewest stops)", "Fastest Trip (direct)")


def open_reports(parent=None):
    root = tkinter.Toplevel(parent) if parent is not None else tkinter.Tk()
    root.title("Reports")
    root.geometry("800x500")

    frame = Frame(root, padding=10)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    Label(frame, text="Reports", font=("Arial", 16)).grid(row=0, column=0, columnspan=3, pady=10)

    Label(frame, text="Report: ").grid(row=1, column=0)
    report = Combobox(frame, values=list(REPORTS), state="readonly", width=30)
    report.current(0)
    report.grid(row=1, column=1)

    stop_names = [row[0] for row in db.run_query("SELECT Stop_Name FROM Stops ORDER BY Stop_Name")]
    stops = Frame(frame)
    stops.grid(row=2, column=0, columnspan=3, pady=5)
    Label(stops, text="From: ").grid(row=0, column=0)
    from_stop = Combobox(stops, values=stop_names, state="readonly", width=25)
    from_stop.grid(row=0, column=1, padx=(0, 15))
    Label(stops, text="To: ").grid(row=0, column=2)
    to_stop = Combobox(stops, values=stop_names, state="readonly", width=25)
    to_stop.grid(row=0, column=3)

    results = Treeview(frame, height=14, show="headings")
    results.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

    lbl = Label(frame)
    lbl.grid(row=4, column=0, columnspan=3, pady=5)

    frame.columnconfigure(1, weight=1)
    frame.rowconfigure(3, weight=1)

    def run(event=None):
        if report.get() in NEEDS_STOPS:
            names = [row[0] for row in db.run_query("SELECT Stop_Name FROM Stops ORDER BY Stop_Name")]
            from_stop["values"] = names
            to_stop["values"] = names
            stops.grid()
        else:
            stops.grid_remove()
        headings, sql = REPORTS[report.get()]
        params = ()
        if report.get() in NEEDS_STOPS:
            if not from_stop.get() or not to_stop.get():
                lbl.configure(text="Choose a From and To stop for this report")
                return
            params = (from_stop.get(), to_stop.get())
        try:
            rows = db.run_query(sql, params)
        except sqlite3.Error as error:
            messagebox.showerror("Report failed", str(error), parent=root)
            return
        results.delete(*results.get_children())
        results["columns"] = headings
        for h in headings:
            results.heading(h, text=h)
            results.column(h, width=450 if h == "Path" else 100)
        for row in rows:
            results.insert("", "end", values=["" if v is None else v for v in row])
        lbl.configure(text=str(len(rows)) + " row(s)" if rows else "No results")

    Button(frame, text="Refresh", command=run).grid(row=1, column=2)
    report.bind("<<ComboboxSelected>>", run)
    from_stop.bind("<<ComboboxSelected>>", run)
    to_stop.bind("<<ComboboxSelected>>", run)
    run()

    if parent is None:
        root.mainloop()
    return root


if __name__ == "__main__":
    open_reports()
