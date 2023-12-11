# main.py
import tkinter as tk
from controller import SearchController
from view import SearchView
from model import PUBLIC_KEY, PRIVATE_KEY

if __name__ == "__main__":
    # Create instances
    root = tk.Tk()
    controller = SearchController(PUBLIC_KEY, PRIVATE_KEY)

    version = "0.1.0"  # Set version number
    app = SearchView(root, controller, version)

    root.mainloop()
