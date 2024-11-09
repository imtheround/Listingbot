import discord
from discord.ext import commands
import requests
import os
import json
import sys
import chat_exporter
import io
class exporter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.export = chat_exporter
    @discord.app_commands.command(name="exportchat", description="set the seller role")
    async def exportchat(self, interaction: discord.Interaction):
        await interaction.response.defer()
        transcript = await self.export.export(interaction.channel)
        transcript_file = discord.File(
                io.BytesIO(transcript.encode()),
                filename=f"transcript.html",
            )
        await interaction.followup.send(f"Chat exported", ephemeral=True, file=transcript_file)


async def setup(bot):
    await bot.add_cog(exporter(bot))
    
