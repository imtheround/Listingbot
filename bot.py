import discord
from discord.ext import commands
import os
import json
from utils.generalUtils import handleError
from db.dbStuff import dbStuff

with open("/home/round/projects/ListingBot/config.json", "r") as f:
    token = json.load(f)["token"]

intents = discord.Intents.all()
intents.message_content = True 
bot = commands.Bot(command_prefix='!', intents=intents)
bot.help_command = None
async def load_commands():
    for filename in os.listdir('/home/round/projects/ListingBot/commands'):
        if filename.endswith('.py'):
            await bot.load_extension(f'commands.{filename[:-3]}')
            print(f"Loaded command: {filename[:-3]}")

@bot.event
async def on_ready():
    await handleError().initProject()
    await dbStuff().init()
    await load_commands()  
    await bot.tree.sync() 
    print(f'Logged in as {bot.user}!')


if __name__ == "__main__":
    bot.run(token)
