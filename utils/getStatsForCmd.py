from caching import Caching
from utils.getProfile import get_profile
from utils.getUuid import get_uuid
from utils.fetchStats import fetchNetworth
import datetime
class getStatsForCmd:
    def __init__(self):
        self.caching = Caching()
        self.cached = {}
    async def get_stats(self,username, profile: str = ""):
        caching = Caching()
        cached = caching.load_cache()
        try:
            self.cached[username]
            if self.cached[username]['last_updated'] - datetime.datetime.timestamp(datetime.datetime.now()) < 1800:
                stats = self.cached[username]
                if profile == "" or profile == "none":
                    stats = stats['profiles'][0]
                else:
                    for i in range(len(stats['profiles'])):
                        if next(iter(stats['profile'][i].keys())) == profile:
                            stats = stats['profiles'][i]
                            break
                        if i == len(stats['profiles']):
                            return {"sucess": False, "cause": "No profile found, you sure this is a valid profile?"}
                caching.save_cache(username, stats)
                return stats
            else:
                pass
        except:
            pass
        data = fetchNetworth()
        uuid = await get_uuid(username,)
        if uuid == None:
            return {"sucess": False, "cause": "No UUID found, you sure this is a valid username?"}
        if profile == "" or profile == "none":
            stats = await data.get_data(uuid=uuid, username=username)
            if stats['sucess'] == False:
                return  {"sucess": False, "cause": stats['cause']}
            stats = stats['profiles'][0]
        else:
            stats = await data.get_data(uuid, username)
            if stats['sucess'] == False:
                return  {"sucess": False, "cause": stats['cause']}
            self.cached[username] = stats
            self.caching.save_cache(username, stats)
            for i in range(len(stats['profiles'])):
                if next(iter(stats['profiles'][i].keys())) == profile:
                    stats = stats['profiles'][i]
                    break
                if i == len(stats['profiles']):
                    return {"sucess": False, "cause": "No profile found, you sure this is a valid profile?"}
        caching.save_cache(username, stats)
        return stats