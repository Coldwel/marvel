# cache.py
from cachetools import TTLCache

# Initialize the cache with a maximum size of 100 and expiration time of 1 hour
cache = TTLCache(maxsize=100, ttl=3600)
