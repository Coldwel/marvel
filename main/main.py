# main.py
import json
import tkinter as tk
from controller import SearchController
from view import SearchView
from model import PUBLIC_KEY, PRIVATE_KEY

SOFTWARE_VERSION = "0.1.2"

with open("config.json") as f:
    config = json.load(f)
    window_size = config.get("window_size")

if __name__ == "__main__":
    # Create instances
    root = tk.Tk()
    controller = SearchController(PUBLIC_KEY, PRIVATE_KEY)
    version = SOFTWARE_VERSION  # Set version number
    app = SearchView(root, controller, version)
    root.geometry(window_size)
    root.mainloop()
