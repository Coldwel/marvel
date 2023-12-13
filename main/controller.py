# controller.py
import hashlib
from model import MarvelAPI


class SearchController:
    def __init__(self, public_key, private_key):
        self.marvel_api = MarvelAPI(public_key, private_key)
        self.PUBLIC_KEY = public_key
        self.PRIVATE_KEY = private_key

    def search(self, query):
        # Implement the search logic using MarvelAPI
        return self.marvel_api.search_characters(query)

    def generate_hash(self, timestamp):
        hash_input = timestamp + self.PRIVATE_KEY + self.PUBLIC_KEY
        md5_hash = hashlib.md5(hash_input.encode('utf-8')).hexdigest()
        return md5_hash
