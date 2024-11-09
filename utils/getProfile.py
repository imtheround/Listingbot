import requests
import json
import asyncio
from getUuid import get_uuid

async def get_profile(uuid, profile = None, **args):
    f = open("/home/round/projects/ListingBot/config.json", "r")
    config = json.load(f)
    API_KEY = config["API_KEY"]
    response = requests.get(f"https://api.hypixel.net/v2/skyblock/profiles?key={API_KEY}&uuid={uuid}")
    if response.status_code != 200:
        return None
    data = json.loads(response.text)
    if profile is not None:
        for i in data['profiles']:
            if i == len(data['profiles']):
                return None
            if i['cute_name'] == profile:
                return i['profile_id']
    else:
        profiles = []
        for i in data['profiles']:
            data = {
                "CuteName": i['cute_name'],
                "ProfileID": i['profile_id']
            }
            profiles.append(data)
        return profiles
    return None

if  __name__ == "__main__":
    print(asyncio.run(get_profile("28667672039044989b0019b14a2c34d6")))