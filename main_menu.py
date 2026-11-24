import tkinter as tk
import transit_gui


def main_menu_gui():

    root = tk.Tk()
    root.title("Public Transportation System")
    root.geometry("800x600")

    frame = tk.Frame(root)
    frame.pack(pady=10)

    tk.Label(frame, text = "Welcome to the City Public Transportaion", font = ("Arial", 16, "bold")).grid(row=60, column=5)

    button = tk.Frame(root)
    button.pack(pady=10)

    menu_button = tk.Button(button, text="Head to search", command=lambda: transit_gui.open_search(root))
    menu_button.grid(row=0, column=0, padx=5, pady=5)

   
    root.mainloop()

if __name__ == "__main__":
    main_menu_gui()