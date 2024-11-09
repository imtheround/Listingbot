import asyncio
import os
import discord
from discord.ext import commands
from discord import *
import requests
import os
import json
import sys
import json
import re
import traceback
import datetime

from discord.ui import Button, View, Modal, TextInput
from requests.exceptions import URLRequired
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
from utils.getStatsForCmd import getStatsForCmd
from utils.caching import Caching
from utils.getProfile import get_profile
from utils.generalUtils import handleError
from utils.getUuid import get_uuid
from utils.fetchStats import fetchNetworth

class valueCommand(commands.Cog):
    def __init__(self, bot):
        self.get_stats = getStatsForCmd.get_stats
        self.caching = Caching()
        self.bot = bot
    


    @discord.app_commands.command(name="value", description="get the value value of a specified Skyblock profile")
    @discord.app_commands.describe(username="The username of the player you want to get the value value of")
    @discord.app_commands.describe(profile="The profile you want to get the value value of")
    async def value(self, interaction: discord.Interaction, username: str, profile: str = ""):
        profile = profile.capitalize()
        uuid = await get_uuid(username,)
        if uuid == "error":
            await interaction.response.send_message(f"No UUID found, you sure this is a valid username?", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        try:
            stats = getStatsForCmd()
            stats = await stats.get_stats(username, profile)
            profileName = next(iter(stats.keys()))
            gamemode = f"{stats[profileName]['gameMode']}"
            if gamemode == "Normal":
                title = f"**Value for {username} on {profileName}**"
            elif gamemode == "ironman":
                title = f"**Value for {username}♻️**"
            else:
                title = f"**Value for {username} in {gamemode}**"
            catacombs = f"**{stats['valuation']['value']['Catacombs Value']}$**"
            skills = f"**{stats['valuation']['value']['skill_value']}$**"
            hotm = f"**{stats['valuation']['value']['HOTM Value']}$**"
            total_value = f"**{str(round(float(stats['valuation']['value']['total value'].replace(",", "")), 2))}$**"
            slayer = f"**{stats['valuation']['value']['Slayer Value']}$**"
            truenw = float(str(stats['valuation']['value']['Soulbound Networth']).replace(",", "")) + float(str(stats['valuation']['value']['Unsoulbound Networth']).replace(",", "")) - float(str(stats['valuation']['value']['Liquid Coins Value']).replace(",", ""))
            networth = f"**{round(truenw, 2)}$**"
            view = View(timeout=60)
            if profile != "":
                view.add_item(DynamicButton(username, profile))
            else:
                view.add_item(DynamicButton(username=username, profile="none"))
            embed = discord.Embed(
                title=title,
                color=discord.Color.pink(),
                timestamp=datetime.datetime.now()
            )
            embed.url = f"https://sky.shiiyu.moe/stats/{uuid}"
            embed.add_field(name="**Skills:**", value=skills, inline=False)
            embed.add_field(name="**Networth:**", value=networth, inline=False)
            embed.add_field(name="**HOTM:**", value=hotm, inline=False)
            embed.add_field(name="**Slayers:**", value=slayer, inline=False)
            embed.add_field(name="**Catacombs:**", value=catacombs, inline=False)
            embed.add_field(name="**Total Value:**", value=total_value, inline=False)
            embed.set_thumbnail(url=f"https://mc-heads.net/body/{uuid}/left")
            embed.set_footer(text="Made by Totally_not_toxic (Round) with ♡", icon_url="https://cdn.discordapp.com/avatars/895394445195903047/d84af1c3e97bdb221e20f9c5aaad43db.png?size=1024")
            await interaction.followup.send(embed=embed, view=view)
        except Exception as e:
            a = handleError()
            handle = await a.handle(traceback.format_exc(), "Value.py")
            embed = discord.Embed(title="Error", color=discord.Color.red(), timestamp=datetime.datetime.now())
            embed.add_field(name="Error", value=f"An error occurred here is the error message:\n```{traceback.format_exc()}```", inline=False)
            embed.set_footer(text="Please report this to Totally_not_toxic (Round)", icon_url="https://cdn.discordapp.com/avatars/895394445195903047/d84af1c3e97bdb221e20f9c5aaad43db.png?size=1024")
            await interaction.followup.send(embed=embed, ephemeral=True)

        
class DynamicButton(
    discord.ui.DynamicItem[discord.ui.Button],
    template=r'username:(?P<username>[a-zA-Z0-9_]+):profile:(?P<profile>[a-zA-Z0-9]+)',
   
):

    def __init__(self, username: str = "", profile: str = "")-> None:
        self.user_id = user
        self.username: str = username
        self.profile = profile
        stats = getStatsForCmd()
        super().__init__(
            discord.ui.Button(
                label=f"Details for {username}'s Value",
                style=discord.ButtonStyle.primary,
                custom_id=f"username:{username}:profile:{profile}"
                #emoji='\N{THUMBS UP SIGN}',
            )
        )

    @classmethod
    async def from_custom_id(cls, interaction: discord.Interaction, item: discord.ui.Button, match: re.Match[str], /):
        username = match['username']
        profile = match['profile']
        return cls(username, profile)

    
    async def callback(self, interaction: discord.Interaction) -> None:
        try:
            await interaction.response.defer(ephemeral=True)
            self.stats = getStatsForCmd()
            if self.profile == "none":
                stats = await self.stats.get_stats(username=self.username, profile="")
            else:
                stats = await self.stats.get_stats(username=self.username, profile=self.profile)
            stats = await self.stats.get_stats(username=self.username)
            username = self.username
            uuid = await get_uuid(username,)
            try:
                stats['valuation']
            except:
                return await interaction.followup.send("No stats found for this user", ephemeral=True)
            value = stats['valuation']['value']
            profileName = next(iter(stats.keys()))
            gamemode = stats[profileName]['gameMode']
            if gamemode == "Normal":
                title = f"**Value for {username}**"
            elif gamemode == "ironman":
                title = f"**Value for {username}♻️**"
            else:
                title = f"**Value for {username} in {gamemode}**"
            coop = stats[profileName]['members']
            try:
                farming = stats['valuation']['value']['Farming']
            except:
                farming = 0
            try:
                foraging = stats['valuation']['value']['Foraging']
            except:
                foraging = 0
            try:
                fishing = stats['valuation']['value']['Fishing']
            except:
                fishing = 0
            try:
                mining = stats['valuation']['value']['Mining']
            except:
                mining = 0
            try:
                combat = stats['valuation']['value']['Combat']
            except:
                combat = 0
            try:
                skill_value = stats['valuation']['value']['skill_value']
            except:
                skill_value = 0
            try:
                hotm_value = stats['valuation']['value']['HOTM Value']
            except:
                hotm_value = 0
            try:
                slayer_value = stats['valuation']['value']['Slayer Value']
            except:
                slayer_value = 0
            total_value = f"**Total Value:** {str(round(float(stats['valuation']['value']['total value'].replace(",", "")), 2))}$"
            skill = f"""
    Total: **{stats['valuation']['value']['skill_value']}$**
    Fishing: **{fishing}$**
    Mining: **{mining}$**
    Combat: **{combat}$**
    Foraging: **{foraging}$**
    Farming: **{farming}$**
            """
            coins = f"""
    Networth total: **{round(float(str(stats['valuation']['value']['Soulbound Networth']).replace(",", "")) + float(str(stats['valuation']['value']['Unsoulbound Networth']).replace(",", "")) - float(str(stats['valuation']['value']['Liquid Coins Value']).replace(",", "")))}$**
    Soulbound: **{stats['valuation']['value']['Soulbound Networth']}$**
    Unsoulbound: **{stats['valuation']['value']['Unsoulbound Networth']}$**
            """
            catacombs = f"""
    **{stats['valuation']['value']['Catacombs Value']}$**
            """
            hotm = f"""
    HOTM total: **{stats['valuation']['value']['HOTM Value']}$**
    hotm level: **{stats['valuation']['value']['Hotm level value']}$**
    Mithril Powder: **{stats['valuation']['value']['mithril']}$**
    Gemstone Powder: **{stats['valuation']['value']['gemstone']}$**
            """
            ajustment = f"""
    Coop Ajustment: **x{stats['valuation']['value']['adjustment']}** ({coop} Coop members)
    Game Mode Adjustment: **x{stats['valuation']['value']['gamemode adjustment']}** (Calculated after accounting for Coop )
            """
            slayer = f"""
    **{stats['valuation']['value']['Slayer Value']}$**
            """
            embed = discord.Embed(title=title, color=discord.Color.green(), timestamp=datetime.datetime.now())
            embed.url = f"https://sky.shiiyu.moe/stats/{uuid}"
            embed.add_field(name="", value=total_value, inline=False)
            embed.add_field(name="**Skills:**", value=skill, inline=True)
            embed.add_field(name="**Networth:**", value=coins, inline=True)
            embed.add_field(name="**HOTM:**", value=hotm, inline=True)
            embed.add_field(name="**Slayers:**", value=slayer, inline=True)
            embed.add_field(name="**Catacombs:**", value=catacombs, inline=True)
            embed.add_field(name="**Adjustments:**", value=ajustment, inline=False)
            embed.set_thumbnail(url=f"https://mc-heads.net/body/{uuid}/left")
            embed.set_footer(text="Made by Totally_not_toxic (Round) with ♡", icon_url="https://cdn.discordapp.com/avatars/895394445195903047/d84af1c3e97bdb221e20f9c5aaad43db.png?size=1024")
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            a = handleError()
            handle = await a.handle(traceback.format_exc(), "value.py")
            embed = discord.Embed(title="Error", color=discord.Color.red(), timestamp=datetime.datetime.now())
            embed.add_field(name="Error", value=f"An error occurred here is the error message:\n```{traceback.format_exc()}```", inline=False)
            embed.set_footer(text="Please report this to Totally_not_toxic (Round)", icon_url="https://cdn.discordapp.com/avatars/895394445195903047/d84af1c3e97bdb221e20f9c5aaad43db.png?size=1024")
            await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    bot.add_dynamic_items(DynamicButton)
    await bot.add_cog(valueCommand(bot))
    