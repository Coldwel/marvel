import tkinter as tk
from tkinter import messagebox
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
        self.favorite_window = None
        self.logged_in_user = None

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

        self.current_page = 1
        self.current_comic_page = 1
        self.total_comic_pages = 0
        self.comics_list = []

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
        query_label.grid(row=0, column=0, padx=(10, 10), sticky=tk.W)

        # Query entry
        self.query_entry = tk.Entry(self.search_frame, width=20, bg=SECONDARY_COLOR, fg=PRIMARY_COLOR, font=LABEL_FONT)
        self.query_entry.grid(row=0, column=1, padx=(0, 10))

        # Give focus to query_entry
        self.query_entry.focus_set()

        # Search button
        search_button = tk.Button(self.search_frame, text="Search", bg=ACCENT_COLOR, fg=SECONDARY_COLOR,
                                  font=BUTTON_FONT, command=self.search_api)
        search_button.grid(row=0, column=2, padx=(0, 10))

        # Username label
        self.username_label = tk.Label(self.search_frame, text="Username:", bg=BG_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
        self.username_label.grid(row=3, column=0, padx=(10, 10), pady=(20, 0), sticky=tk.W)

        # Username entry
        self.username_entry = tk.Entry(self.search_frame, width=20, bg=SECONDARY_COLOR, fg=PRIMARY_COLOR, font=LABEL_FONT)
        self.username_entry.grid(row=3, column=1, padx=(0, 10), pady=(20, 0))

        # Password label
        self.password_label = tk.Label(self.search_frame, text="Password:", bg=BG_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
        self.password_label.grid(row=4, column=0, padx=(10, 10), pady=(5, 0), sticky=tk.W)

        # Password entry
        self.password_entry = tk.Entry(self.search_frame, width=20, bg=SECONDARY_COLOR, fg=PRIMARY_COLOR, font=LABEL_FONT, show="*")
        self.password_entry.grid(row=4, column=1, padx=(0, 10), pady=(5, 0))

        # Login button
        self.login_button = tk.Button(self.search_frame, text="Login", bg=ACCENT_COLOR, fg=SECONDARY_COLOR,
                                 font=BUTTON_FONT, command=self.login)
        self.login_button.grid(row=3, column=2, rowspan=2, padx=(0, 10), pady=(20, 0), sticky=tk.NS)

        # Registration button
        self.registration_button = tk.Button(self.search_frame, text="Register", bg=SECONDARY_COLOR, fg=PRIMARY_COLOR,
                                        font=SMALL_FONT, command=self.open_registration_window)
        self.registration_button.grid(row=5, column=1, pady=(10, 0))

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        user = self.controller.login_user(username, password)

        if user:
            self.logged_in_user = user
            messagebox.showinfo("Success", "Login successful.")
            # Hide login-related widgets
            self.username_entry.grid_remove()
            self.username_label.grid_remove()
            self.password_label.grid_remove()
            self.password_entry.grid_remove()
            self.login_button.grid_remove()
            self.registration_button.grid_remove()

            # Show welcome message or perform other actions
            welcome_label = tk.Label(self.search_frame, text=f"Welcome, {username}!", bg=BG_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
            welcome_label.grid(row=3, column=0, columnspan=3, padx=(10, 10), pady=(20, 0))

            # Create and position the favorite list button
            favorite_button = tk.Button(self.root, text="Favorite List", bg=ACCENT_COLOR, fg=SECONDARY_COLOR,
                                        font=BUTTON_FONT, command=self.open_favorite_window)
            favorite_button.place(x=10, y=10)

        else:
            messagebox.showerror("Error", "Invalid username or password.")

    def open_registration_window(self):
        self.registration_window = tk.Toplevel(self.root)
        self.registration_window.title("Registration")
        self.registration_window.configure(bg=BG_COLOR)

        # Registration form elements
        name_label = tk.Label(self.registration_window, text="Name:", bg=BG_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
        name_label.grid(row=0, column=0, padx=(10, 10), pady=(10, 0), sticky=tk.W)
        self.name_entry = tk.Entry(self.registration_window, width=20, bg=SECONDARY_COLOR, fg=PRIMARY_COLOR,
                                   font=LABEL_FONT)
        self.name_entry.grid(row=0, column=1, padx=(0, 10), pady=(10, 0))

        email_label = tk.Label(self.registration_window, text="Email:", bg=BG_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
        email_label.grid(row=1, column=0, padx=(10, 10), pady=(5, 0), sticky=tk.W)
        self.email_entry = tk.Entry(self.registration_window, width=20, bg=SECONDARY_COLOR, fg=PRIMARY_COLOR,
                                    font=LABEL_FONT)
        self.email_entry.grid(row=1, column=1, padx=(0, 10), pady=(5, 0))

        password_label = tk.Label(self.registration_window, text="Password:", bg=BG_COLOR, fg=TEXT_COLOR,
                                  font=LABEL_FONT)
        password_label.grid(row=2, column=0, padx=(10, 10), pady=(5, 0), sticky=tk.W)
        self.password_entry = tk.Entry(self.registration_window, width=20, bg=SECONDARY_COLOR, fg=PRIMARY_COLOR,
                                       font=LABEL_FONT, show="*")
        self.password_entry.grid(row=2, column=1, padx=(0, 10), pady=(5, 0))

        confirm_password_label = tk.Label(self.registration_window, text="Confirm Password:", bg=BG_COLOR,
                                          fg=TEXT_COLOR, font=LABEL_FONT)
        confirm_password_label.grid(row=3, column=0, padx=(10, 10), pady=(5, 0), sticky=tk.W)
        self.confirm_password_entry = tk.Entry(self.registration_window, width=20, bg=SECONDARY_COLOR, fg=PRIMARY_COLOR,
                                               font=LABEL_FONT, show="*")
        self.confirm_password_entry.grid(row=3, column=1, padx=(0, 10), pady=(5, 0))

        register_button = tk.Button(self.registration_window, text="Register", bg=ACCENT_COLOR, fg=SECONDARY_COLOR,
                                    font=BUTTON_FONT, command=self.register)
        register_button.grid(row=4, column=1, pady=(10, 10))

    def register(self):
        name = self.name_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.")
            return

        success = self.controller.register_user(name, email, password)

        if success:
            messagebox.showinfo("Success", "User registered successfully.")
            self.registration_window.destroy()
        else:
            messagebox.showerror("Error", "Email already exists.")

    def open_favorite_window(self):
        if not hasattr(self, 'favorite_window') or self.favorite_window is None or not self.favorite_window.winfo_exists():
            self.favorite_window = tk.Toplevel(self.root)
            self.favorite_window.title("Favorite List")
            self.favorite_window.configure(bg=BG_COLOR)
            self.favorite_window.geometry("800x500")

            user_id = self.logged_in_user[0]
            favorite_comics = self.controller.get_favorite_comics(user_id)

            favorite_canvas = tk.Canvas(self.favorite_window, bg=BG_COLOR)
            favorite_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            scrollbar = tk.Scrollbar(self.favorite_window, orient=tk.VERTICAL, command=favorite_canvas.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            favorite_canvas.configure(yscrollcommand=scrollbar.set)

            favorite_frame = tk.Frame(favorite_canvas, bg=BG_COLOR)
            favorite_canvas.create_window((0, 0), window=favorite_frame, anchor=tk.NW)

            def on_mousewheel(event):
                favorite_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

            favorite_canvas.bind_all("<MouseWheel>", on_mousewheel)

            if favorite_comics:
                for comic in favorite_comics:
                    comic_frame = tk.Frame(favorite_frame, bg=BG_COLOR)
                    comic_frame.pack(pady=5, anchor=tk.W)

                    title_label = tk.Label(comic_frame, text=comic['comic_title'], bg=BG_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
                    title_label.pack(side=tk.LEFT, anchor=tk.W)

                    remove_button = tk.Button(comic_frame, text="Remove", bg=ACCENT_COLOR, fg=SECONDARY_COLOR,
                                              font=SMALL_FONT, command=lambda comic_id=comic['id']: self.remove_from_favorites(comic_id))
                    remove_button.pack(side=tk.RIGHT, padx=10)

                    description_label = tk.Label(comic_frame, text=comic['comic_description'], bg=BG_COLOR, fg=TEXT_COLOR,
                                                 font=SMALL_FONT, wraplength=350)
                    description_label.pack(anchor=tk.W)

            else:
                empty_label = tk.Label(favorite_frame, text="No favorite comics yet.", bg=BG_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
                empty_label.pack()

            favorite_frame.bind("<Configure>", lambda e: favorite_canvas.configure(scrollregion=favorite_canvas.bbox("all")))

            self.favorite_window.protocol("WM_DELETE_WINDOW", self.on_favorite_window_close)
        else:
            self.favorite_window.lift()

    def on_favorite_window_close(self):
        self.favorite_window.destroy()
        self.favorite_window = None

    def remove_from_favorites(self, comic_id):
        user_id = self.logged_in_user[0]
        success = self.controller.remove_favorite_comic(user_id, comic_id)

        if success:
            messagebox.showinfo("Success", "Comic removed from favorites.")
            self.open_favorite_window()
        else:
            messagebox.showerror("Error", "Failed to remove comic from favorites.")

    def search_api(self):
        if hasattr(self, 'query_entry') and self.query_entry is not None:
            query = self.query_entry.get()
            if query:
                print("Query is not empty")
                results = self.controller.search(query, self.current_page)
                self.show_results(results)
            else:
                print("Query is empty")
        else:
            print("query_entry is None")

    def on_mousewheel(self, event):
        self.results_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

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
            hero_list_frame.bind("<Configure>",
                                 lambda e: self.results_canvas.configure(scrollregion=self.results_canvas.bbox("all")))
            self.results_canvas.create_window((0, 0), window=hero_list_frame, anchor="nw")

            pagination_frame = tk.Frame(hero_list_frame, bg=BG_COLOR)
            pagination_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

            prev_button = tk.Button(pagination_frame, text="Previous", bg=ACCENT_COLOR, fg=SECONDARY_COLOR,
                                    font=BUTTON_FONT, command=self.previous_page)
            prev_button.pack(side=tk.LEFT)

            next_button = tk.Button(pagination_frame, text="Next", bg=ACCENT_COLOR, fg=SECONDARY_COLOR,
                                    font=BUTTON_FONT, command=self.next_page)
            next_button.pack(side=tk.RIGHT)

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
                                          command=lambda url=result["comics_url"]: self.retrieve_and_display_comics(
                                              url))
                comics_button.pack(pady=5, anchor="w")

                # Bind mouse wheel event to the canvas
                self.results_canvas.bind_all("<MouseWheel>", self.on_mousewheel)

                # Set a fixed size for the results window
                self.root.geometry("800x600")

    def previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.search_api()

    def next_page(self):
        self.current_page += 1
        self.search_api()

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
            "limit": 100,
            "orderBy": "-onsaleDate"
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
                        "thumbnail_url": result["thumbnail"]["path"] + "/portrait_uncanny." + result["thumbnail"][
                            "extension"],
                        "description": result["description"],
                        "prices": result["prices"]
                    }
                    comics_list.append(comic_item)

                cache[comics_url] = comics_list  # Cache the comics list
                self.display_comics_list(comics_list)
            else:
                self.show_error("No comics found.")

    def display_comic_page(self, comics_canvas, page):
        comics_frame = comics_canvas.find_withtag("comics_frame")
        if comics_frame:
            comics_canvas.delete("comics_frame")

        new_comics_frame = tk.Frame(comics_canvas, bg=BG_COLOR)
        comics_canvas.create_window((0, 0), window=new_comics_frame, anchor=tk.NW, tags=("comics_frame",))

        start_index = (page - 1) * 10
        end_index = min(start_index + 10, len(self.comics_list))

        row_index = 0
        for comic_item in self.comics_list[start_index:end_index]:
            thumbnail_url = comic_item.get("thumbnail_url", "")

            if comic_item['prices']:
                price = comic_item['prices'][0]['price']
                price_label = tk.Label(new_comics_frame, text=f"Price: ${price:.2f}", bg=BG_COLOR, fg=TEXT_COLOR,
                                       font=SMALL_FONT)
                price_label.grid(row=row_index + 1, column=0, padx=2, pady=2, sticky=tk.N)
            else:
                price_label = tk.Label(new_comics_frame, text="Price: N/A", bg=BG_COLOR, fg=TEXT_COLOR,
                                       font=SMALL_FONT)
                price_label.grid(row=row_index + 1, column=0, padx=2, pady=2, sticky=tk.N)

            if thumbnail_url:
                image_bytes = requests.get(thumbnail_url).content
                image_data = io.BytesIO(image_bytes)
                img = Image.open(image_data)
                img = img.resize((100, 150))
                img = ImageTk.PhotoImage(img)

                thumbnail_label = tk.Label(new_comics_frame, image=img, bg=BG_COLOR)
                thumbnail_label.image = img
                thumbnail_label.grid(row=row_index, column=0, padx=5, pady=5, sticky=tk.W)

            title_label = tk.Label(new_comics_frame, text=comic_item['title'], bg=BG_COLOR, fg=TEXT_COLOR,
                                   font=LABEL_FONT)
            title_label.grid(row=row_index, column=1, padx=2, sticky=tk.W)

            des_label = tk.Label(new_comics_frame, text=comic_item['description'], bg=BG_COLOR, fg=TEXT_COLOR,
                                 font=SMALL_FONT, wraplength=500)
            des_label.grid(row=row_index + 1, column=1, padx=2, pady=2, sticky=tk.W)

            add_button = tk.Button(new_comics_frame, text="Add", bg=ACCENT_COLOR, fg=SECONDARY_COLOR,
                                   font=SMALL_FONT, command=lambda comic=comic_item: self.add_to_favorites(comic))
            add_button.grid(row=row_index, column=2, padx=5, pady=5)

            new_comics_frame.columnconfigure(0, weight=1)
            new_comics_frame.columnconfigure(1, weight=1)

            row_index += 2

        comics_canvas.update_idletasks()
        comics_canvas.config(scrollregion=comics_canvas.bbox('all'))

    def add_to_favorites(self, comic):
        user_id = self.logged_in_user[0]
        comic_title = comic['title']
        comic_description = comic['description']

        success = self.controller.add_favorite_comic(user_id, comic_title, comic_description)

        if success:
            messagebox.showinfo("Success", "Comic added to favorites.")
        else:
            messagebox.showerror("Error", "Failed to add comic to favorites.")

    def display_comics_list(self, comics_list):
        # Testing methods runtime
        start = time.time()

        self.comics_list = comics_list  # Store the comics_list as an instance variable
        # ...
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

        self.current_comic_page = 1
        self.total_comic_pages = (len(self.comics_list) - 1) // 10 + 1

        self.display_comic_page(comics_canvas, self.current_comic_page)

        pagination_frame = tk.Frame(comics_window, bg=BG_COLOR)
        pagination_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        prev_button = tk.Button(pagination_frame, text="Previous", bg=ACCENT_COLOR, fg=SECONDARY_COLOR,
                                font=BUTTON_FONT,
                                command=lambda: self.change_comic_page(-1, comics_canvas, prev_button, next_button))
        prev_button.pack(side=tk.LEFT)

        next_button = tk.Button(pagination_frame, text="Next", bg=ACCENT_COLOR, fg=SECONDARY_COLOR,
                                font=BUTTON_FONT,
                                command=lambda: self.change_comic_page(1, comics_canvas, prev_button, next_button))
        next_button.pack(side=tk.RIGHT)

        # Disable the "Previous" button initially
        prev_button.config(state=tk.DISABLED)

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

    def change_comic_page(self, offset, comics_canvas, prev_button, next_button):
        new_page = self.current_comic_page + offset
        if 1 <= new_page <= self.total_comic_pages:
            self.current_comic_page = new_page
            self.display_comic_page(comics_canvas, self.current_comic_page)

            # Disable the "Previous" button if on the first page
            if self.current_comic_page == 1:
                prev_button.config(state=tk.DISABLED)
            else:
                prev_button.config(state=tk.NORMAL)

            # Disable the "Next" button if on the last page
            if self.current_comic_page == self.total_comic_pages:
                next_button.config(state=tk.DISABLED)
            else:
                next_button.config(state=tk.NORMAL)

    def show_error(self, message):
        error_window = tk.Toplevel(self.root)
        error_window.title("Error")
        error_window.configure(bg=BG_COLOR)

        error_label = tk.Label(error_window, text=message, bg=BG_COLOR, fg="#fcbd19", font=LABEL_FONT)
        error_label.pack(pady=20)
