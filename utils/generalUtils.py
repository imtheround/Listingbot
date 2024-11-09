import asyncio, json, os, datetime, aiohttp, traceback

class handleError():
    def __init__(self):
        pass
    async def initProject(self):
        os.system("touch ../cache/accCache.json")
        with open('../cache/accCache.json', 'w') as f:
            f.write("{}")
        return
    async def handle(self,error, filename):
        f = open("../logs.txt", "a+")
        f.write(f"\n[{datetime.datetime.now()}] Error: \n{error} while running in {filename}")
        f.close()
        f = open("/home/round/projects/ListingBot/config.json", "r")
        webhook = f.read()
        webhook = json.loads(webhook)["errorWebhook"]
        async with aiohttp.ClientSession() as session:
            webhookHeaders = {
                "username": "Listing Bot Error",
                "content": "<@895394445195903047>",
                "embeds": [
                    {
                    "title": "**Error**",
                    "description": f"Imagine writting bad code smh \n\n **Error:** \n ```{error}```",
                    "color": 15258703,
                    }
                ]
                }
            await session.post(webhook, json=webhookHeaders)
        return {"sucess": True, "cause": "ok"}