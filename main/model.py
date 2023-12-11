# model.py
import json
import requests
import hashlib

with open("config.json") as f:
    config = json.load(f)

PUBLIC_KEY = config["MARVEL_PUBLIC_KEY"]
PRIVATE_KEY = config["MARVEL_PRIVATE_KEY"]

MARVEL_CHARACTER_URL = "http://gateway.marvel.com/v1/public/characters"


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
        response = requests.get(MARVEL_CHARACTER_URL, headers=headers, params=params)
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
