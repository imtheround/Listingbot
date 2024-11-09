import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

class Caching:
    def __init__(self):
        self.cache = "../cache/accCache.json"
        self.uuidCache = "../cache/uuids.json"
        
    def load_cache(self):
        with open(self.cache, "r") as f:
            self.cached = json.loads(f.read())
            return self.cached
    
    def save_cache(self, itemname, item):
        cached = self.load_cache()
        cached[itemname] = item
        json.dump(cached, open(self.cache, "w"), indent=4)
    def delete_cache(self, itemname):
        cached = self.load_cache()
        del cached[itemname]
    def save_cache_uuid(self, uuid, username):
        cached = self.load_cache_uuid()
        cached[username] = uuid
        json.dump(cached, open(self.uuidCache, "w"), indent=4)
        
    def load_cache_uuid(self):
        f = open(self.uuidCache, "r")
        content = f.read()
        cached = json.loads(content)
        f.close()
        return cached
    def delete_cache_uuid(self, username):
        cached = self.load_cache()
        del cached[username]

