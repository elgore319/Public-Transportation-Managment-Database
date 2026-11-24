# Public Transportation Management Database

## Run the application

From the project directory, run:

```powershell
python .\transit_gui.py
```

The **Search** tab looks up tickets, passengers, routes, and stops. The **Manage Data** tab lets you select a database table, add records, update a selected record, and delete a selected record. Leave an integer primary-key field blank when adding a record to let SQLite assign it automatically. Deleting a record requires confirmation, and database constraint errors are shown in a dialog.
