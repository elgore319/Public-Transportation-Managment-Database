# Public Transportation Management Database

## Run the application

The repository's `public_transportation.db` already holds the sample data. To rebuild it from scratch, delete it and run `python .\Create_Tables.py` then `python .\Sample_Data.py`.

From the project directory, run:

```powershell
python .\login.py
```

Log in with `admin` / `password` to open the main menu.

- **Head to search** opens the bus lookup. Search by ticket number, passenger name, route number or stop name.
- **Head to reports** shows delayed buses, busiest stops, passenger demand by route and vehicle utilization, and finds the shortest route (fewest stops, transfers allowed) or fastest direct trip between two stops.
- **Head to manage database** opens the manage page. Pick what to change (Ticket, Route, Stop, Trip, Vehicle, Driver or GPS Record), fill in the fields, and use Create, Read, Update or Delete. IDs are assigned automatically. Read loads a record so Update and Delete can act on it.

All files use `public_transportation.db` in the project folder, wherever the app is started from.
