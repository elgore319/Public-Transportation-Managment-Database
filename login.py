import tkinter as tk
import main_menu
from tkinter import messagebox

# Function to validate the login
def validate_login():
    userid = username_entry.get()
    password = password_entry.get()

    if userid == "admin" and password == "password":
        main_menu.main_menu_gui()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")


# Create the main window
root = tk.Tk() 
root.title("Login Form")

# Create and place the username label and entry
username_label = tk.Label(root, text="Userid:")
username_label.pack()

username_entry = tk.Entry(root)
username_entry.pack()


# Create and place the password label and entry
password_label = tk.Label(root, text="Password:")
password_label.pack()

password_entry = tk.Entry(root, show="*")
password_entry.pack()

# Create and place the login button
login_button = tk.Button(root, text = "Login", command = validate_login)
login_button.pack()

#Start the Tkinter event loop
root.mainloop()

