import tkinter as tk
import requests
from PIL import Image, ImageTk
import io
import hashlib
from tkinter.scrolledtext import ScrolledText
from cachetools import TTLCache
import json

# loads config file holding API keys
with open("config.json") as f:
    config = json.load(f)

PUBLIC_KEY = config["MARVEL_PUBLIC_KEY"]
PRIVATE_KEY = config["MARVEL_PRIVATE_KEY"]

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

# Initialize the cache with a maximum size of 100 and expiration time of 1 hour
cache = TTLCache(maxsize=100, ttl=3600)


class MarvelAPI:
    def __init__(self, public_key, private_key):
        self.public_key = public_key
        self.private_key = private_key

    def generate_hash(self, timestamp):
        hash_input = timestamp + self.private_key + self.public_key
        md5_hash = hashlib.md5(hash_input.encode('utf-8')).hexdigest()
        return md5_hash

    def search_characters(self, query):
        timestamp = "1"
        md5_hash = self.generate_hash(timestamp)

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        params = {
            "ts": timestamp,
            "apikey": self.public_key,
            "hash": md5_hash,
            "nameStartsWith": query
        }
        response = requests.get("https://gateway.marvel.com/v1/public/characters", headers=headers, params=params)
        data = response.json()

        results = []
        if data["data"]["total"] > 0:
            for result in data["data"]["results"]:
                thumbnail = result["thumbnail"]
                item = {
                    "name": result["name"],
                    "description": result["description"],
                    "image_url": thumbnail["path"] + "/landscape_large.jpg",
                    "comics_url": result["comics"]["collectionURI"]
                }
                results.append(item)

        return results


class SearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Marvel Search App")
        self.root.configure(bg=BG_COLOR)

        self.search_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.search_frame.pack(pady=10)

        self.query_label = tk.Label(self.search_frame, text="Search Character:", bg=BG_COLOR, fg=TEXT_COLOR,
                                    font=LABEL_FONT)
        self.query_label.pack(side=tk.LEFT, padx=(10, 10))

        self.query_entry = tk.Entry(self.search_frame, width=20, bg=SECONDARY_COLOR, fg=BG_COLOR, font=LABEL_FONT)
        self.query_entry.pack(side=tk.LEFT)

        self.search_button = tk.Button(self.search_frame, text="Search", bg=ACCENT_COLOR, fg=SECONDARY_COLOR,
                                       font=BUTTON_FONT, command=self.search_api)
        self.search_button.pack(side=tk.LEFT, padx=(10, 10))

        self.results_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.comics_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.comics_frame.pack_forget()

        self.marvel_api = MarvelAPI(PUBLIC_KEY, PRIVATE_KEY)

    def search_api(self):
        query = self.query_entry.get()
        if query:
            if query in cache:
                results = cache[query]
                self.show_results(results)
            else:
                timestamp = "1"
                md5_hash = self.marvel_api.generate_hash(timestamp)

                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
                params = {
                    "ts": timestamp,
                    "apikey": PUBLIC_KEY,
                    "hash": md5_hash,
                    "nameStartsWith": query
                }
                response = requests.get("https://gateway.marvel.com/v1/public/characters", headers=headers,
                                        params=params)
                data = response.json()

                results = []
                if data["data"]["total"] > 0:
                    for result in data["data"]["results"]:
                        item = {
                            "name": result["name"],
                            "description": result["description"],
                            "image_url": result["thumbnail"]["path"],
                            "comics_url": result["comics"]["collectionURI"]
                        }
                        item["image_url"] += "/landscape_large.jpg"
                        results.append(item)

                    cache[query] = results  # Cache the results

                    self.show_results(results)
                else:
                    self.show_error("No results found.")

    def show_results(self, results):
        self.results_frame.pack(fill=tk.BOTH, expand=True)

        for widget in self.results_frame.winfo_children():
            widget.destroy()

        if len(results) > 0:
            canvas = tk.Canvas(self.results_frame, bg=BG_COLOR, bd=0, highlightthickness=0, height=400, width=600)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            scrollbar = tk.Scrollbar(self.results_frame, orient=tk.VERTICAL, command=canvas.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            canvas.configure(yscrollcommand=scrollbar.set)

            hero_list_frame = tk.Frame(canvas, bg=BG_COLOR)
            hero_list_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=hero_list_frame, anchor="nw")

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

                hero_name = tk.Label(hero_info_frame, text=result["name"], bg=BG_COLOR, fg=TEXT_COLOR, font=LABEL_FONT,
                                     wraplength=300)
                hero_name.pack(pady=5, anchor="w")

                hero_desc = tk.Label(hero_info_frame, text=result["description"], bg=BG_COLOR, fg=TEXT_COLOR,
                                     font=LABEL_FONT, wraplength=300)
                hero_desc.pack(pady=5, anchor="w")

                comics_button = tk.Button(hero_info_frame, text="Comics", bg=ACCENT_COLOR, fg=SECONDARY_COLOR,
                                          font=BUTTON_FONT,
                                          command=lambda url=result["comics_url"]: self.show_comics_window(url))
                comics_button.pack(pady=5, anchor="w")

    def show_comics_window(self, comics_url):
        if comics_url in cache:
            comics_list = cache[comics_url]
            self.display_comics_list(comics_list)
        else:
            timestamp = "1"
            md5_hash = self.marvel_api.generate_hash(timestamp)

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

                cache[comics_url] = comics_list  # Cache the comics list

                self.display_comics_list(comics_list)
            else:
                self.show_error("No comics found.")

    def display_comics_list(self, comics_list):
        message = "\n".join(comics_list)

        # create a new window to show the comics list
        comics_window = tk.Toplevel(self.root)
        comics_window.title("Comics List")
        comics_window.configure(bg=BG_COLOR, pady=5)
        comics_window.geometry('500x400')

        # create a ScrolledText widget to show the comics list
        comics_text = ScrolledText(comics_window, bg=BG_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
        comics_text.pack(fill=tk.BOTH, expand=True)
        comics_text.insert(tk.END, message)
        comics_text.configure(state="disabled")

    def show_error(self, message):
        error_window = tk.Toplevel(self.root)
        error_window.title("Error")
        error_window.configure(bg=BG_COLOR)

        error_label = tk.Label(error_window, text=message, bg=BG_COLOR, fg=TEXT_COLOR, font=LABEL_FONT)
        error_label.pack(pady=20)


if __name__ == "__main__":
    root = tk.Tk()
    app = SearchApp(root)

    # Set the initial size of the main window
    root.geometry("800x600")

    # Update the size of the comics window
    def show_comics_window(url):
        comics_window = tk.Toplevel(root)
        comics_window.title("Comics List")

        # Set the size of the comics window
        comics_window.geometry("600x400")

        # Call the show_comics method
        app.show_comics(url)

    app.show_comics = show_comics_window

    root.mainloop()
