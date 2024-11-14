import discord
from discord.ext import commands
import requests
import os
import json
import sys

from db.dbStuff import dbStuff
class appointSeller(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = dbStuff()
    @discord.app_commands.command(name="setsellerrole", description="set the seller role")
    @discord.app_commands.describe(seller_role="role")
    async def uuid(self, interaction: discord.Interaction, seller_role: discord.Role):
        if interaction.user.guild_permissions.administrator == False:
            await interaction.response.send_message("You don't have the required permissions to appoint a seller role", ephemeral=True)
            return
        await interaction.response.defer()
        await self.db.set_seller_role(seller_role.id)
        await interaction.followup.send(f"Seller role set to {seller_role.mention}", ephemeral=True)
    
    @discord.app_commands.command(name="setowner", description="Appoint a owner")
    @discord.app_commands.describe(human="human")
    async def appointSeller(self, interaction: discord.Interaction, human: discord.Member):
        if interaction.user.guild_permissions.administrator == False:
            await interaction.response.send_message("You don't have the required permissions to appoint an owner", ephemeral=True)
            return
        await interaction.response.defer()
        await self.db.add_owner(human.id)
        await interaction.followup.send(f"gigger {human.mention} appointed", ephemeral=True)
    @discord.app_commands.command(name="removeowner", description="Remove a owner")
    @discord.app_commands.describe(human="human")
    async def removeOwner(self, interaction: discord.Interaction, human: discord.Member):
        if interaction.user.guild_permissions.administrator == False:
            await interaction.response.send_message("You don't have the required permissions to appoint a seller role", ephemeral=True)
            return
        await interaction.response.defer()
        await self.db.remove_owner(human.id)
        await interaction.followup.send(f"gigger {human.mention} removed", ephemeral=True)
    @discord.app_commands.command(name="setverified", description="Check if a owner exists")
    @discord.app_commands.describe(role="role")
    async def setverified(self, interaction: discord.Interaction, role: discord.Role):
        if interaction.user.guild_permissions.administrator == False:
            await interaction.response.send_message("You don't have the required permissions to appoint a seller role", ephemeral=True)
            return
        await interaction.response.defer()
        await self.db.set_verified(role.id)
        await interaction.followup.send(f"Verified role set to {role.mention}", ephemeral=True)
    @discord.app_commands.command(name="setlogschannel", description="Check if a owner exists")
    @discord.app_commands.describe(channel="channel")
    async def setlogschannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if interaction.user.guild_permissions.administrator == False:
            await interaction.response.send_message("You don't have the required permissions to appoint a seller role", ephemeral=True)
            return
        await interaction.response.defer()
        await self.db.set_logs_channel(channel.id)
        await interaction.followup.send(f"Logs channel set to {channel.mention}", ephemeral=True)
    @discord.app_commands.command(name="setlistingcategory", description="Check if a owner exists")
    @discord.app_commands.describe(category="category")
    async def setlistingcategory(self, interaction: discord.Interaction, category: str):
        if interaction.user.guild_permissions.administrator == False:
            await interaction.response.send_message("You don't have the required permissions to appoint a seller role", ephemeral=True)
            return
        await interaction.response.defer()
        await self.db.set_listing_catergory(category)
        await interaction.followup.send(f"Listing category set to {category}", ephemeral=True)  
async def setup(bot):
    await bot.add_cog(appointSeller(bot))
    
