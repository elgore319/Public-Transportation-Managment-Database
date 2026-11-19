import tkinter
import sqlite3
from tkinter import messagebox
from tkinter.ttk import *
import db_functions as db

root = tkinter.Tk()
root.title("Bus Schedule Lookup")
root.geometry("900x600")

tabs = Notebook(root)
tabs.pack(fill="both", expand=True, padx=10, pady=10)

search_tab = Frame(tabs, padding=10)
tabs.add(search_tab, text="Search")

title = Label(search_tab, text="Find Your Bus", font=("Arial", 16))
title.grid(row=0, column=0, columnspan=4, pady=10)

label = Label(search_tab, text="Search by: ")
label.grid(row=1, column=0)
search_by = Combobox(search_tab, values=list(db.SEARCHES.keys()), state="readonly", width=15)
search_by.current(0)
search_by.grid(row=1, column=1)

entry = Entry(search_tab, width=20)
entry.grid(row=1, column=2)

results = Treeview(search_tab, height=14, show="headings")
results.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

lbl = Label(search_tab)
lbl.grid(row=3, column=0, columnspan=4, pady=5)

search_tab.columnconfigure(0, weight=1)
search_tab.rowconfigure(2, weight=1)


def search(event=None):
    search_entry = event.widget if event is not None else entry
    query = search_entry.get().strip()
    if not query:
        lbl.configure(text="Please enter something to search for")
        return
    try:
        headings, rows = db.SEARCHES[search_by.get()](query)
    except sqlite3.Error as error:
        messagebox.showerror("Search failed", str(error), parent=root)
        return

    # Clear the old results and set up the columns for this search
    results.delete(*results.get_children())
    results["columns"] = headings
    for h in headings:
        results.heading(h, text=h)
        results.column(h, width=100)
    for row in rows:
        results.insert("", "end", values=["" if v is None else v for v in row])

    if rows:
        lbl.configure(text="Found " + str(len(rows)) + " result(s)")
    else:
        lbl.configure(text="Nothing found for " + search_by.get() + " " + query)


button1 = Button(search_tab, text="Search", command=search)
button1.grid(row=1, column=3)
entry.bind("<Return>", search)
entry.focus()

manage_tab = Frame(tabs, padding=10)
tabs.add(manage_tab, text="Manage Data")

table_label = Label(manage_tab, text="Table:")
table_label.grid(row=0, column=0, sticky="w", padx=(0, 5), pady=5)
table_choice = Combobox(manage_tab, values=db.TABLES, state="readonly", width=20)
table_choice.grid(row=0, column=1, sticky="w", pady=5)

records_frame = Frame(manage_tab)
records_frame.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=5)
records = Treeview(records_frame, show="headings", height=12, selectmode="browse")
vertical_scrollbar = Scrollbar(records_frame, orient="vertical", command=records.yview)
horizontal_scrollbar = Scrollbar(records_frame, orient="horizontal", command=records.xview)
records.configure(
    yscrollcommand=vertical_scrollbar.set,
    xscrollcommand=horizontal_scrollbar.set,
)
records.grid(row=0, column=0, sticky="nsew")
vertical_scrollbar.grid(row=0, column=1, sticky="ns")
horizontal_scrollbar.grid(row=1, column=0, sticky="ew")
records_frame.columnconfigure(0, weight=1)
records_frame.rowconfigure(0, weight=1)

form = LabelFrame(manage_tab, text="Record fields", padding=8)
form.grid(row=2, column=0, columnspan=4, sticky="ew", pady=5)

form_entries = {}
table_schema = []
selected_key = None
manage_status = Label(manage_tab)
manage_status.grid(row=4, column=0, columnspan=4, sticky="w", pady=5)


def clear_form():
    global selected_key
    selected_key = None
    for field in form_entries.values():
        field.configure(state="normal")
        field.delete(0, "end")
    manage_status.configure(text="")


