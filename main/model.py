# model.py
import json
import requests
import hashlib
from mysql.connector import Error
from mysql.connector.connection import MySQLConnection

with open("config.json") as f:
    config = json.load(f)

PUBLIC_KEY = config['MARVEL_PUBLIC_KEY']
PRIVATE_KEY = config['MARVEL_PRIVATE_KEY']

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'marvel_db'
}

MARVEL_CHARACTER_URL = "http://gateway.marvel.com/v1/public/characters"


class MarvelAPI:
    def __init__(self, public_key, private_key):
        self.public_key = public_key
        self.private_key = private_key

    def generate_hash(self, timestamp):
        hash_input = timestamp + self.private_key + self.public_key
        md5_hash = hashlib.md5(hash_input.encode('utf-8')).hexdigest()
        return md5_hash

    def search_characters(self, query, page=1):
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
            "nameStartsWith": query,
            "offset": (page - 1) * 25,
            "limit": 25
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


class Database:
    def __init__(self, config):
        self.config = config

    def __enter__(self):
        try:
            self.conn = MySQLConnection(**self.config)
            print("Connected to the MySQL database")
            return self.conn
        except Error as e:
            print(f"Error connecting to the MySQL database: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
            print("Disconnected from the MySQL database")
