import discord
from discord.ext import commands
import requests
import os
import json
import sys
from utils import getUuid

class listCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="list", description="Get the UUID of a specified Minecraft username")
    async def uuid(self, interaction: discord.Interaction, username: str):
        uuid = await getUuid.get_uuid(username)

        # Create an embed to display the username and UUID+
        embed = discord.Embed(title="Minecraft UUID", color=discord.Color.green())
        embed.add_field(name="Username", value=username, inline=True)
        embed.add_field(name="UUID", value=uuid, inline=True)

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(listCommand(bot))
    
