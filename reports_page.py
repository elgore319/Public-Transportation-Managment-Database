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
}


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

    results = Treeview(frame, height=14, show="headings")
    results.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

    lbl = Label(frame)
    lbl.grid(row=3, column=0, columnspan=3, pady=5)

    frame.columnconfigure(1, weight=1)
    frame.rowconfigure(2, weight=1)

    def run(event=None):
        headings, sql = REPORTS[report.get()]
        try:
            rows = db.run_query(sql)
        except sqlite3.Error as error:
            messagebox.showerror("Report failed", str(error), parent=root)
            return
        results.delete(*results.get_children())
        results["columns"] = headings
        for h in headings:
            results.heading(h, text=h)
            results.column(h, width=100)
        for row in rows:
            results.insert("", "end", values=["" if v is None else v for v in row])
        lbl.configure(text=str(len(rows)) + " row(s)" if rows else "No data for this report yet")

    Button(frame, text="Run", command=run).grid(row=1, column=2)
    report.bind("<<ComboboxSelected>>", run)
    run()

    if parent is None:
        root.mainloop()
    return root


if __name__ == "__main__":
    open_reports()
