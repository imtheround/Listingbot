import asyncio, json, os, datetime, aiohttp

async def handle(error, filename):
        f = open("../logs.txt", "a+")
        f.write(f"\n[{datetime.datetime.now()}] Error: {error} while running in {filename}")
        f.close()
        f = open("../config.json", "r")
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
        

if  __name__ == "__main__":
    print(asyncio.run(handle("test", "test.py")))