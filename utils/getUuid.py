import requests
import asyncio
import json
import utils.caching
from utils.caching import Caching
async def get_uuid(username):
    uuid = Caching().load_cache_uuid()
    try:
        uuid =  uuid[username]
        return uuid
    except:
        pass
    response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
    if response.status_code == 200:
        json_data = json.loads(response.text)
        uuid = json_data['id']
        Caching().save_cache_uuid(uuid, username)
    else:
        uuid = "error"
    return uuid
    
    
if  __name__ == "__main__":
    print(asyncio.run(get_uuid("refraction")))