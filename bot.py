import discord
from discord.ext import commands
import os
import json
from utils.generalUtils import handleError
from db.dbStuff import dbStuff

# Load the token
with open("/home/round/projects/ListingBot/config.json", "r") as f:
    token = json.load(f)["token"]

# Set up the bot with required intents
intents = discord.Intents.all()
intents.message_content = True  # Ensure message content intent is enabled
bot = commands.Bot(command_prefix='!', intents=intents)

async def load_commands():
    for filename in os.listdir('/home/round/projects/ListingBot/commands'):
        if filename.endswith('.py'):
            await bot.load_extension(f'commands.{filename[:-3]}')
            print(f"Loaded command: {filename[:-3]}")

@bot.event
async def on_ready():
    await handleError().initProject()
    await dbStuff().init()
    await load_commands()  # Load commands when the bot is ready
    await bot.tree.sync()  # Sync commands only once here
    print(f'Logged in as {bot.user}!')

# Temporary command added directly to bot.py for testing
@bot.tree.command(name="dm_test", description="Test command for DM")
async def dm_test(interaction: discord.Interaction):
    await interaction.response.send_message("This command works in both DMs and servers!")

# Run the bot
if __name__ == "__main__":
    bot.run(token)
