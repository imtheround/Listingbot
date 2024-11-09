import discord
from discord.ext import commands
import requests
import os
import json
import sys

from db.dbStuff import dbStuff
class listCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = dbStuff()
    @discord.app_commands.command(name="setsellerrole", description="set the seller role")
    @discord.app_commands.describe(seller_role="role")
    async def uuid(self, interaction: discord.Interaction, seller_role: discord.Role):
        await interaction.response.defer()
        await self.db.set_seller_role(seller_role.id)
        await interaction.followup.send(f"Seller role set to {seller_role.mention}", ephemeral=True)
    
    @discord.app_commands.command(name="setowner", description="Appoint a owner")
    @discord.app_commands.describe(human="seller")
    async def appointSeller(self, interaction: discord.Interaction, human: discord.Member):
        await interaction.response.defer()
        await self.db.add_owner(human.id)
        await interaction.followup.send(f"gigger {human.mention} appointed", ephemeral=True)




async def setup(bot):
    await bot.add_cog(listCommand(bot))
    
