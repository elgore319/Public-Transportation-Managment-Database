import tkinter
from testnum import buses
from tkinter.ttk import *
root = tkinter.Tk()
root.title("Bus Search")
root.geometry ("350x250")
label = Label(root, text= "Enter Bus Number: ")
label.grid(row= 1 , column=0)
entry = Entry(root,width= 20)
entry.grid(row= 1 , column=1)
lbl = Label(root)
lbl.grid(row=3, column=1)
def search(event=None):
    query = entry.get().strip()
    if not query:
        lbl.configure(text="Please enter a bus number")
        return
    matches = [bus for bus in buses if query in str(bus)]
    if matches:
        lbl.configure(text="Found: " + ", ".join("Bus " + str(bus) for bus in matches))
    else:
        lbl.configure(text="No bus found for " + query)
button1 = Button(root,text="Search",command=search)
button1.grid(row= 2 , column=1)
entry.bind("<Return>", search)
root.mainloop()
