# controller.py
from model import MarvelAPI


class SearchController:
    def __init__(self, public_key, private_key):
        self.marvel_api = MarvelAPI(public_key, private_key)
        self.PUBLIC_KEY = public_key
        self.PRIVATE_KEY = private_key

    def search(self, query):
        # Implement the search logic using MarvelAPI
        return self.marvel_api.search_characters(query)
