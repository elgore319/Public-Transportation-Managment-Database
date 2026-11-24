import tkinter
import sqlite3
from tkinter import messagebox
from tkinter.ttk import *
import db_functions as db

root = tkinter.Tk()
root.title("Bus Schedule Lookup")
root.geometry("900x600")

search_tab = Frame(root, padding=10)
search_tab.pack(fill="both", expand=True, padx=10, pady=10)

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

root.mainloop()
