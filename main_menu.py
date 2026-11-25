import tkinter as tk
import transit_gui
import manage_page
import reports_page


def main_menu_gui(parent=None):

    root = tk.Toplevel(parent) if parent is not None else tk.Tk()
    root.title("Public Transportation System")
    root.geometry("800x600")

    frame = tk.Frame(root)
    frame.pack(pady=10)

    tk.Label(frame, text = "Welcome to the City Public Transportation", font = ("Arial", 16, "bold")).grid(row=60, column=5)

    button = tk.Frame(root)
    button.pack(pady=10)

    menu_button = tk.Button(button, text="Head to search", command=lambda: transit_gui.open_search(root))
    menu_button.grid(row=0, column=0, padx=5, pady=5)

    menu_button2 = tk.Button(button, text="Head to manage database", command=lambda: manage_page.open_manage(root))
    menu_button2.grid(row=1, column=0, padx=5, pady=5)

    menu_button3 = tk.Button(button, text="Head to reports", command=lambda: reports_page.open_reports(root))
    menu_button3.grid(row=2, column=0, padx=5, pady=5)
   
    if parent is None:
        root.mainloop()
    else:
        root.protocol("WM_DELETE_WINDOW", parent.destroy)

if __name__ == "__main__":
    main_menu_gui()