import discord
from discord.ext import commands
import os, json
from utils.generalUtils import handleError
f = open("/home/round/projects/ListingBot/config.json", "r")
token = json.load(f)["token"]
f.close()
# Set up the bot with required intents
intents = discord.Intents.all()
intents.message_content = True  # Ensure message content intent is enabled
bot = commands.Bot(command_prefix='!', intents=intents)

async def load_commands():
    for filename in os.listdir('/home/round/projects/ListingBot/commands'):
        if filename.endswith('.py'):
            await bot.load_extension(f'commands.{filename[:-3]}')  # Await here
            print(f"Loaded command: {filename[:-3]}")  # Debug statement

@bot.event
async def on_ready():
    await handleError().initProject()
    await load_commands()  # Load commands when the bot is ready
    await bot.tree.sync()  # Sync command tree with Discord
    print(f'Logged in as {bot.user}!')

# Run the bot
if __name__ == "__main__":
    bot.run(token)