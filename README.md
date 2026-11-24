# Public Transportation Management Database

## Run the application

From the project directory, run:

```powershell
python .\login.py
```

Log in with `admin` / `password` to open the main menu.

- **Head to search** opens the bus lookup. Search by ticket number, passenger name, route number or stop name.
- **Head to manage database** opens the manage page. Pick what to change (Ticket, Route, Stop, Trip, Vehicle, Driver or GPS Record), fill in the fields, and use Create, Read, Update or Delete. IDs are assigned automatically. Read loads a record so Update and Delete can act on it.

All files use `public_transportation.db` in the project folder, wherever the app is started from.
