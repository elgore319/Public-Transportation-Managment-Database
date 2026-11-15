import tkinter
from tkinter.ttk import *
import db_functions as db

root = tkinter.Tk()
root.title("Bus Schedule Lookup")

title = Label(root, text="Find Your Bus", font=("Arial", 16))
title.grid(row=0, column=0, columnspan=4, pady=10)

label = Label(root, text="Search by: ")
label.grid(row=1, column=0)
search_by = Combobox(root, values=list(db.SEARCHES.keys()), state="readonly", width=15)
search_by.current(0)
search_by.grid(row=1, column=1)

entry = Entry(root, width=20)
entry.grid(row=1, column=2)

# Results table
results = Treeview(root, height=14, show="headings")
results.grid(row=2, column=0, columnspan=4, padx=10, pady=10)

lbl = Label(root)
lbl.grid(row=3, column=0, columnspan=4, pady=5)


def search(event=None):
    query = entry.get().strip()
    if not query:
        lbl.configure(text="Please enter something to search for")
        return
    headings, rows = db.SEARCHES[search_by.get()](query)

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


button1 = Button(root, text="Search", command=search)
button1.grid(row=1, column=3)
entry.bind("<Return>", search)
entry.focus()

root.mainloop()