def show_table(event=None):
    global table_schema, form_entries
    table_name = event.widget.get() if event is not None else table_choice.get()
    if not table_name:
        return

    try:
        table_schema = db.get_table_schema(table_name)
        columns, rows = db.get_table_rows(table_name)
    except (sqlite3.Error, ValueError) as error:
        messagebox.showerror("Could not load table", str(error), parent=root)
        return

    records.delete(*records.get_children())
    records["columns"] = columns
    for column in columns:
        records.heading(column, text=column)
        records.column(column, width=130, stretch=False)
    for row in rows:
        records.insert("", "end", values=["" if value is None else value for value in row])

    for child in form.winfo_children():
        child.destroy()
    form_entries = {}
    for index, schema_column in enumerate(table_schema):
        column = schema_column[0]
        grid_row = index // 2
        grid_column = (index % 2) * 2
        Label(form, text=column + ":").grid(
            row=grid_row, column=grid_column, sticky="e", padx=(4, 6), pady=3
        )
        field = Entry(form, width=28)
        field.grid(row=grid_row, column=grid_column + 1, sticky="ew", padx=(0, 12), pady=3)
        form_entries[column] = field
    for column in range(4):
        form.columnconfigure(column, weight=1 if column % 2 else 0)
    manage_status.configure(text=str(len(rows)) + " record(s)")
    clear_form()


def load_selected_record(event):
    global selected_key
    selected = event.widget.selection()
    if not selected:
        return

    values = event.widget.item(selected[0], "values")
    primary_key = next((column for column in table_schema if column[2]), None)
    if primary_key is None:
        return

    key_index = [column[0] for column in table_schema].index(primary_key[0])
    selected_key = values[key_index]
    for index, schema_column in enumerate(table_schema):
        column = schema_column[0]
        field = form_entries[column]
        field.configure(state="normal")
        field.delete(0, "end")
        field.insert(0, values[index])
        if schema_column[2]:
            field.configure(state="readonly")


def get_form_values(include_primary_key):
    values = {}
    for column, declared_type, is_primary_key in table_schema:
        if is_primary_key and not include_primary_key:
            continue

        raw_value = form_entries[column].get().strip()
        if not raw_value:
            if is_primary_key:
                continue
            values[column] = None
        elif "INT" in declared_type.upper():
            values[column] = int(raw_value)
        elif any(kind in declared_type.upper() for kind in ("REAL", "FLOAT", "DOUBLE")):
            values[column] = float(raw_value)
        else:
            values[column] = raw_value
    return values


def add_record():
    try:
        new_id = db.insert_record(table_choice.get(), get_form_values(True))
        show_table()
        manage_status.configure(text="Record added (ID " + str(new_id) + ")")
    except (sqlite3.Error, ValueError) as error:
        messagebox.showerror("Could not add record", str(error), parent=root)


def update_record():
    if selected_key is None:
        messagebox.showinfo("Select a record", "Select a record to update.", parent=root)
        return

    primary_key = next((column[0] for column in table_schema if column[2]), None)
    if primary_key is None:
        messagebox.showerror("Could not update record", "The table has no primary key.", parent=root)
        return
    try:
        updated = db.update_record(
            table_choice.get(), primary_key, selected_key, get_form_values(False)
        )
        show_table()
        manage_status.configure(text="Record updated" if updated else "No matching record to update")
    except (sqlite3.Error, ValueError) as error:
        messagebox.showerror("Could not update record", str(error), parent=root)


def delete_selected_record():
    if selected_key is None:
        messagebox.showinfo("Select a record", "Select a record to delete.", parent=root)
        return
    if not messagebox.askyesno(
        "Confirm delete", "Delete the selected record?", parent=root
    ):
        return

    primary_key = next((column[0] for column in table_schema if column[2]), None)
    if primary_key is None:
        messagebox.showerror("Could not delete record", "The table has no primary key.", parent=root)
        return
    try:
        deleted = db.delete_record(table_choice.get(), primary_key, selected_key)
        show_table()
        manage_status.configure(text="Record deleted" if deleted else "No matching record to delete")
    except (sqlite3.Error, ValueError) as error:
        messagebox.showerror("Could not delete record", str(error), parent=root)


def clear_selected_form():
    records.selection_remove(*records.selection())
    clear_form()


records.bind("<<TreeviewSelect>>", load_selected_record)
table_choice.bind("<<ComboboxSelected>>", show_table)
table_choice.current(0)
Button(manage_tab, text="Add", command=add_record).grid(row=3, column=0, sticky="w", pady=5)
Button(manage_tab, text="Update selected", command=update_record).grid(
    row=3, column=1, sticky="w", pady=5
)
Button(manage_tab, text="Delete selected", command=delete_selected_record).grid(
    row=3, column=2, sticky="w", pady=5
)
Button(manage_tab, text="Clear", command=clear_selected_form).grid(
    row=3, column=3, sticky="w", pady=5
)
manage_tab.columnconfigure(0, weight=1)
manage_tab.rowconfigure(1, weight=1)
show_table()

root.mainloop()
