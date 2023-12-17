# view.py
import tkinter as tk
import requests
import io
from PIL import Image, ImageTk
from cache import cache
from model import PUBLIC_KEY, PRIVATE_KEY, MarvelAPI
import asyncio
import aiohttp
import time

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
VERSION_FONT = ("Helvetica Neu", 10, "bold")
SMALL_FONT = ("Helvetica Neu", 10)


class SearchView:
    def __init__(self, root, controller, version):
        self.root = root
        self.controller = controller
        self.root.configure(bg=BG_COLOR)
        self.root.title("Marvel Comic Search")

        self.marvel_api = MarvelAPI(PUBLIC_KEY, PRIVATE_KEY)

        self.version = version  # pass the version number to SearchView

        # GUI setup
        self.version_label = tk.Label(self.root, text=f"v{self.version}", bg=BG_COLOR, fg="black",
                                      font=VERSION_FONT)
        self.version_label.pack(side=tk.BOTTOM, pady=10)

        self.query_entry = None
        self.search_frame = None
        # Call the method to display the static image
        self.display_static_image()
        self.setup_search_frame()

        # Bind the Enter key to initiate the search
        self.root.bind("<Return>", lambda event: self.search_api())

        self.results_frame = None
        self.results_canvas = None

        self.results_frame = tk.Frame(self.root)
        self.comics_frame = tk.Frame(self.root)
        self.comics_frame.pack_forget()

    def display_static_image(self):
        # Create a frame for the Marvel logo section
        marvel_logo_frame = tk.Frame(self.root, bg=BG_COLOR)
        # Set expand to True to fill available space
        marvel_logo_frame.pack(expand=True, pady=40, anchor="n")

        # Display static image information (Marvel logo in this case)
        image_path = "marvel-logo.png"
        image_data = Image.open(image_path)
        image_data.thumbnail((350, 350))
        img = ImageTk.PhotoImage(image_data)

        # Center the image in the middle of the window
        marvel_logo = tk.Label(marvel_logo_frame, image=img, bg=BG_COLOR)
        marvel_logo.image = img
        marvel_logo.pack(side=tk.TOP, pady=(self.root.winfo_height() - 0) // 2)

    def setup_search_frame(self):
        # Create a frame for the search-related elements
        self.search_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.search_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Query label
        query_label = tk.Label(self.search_frame, text="Search Character:", bg=BG_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
        query_label.pack(side=tk.LEFT, padx=(10, 10))

        # Query entry
        self.query_entry = tk.Entry(self.search_frame, width=20, bg=SECONDARY_COLOR, fg=PRIMARY_COLOR, font=LABEL_FONT)
        self.query_entry.pack(side=tk.LEFT)

        # Give focus to query_entry
        self.query_entry.focus_set()

        # Search button
        search_button = tk.Button(self.search_frame, text="Search", bg=ACCENT_COLOR, fg=SECONDARY_COLOR,
                                  font=BUTTON_FONT, command=self.search_api)
        search_button.pack(side=tk.LEFT, padx=(10, 10))

    def search_api(self):
        if hasattr(self, 'query_entry') and self.query_entry is not None:
            query = self.query_entry.get()
            if query:
                print("Query is not empty")
                results = self.controller.search(query)
                self.show_results(results)
            else:
                print("Query is empty")
        else:
            print("query_entry is None")

    def on_mousewheel(self, event):
        # Handle mousewheel event
        self.results_canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def show_results(self, results):
        if self.results_frame:
            self.results_frame.destroy()

        self.results_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.results_frame.pack(fill=tk.BOTH, expand=True)

        self.search_frame.place(relx=0.5, rely=0.4, anchor="center")

        if len(results) > 0:
            self.results_canvas = tk.Canvas(self.results_frame, bg=BG_COLOR, bd=0, highlightthickness=0)
            self.results_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            scrollbar = tk.Scrollbar(self.results_frame, orient=tk.VERTICAL, command=self.results_canvas.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            self.results_canvas.configure(yscrollcommand=scrollbar.set)

            hero_list_frame = tk.Frame(self.results_canvas, bg=BG_COLOR)
            hero_list_frame.bind("<Configure>", lambda e: self.results_canvas.configure(scrollregion=self.results_canvas.bbox("all")))
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
                                     font=LABEL_FONT, wraplength=450)
                hero_desc.pack(pady=5, anchor="w")

                comics_button = tk.Button(hero_info_frame, text="Comics", bg=ACCENT_COLOR, fg=SECONDARY_COLOR,
                                          font=BUTTON_FONT,
                                          command=lambda url=result["comics_url"]: self.retrieve_and_display_comics(url))
                comics_button.pack(pady=5, anchor="w")

                # Bind mouse wheel event to the canvas
                self.results_canvas.bind_all("<MouseWheel>", self.on_mousewheel)

                # Set a fixed size for the results window
                self.root.geometry("800x600")

    async def fetch_comics_data(self, comics_url, timestamp, md5_hash):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        params = {
            "ts": timestamp,
            "apikey": PUBLIC_KEY,
            "hash": md5_hash,
            "format": "comic",
            "formatType": "comic",
            "noVariants": "True",
            "limit": 25,
            "orderBy": "-focDate"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(comics_url, headers=headers, params=params) as response:
                data = await response.json()

        return data

    def retrieve_and_display_comics(self, comics_url):
        if comics_url in cache:
            comics_list = cache[comics_url]
            self.display_comics_list(comics_list)
        else:
            timestamp = "1"
            md5_hash = self.controller.generate_hash(timestamp)

            loop = asyncio.get_event_loop()
            data = loop.run_until_complete(self.fetch_comics_data(comics_url, timestamp, md5_hash))

            comics_list = []
            if data["data"]["total"] > 0:
                for result in data["data"]["results"]:
                    comic_item = {
                        "title": result["title"],
                        "thumbnail_url": result["thumbnail"]["path"] + "/portrait_uncanny." + result["thumbnail"]["extension"],
                        "description": result["description"]
                    }
                    comics_list.append(comic_item)

                cache[comics_url] = comics_list  # Cache the comics list

                self.display_comics_list(comics_list)
            else:
                self.show_error("No comics found.")

    def display_comics_list(self, comics_list):
        # Testing methods runtime
        start = time.time()
        # create a new window to show the comics list
        comics_window = tk.Toplevel(self.root)
        comics_window.title("Comics List")
        comics_window.configure(bg=BG_COLOR, pady=5)
        comics_window.geometry('800x600')

        # create a Canvas widget to show the comics list with custom scrolling
        comics_canvas = tk.Canvas(comics_window, bg=BG_COLOR, highlightthickness=0)
        comics_canvas.pack(fill=tk.BOTH, expand=True)

        # create a Frame to contain the comics content
        comics_frame = tk.Frame(comics_canvas, bg=BG_COLOR)
        comics_canvas.create_window((0, 0), window=comics_frame, anchor=tk.NW)

        # Initialize counter for row index
        row_index = 0
        # Display the comics list in the Frame
        for comic_item in comics_list:
            # Fetch the thumbnail URL from the comic information
            thumbnail_url = comic_item.get("thumbnail_url", "")

            if thumbnail_url:
                # Fetch the thumbnail image
                image_bytes = requests.get(thumbnail_url).content
                image_data = io.BytesIO(image_bytes)
                img = Image.open(image_data)
                img = img.resize((100, 150))  # Adjust the size as needed
                img = ImageTk.PhotoImage(img)

                # Display the thumbnail image within the Canvas
                thumbnail_label = tk.Label(comics_frame, image=img, bg=BG_COLOR)
                thumbnail_label.image = img
                thumbnail_label.grid(row=row_index, column=0, padx=5, pady=5, sticky=tk.W)

            # Display the comic title
            title_label = tk.Label(comics_frame, text=comic_item['title'], bg=BG_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
            title_label.grid(row=row_index, column=1, padx=5, pady=5, sticky=tk.W)
            # Display the comic description
            des_label = tk.Label(comics_frame, text=comic_item['description'], bg=BG_COLOR, fg=TEXT_COLOR,
                                 font=SMALL_FONT, wraplength=500)
            des_label.grid(row=row_index + 1, column=1, padx=5, pady=5, sticky=tk.W)

            row_index += 2

        comics_canvas.update_idletasks()  # Update to calculate the canvas size
        comics_canvas.config(scrollregion=comics_canvas.bbox('all'))  # Set the initial scroll region

        # Add a vertical scrollbar for the Canvas
        scrollbar = tk.Scrollbar(comics_canvas, orient=tk.VERTICAL, command=comics_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        comics_canvas.config(yscrollcommand=scrollbar.set)

        # Bind the Canvas to the scrollbar
        comics_canvas.bind('<Configure>', lambda e: comics_canvas.configure(scrollregion=comics_canvas.bbox('all')))
        comics_canvas.create_window((0, 0), window=comics_frame, anchor=tk.NW)

        # Configure the Canvas scrolling with the mouse wheel
        comics_canvas.bind_all('<MouseWheel>', lambda e: comics_canvas.yview_scroll(-1 * int(e.delta / 120), 'units'))

        comics_canvas.yview_moveto(0.0)  # Ensure the scroll bar is at the top

        # end test
        end = time.time()
        round_time = round(end - start)
        print(f"Runtime of the method is {round_time} seconds.")

        comics_window.mainloop()

    def show_error(self, message):
        error_window = tk.Toplevel(self.root)
        error_window.title("Error")
        error_window.configure(bg=BG_COLOR)

        error_label = tk.Label(error_window, text=message, bg=BG_COLOR, fg="#fcbd19", font=LABEL_FONT)
        error_label.pack(pady=20)
