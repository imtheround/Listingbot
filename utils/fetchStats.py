import asyncio, json, getUuid, calcNw, getProfile, runJsFetchstat, asqlite3, generalUtils, traceback,datetime

class fetchNetworth():
    def __init__(self):
        self.errorhandle = generalUtils.handleError()
        pass
        
    async def get_data(self,uuid, username, **args):
        try:
            self.uuid = uuid
            self.profileStats = runJsFetchstat.run_js_fetchstat(username, self.uuid)
            self.playerSocial = self.profileStats['social']
            self.profiles = []
            self.skyblockProfiles = []
            for i in range(len(self.profileStats['skyblock'])):
                self.profiles.append(self.profileStats['skyblock'][i]['name'])
            for i in range(len(self.profiles)):
                self.skyblockStats = self.profileStats['skyblock'][i]
                self.skyblockCatacombs = self.skyblockStats['catacombs']
                self.skyblockSkills = self.skyblockStats['skills']
                self.profileName = self.profiles[i]
                try:
                    self.skyblockHotm = {
                        "HotmLevel": self.skyblockStats['mining']['hotm'],
                        "gemstonePowder": self.skyblockStats['mining']['gemstonePowder'],
                        "mithrilPowder": self.skyblockStats['mining']['mithrilPowder']
                    }
                except:
                    self.skyblockHotm = {
                        "HotmLevel": self.skyblockStats['mining']['HOTM'],
                        "gemstonePowder": self.skyblockStats['mining']['gemstonePowder'],
                        "mithrilPowder": self.skyblockStats['mining']['mithrilPowder']
                    }
                self.skyblockSlayers = self.skyblockStats['slayers']
                self.skyblockBank = self.skyblockStats['bank']
                self.skyblockPurse = self.skyblockStats['purse']
                self.skyblockLiquideCoins = self.skyblockStats['liquid']
                self.skyblockNetworth = self.skyblockStats['networth']
                self.skyblockunsoulboundNetworth = self.skyblockStats['unsoulboundNetworth']
                self.skyblocksoulboundNetworth = self.skyblockNetworth - self.skyblockunsoulboundNetworth
                self.profilemembers = self.skyblockStats['members']
                self.profilegamemode = self.skyblockStats['gameMode']
                self.skyblockLevel = self.skyblockStats['levels']
                self.lowballValue = await calcNw.calculate_lowball(self.skyblockCatacombs, self.skyblockSkills, self.skyblockHotm, self.skyblockSlayers, self.skyblockLiquideCoins, self.skyblockunsoulboundNetworth, self.skyblocksoulboundNetworth, self.profilemembers,self.profilegamemode)
                self.value = await calcNw.calculate_value(self.skyblockCatacombs, self.skyblockSkills, self.skyblockHotm, self.skyblockSlayers, self.skyblockLiquideCoins, self.skyblockunsoulboundNetworth, self.skyblocksoulboundNetworth, self.profilemembers,self.profilegamemode)
                self.profileStat ={
                    self.profileName:
                        {
                    "catacombs": self.skyblockCatacombs,
                    "skills": self.skyblockSkills,
                    "hotm": self.skyblockHotm,
                    "slayers": self.skyblockSlayers,
                    "bank": self.skyblockBank,
                    "purse": self.skyblockPurse,
                    "liquid": self.skyblockLiquideCoins,
                    "networth": self.skyblockNetworth,
                    "unsoulboundNetworth": self.skyblockunsoulboundNetworth,
                    "soulboundNetworth": self.skyblocksoulboundNetworth,
                    "members": self.profilemembers,
                    "gameMode": self.profilegamemode,
                    "levels": self.skyblockLevel
                },
                "valuation": {
                    "lowball": self.lowballValue,
                    "value": self.value
                }
                }
                self.skyblockProfiles.append(self.profileStat)
            self.stats = {
                "sucess": True,
                "social": self.playerSocial,
                "last_updated": datetime.datetime.timestamp(datetime.datetime.now()),
                "profiles": self.skyblockProfiles
            }
            
            return self.stats
        except Exception as e:
            error_details = traceback.format_exc(limit=4, chain=True)
            e = await self.errorhandle.handle(error_details, "fetchStats.py")
            return e

if __name__ == "__main__":
    a = fetchNetworth().get_data("refraction")
    print(asyncio.run(a))