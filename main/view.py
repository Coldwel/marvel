# view.py
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import requests
import io
from PIL import Image, ImageTk
from cache import cache

# Define custom colors
PRIMARY_COLOR = "#ed1d24"
SECONDARY_COLOR = "#ffffff"
BG_COLOR = "#0072c6"
TEXT_COLOR = "#fcbd19"
ACCENT_COLOR = "#ed1d24"

# Define custom font styles
HEADER_FONT = ("Helvetica Neu", 18, "bold")
LABEL_FONT = ("Helvetica Neu", 14)
BUTTON_FONT = ("Helvetica Neu", 12, "bold")


class SearchView:
    def __init__(self, root, controller, version):
        self.root = root
        self.controller = controller
        self.root.configure(bg=BG_COLOR)
        self.root.title("Marvel Comic Search")
        # Set the initial size of the main window
        root.geometry("800x600")

        self.version = version  # pass the version number to SearchView

        # GUI setup
        self.search_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.search_frame.pack(pady=10)

        self.query_label = tk.Label(self.search_frame, text="Search Character:", bg=BG_COLOR, fg=TEXT_COLOR,
                                    font=LABEL_FONT)
        self.query_label.pack(side=tk.LEFT, padx=(10, 10))

        self.query_entry = tk.Entry(self.search_frame, width=20, bg=SECONDARY_COLOR, fg=PRIMARY_COLOR, font=LABEL_FONT)
        self.query_entry.pack(side=tk.LEFT)

        self.search_button = tk.Button(self.search_frame, text="Search", bg=ACCENT_COLOR, fg=SECONDARY_COLOR,
                                       font=BUTTON_FONT, command=self.search_api)
        self.search_button.pack(side=tk.LEFT, padx=(10, 10))

        self.results_frame = tk.Frame(self.root)
        self.comics_frame = tk.Frame(self.root)
        self.comics_frame.pack_forget()

        self.query_entry.bind("<Return>", lambda event: self.search_api())

        self.version_label = tk.Label(self.root, text=f"Version: {self.version}", bg = BG_COLOR, fg="black",
                                      font=LABEL_FONT)
        self.version_label.pack(side=tk.BOTTOM, pady=10)

    def search_api(self):
        query = self.query_entry.get()
        if query:
            results = self.controller.search(query)
            self.show_results(results)

    def on_mousewheel(self, event):
        # Handle mousewheel event
        self.results_canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def show_results(self, results):
        self.results_frame.pack(fill=tk.BOTH, expand=True)

        for widget in self.results_frame.winfo_children():
            widget.destroy()

        if len(results) > 0:
            self.results_canvas = tk.Canvas(self.results_frame, bg=BG_COLOR, bd=0, highlightthickness=0, height=400,
                                            width=600)
            self.results_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            scrollbar = tk.Scrollbar(self.results_frame, orient=tk.VERTICAL, command=self.results_canvas.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            self.results_canvas.configure(yscrollcommand=scrollbar.set)

            hero_list_frame = tk.Frame(self.results_canvas, bg=BG_COLOR)
            hero_list_frame.bind("<Configure>",
                                 lambda e: self.results_canvas.configure(scrollregion=self.results_canvas.bbox("all")))
            self.results_canvas.create_window((0, 0), window=hero_list_frame, anchor="nw")

            for result in results:
                hero_frame = tk.Frame(hero_list_frame, bg=BG_COLOR, pady=10)
                hero_frame.pack(fill=tk.X, padx=20)

                image_bytes = requests.get(result["image_url"]).content
                image_data = io.BytesIO(image_bytes)
                img = Image.open(image_data)
                img = img.resize((200, 200))
                img = ImageTk.PhotoImage(img)

                hero_image = tk.Label(hero_frame, image=img, bg=BG_COLOR)
                hero_image.image = img
                hero_image.pack(side=tk.LEFT, padx=10)

                hero_info_frame = tk.Frame(hero_frame, bg=BG_COLOR)
                hero_info_frame.pack(side=tk.LEFT)

                hero_name = tk.Label(hero_info_frame, text=result["name"], bg=BG_COLOR, fg=TEXT_COLOR,
                                     font=LABEL_FONT, wraplength=300)
                hero_name.pack(pady=5, anchor="w")

                hero_desc = tk.Label(hero_info_frame, text=result["description"], bg=BG_COLOR, fg=TEXT_COLOR,
                                     font=LABEL_FONT, wraplength=300)
                hero_desc.pack(pady=5, anchor="w")

                comics_button = tk.Button(hero_info_frame, text="Comics", bg=ACCENT_COLOR, fg=SECONDARY_COLOR,
                                          font=BUTTON_FONT,
                                          command=lambda url=result["comics_url"]: self.show_comics_window(url))
                comics_button.pack(pady=5, anchor="w")

            self.results_canvas.bind("<MouseWheel>", self.on_mousewheel)

    def show_comics_window(self, comics_url):
        if comics_url in cache:
            comics_list = cache[comics_url]
            self.display_comics_list(comics_list)
        else:
            timestamp = "1"
            md5_hash = self.controller.marvel_api.generate_hash(timestamp)

            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            params = {
                "ts": timestamp,
                "apikey": self.controller.PUBLIC_KEY,
                "hash": md5_hash,
                "format": "comic",
                "formatType": "comic",
                "noVariants": True,
                "limit": 100,
                "orderBy": "-focDate"
            }
            response = requests.get(comics_url, headers=headers, params=params)
            data = response.json()

            comics_list = []
            if data["data"]["total"] > 0:
                for result in data["data"]["results"]:
                    comics_list.append(result["title"])

                cache[comics_url] = comics_list
                self.display_comics_list(comics_list)
            else:
                self.show_error("No comics found.")

    def display_comics_list(self, comics_list):
        message = "\n".join(comics_list)

        comics_window = tk.Toplevel(self.root)
        comics_window.title("Comics List")
        comics_window.configure(bg=BG_COLOR, pady=5)
        comics_window.geometry('800x600')

        comics_text = ScrolledText(comics_window, bg=BG_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
        comics_text.pack(fill=tk.BOTH, expand=True)
        comics_text.insert(tk.END, message)
        comics_text.configure(state="disabled")

    def show_error(self, message):
        error_window = tk.Toplevel(self.root)
        error_window.title("Error")
        error_window.configure(bg=BG_COLOR)

        error_label = tk.Label(error_window, text=message, bg=BG_COLOR, fg="#fcbd19", font=LABEL_FONT)
        error_label.pack(pady=20)
