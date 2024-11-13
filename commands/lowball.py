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

class lowballCommand(commands.Cog):
    def __init__(self, bot):
        self.get_stats = getStatsForCmd.get_stats
        self.caching = Caching()
        self.bot = bot
    


    @discord.app_commands.command(name="lowball", description="get the lowball value of a specified Skyblock profile")
    @discord.app_commands.describe(username="The username of the player you want to get the lowball value of")
    @discord.app_commands.describe(profile="The profile you want to get the lowball value of")
    async def lowball(self, interaction: discord.Interaction, username: str, profile: str = ""):
        profile = profile.capitalize()
        uuid = await get_uuid(username,)
        if uuid == "error":
            await interaction.response.send_message(f"No UUID found, you sure this is a valid username?")
            return
        await interaction.response.defer()
        try:
            stats = getStatsForCmd()
            stats = await stats.get_stats(username, profile)
            profileName = next(iter(stats.keys()))
            gamemode = f"{stats[profileName]['gameMode']}"
            if gamemode == "Normal":
                title = f"**Lowball for {username} on {profileName}**"
            elif gamemode == "ironman":
                title = f"**Lowball for {username}♻️**"
            else:
                title = f"**Lowball for {username} in {gamemode}**"
            catacombs = f"**{stats['valuation']['lowball']['Catacombs Value']}$**"
            skills = f"**{stats['valuation']['lowball']['skill_value']}$**"
            hotm = f"**{stats['valuation']['lowball']['HOTM Value']}$**"
            total_value = f"**{str(round(float(stats['valuation']['lowball']['total value'].replace(",", "")), 2))}$**"
            slayer = f"**{stats['valuation']['lowball']['Slayer Value']}$**"
            truenw = float(str(stats['valuation']['lowball']['Soulbound Networth']).replace(",", "")) + float(str(stats['valuation']['lowball']['Unsoulbound Networth']).replace(",", "")) - float(str(stats['valuation']['lowball']['Liquid Coins Value']).replace(",", ""))
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
            handle = await a.handle(traceback.format_exc(), "lowball.py")
            embed = discord.Embed(title="Error", color=discord.Color.red(), timestamp=datetime.datetime.now())
            embed.add_field(name="Error", value=f"An error occurred here is the error message:\n```{traceback.format_exc()}```", inline=False)
            embed.set_footer(text="Please report this to Totally_not_toxic (Round)", icon_url="https://cdn.discordapp.com/avatars/895394445195903047/d84af1c3e97bdb221e20f9c5aaad43db.png?size=1024")
            await interaction.followup.send(embed=embed)

        
class DynamicButton(
    discord.ui.DynamicItem[discord.ui.Button],
    template=r'username:(?P<username>[a-zA-Z0-9_]+):profile:(?P<profile>[a-zA-Z0-9]+):usage:(?P<usage>[a-zA-Z0-9]+)',
   
):

    def __init__(self, username: str = "", profile: str = "", usage: str = "")-> None:
        self.user_id = user
        self.username: str = username
        self.profile = profile
        self.usage = usage
        if usage == "":
            label = f"Details for {username}'s lowball"
        elif usage == "listing":
            label = f"View {username}'s lowball"
        stats = getStatsForCmd()
        super().__init__(
            discord.ui.Button(
                label=f"Details for {username}'s lowball",
                style=discord.ButtonStyle.red,
                custom_id=f"username:{username}:profile:{profile}:usage:{usage}"
                #emoji='\N{THUMBS UP SIGN}',
            )
        )

    @classmethod
    async def from_custom_id(cls, interaction: discord.Interaction, item: discord.ui.Button, match: re.Match[str], /):
        username = match['username']
        profile = match['profile']
        usage = match['usage']
        return cls(username, profile, usage)

    
    async def callback(self, interaction: discord.Interaction) -> None:
        try:
            await interaction.response.defer(ephemeral=True)
            self.stats = getStatsForCmd()
            if self.profile == "none":
                stats = await self.stats.get_stats(username=self.username, profile="")
            else:
                stats = await self.stats.get_stats(username=self.username, profile=self.profile)
            username = self.username
            uuid = await get_uuid(username,)
            try:
                stats['valuation']
            except:
                return await interaction.followup.send("No stats found for this user", ephemeral=True)
            lowball = stats['valuation']['lowball']
            profileName = next(iter(stats.keys()))
            gamemode = stats[profileName]['gameMode']
            if gamemode == "Normal":
                title = f"**Lowball for {username}**"
            elif gamemode == "ironman":
                title = f"**Lowball for {username}♻️**"
            else:
                title = f"**Lowball for {username} in {gamemode}**"
            coop = stats[profileName]['members']
            try:
                farming = stats['valuation']['lowball']['Farming']
            except:
                farming = 0
            try:
                foraging = stats['valuation']['lowball']['Foraging']
            except:
                foraging = 0
            try:
                fishing = stats['valuation']['lowball']['Fishing']
            except:
                fishing = 0
            try:
                mining = stats['valuation']['lowball']['Mining']
            except:
                mining = 0
            try:
                combat = stats['valuation']['lowball']['Combat']
            except:
                combat = 0
            try:
                skill_value = stats['valuation']['lowball']['skill_value']
            except:
                skill_value = 0
            try:
                hotm_value = stats['valuation']['lowball']['HOTM Value']
            except:
                hotm_value = 0
            try:
                slayer_value = stats['valuation']['lowball']['Slayer Value']
            except:
                slayer_value = 0
            total_value = f"**Total Value:** {str(round(float(stats['valuation']['lowball']['total value'].replace(",", "")), 2))}$"
            skill = f"""
    Total: **{stats['valuation']['lowball']['skill_value']}$**
    Fishing: **{fishing}$**
    Mining: **{mining}$**
    Combat: **{combat}$**
    Foraging: **{foraging}$**
    Farming: **{farming}$**
            """
            coins = f"""
    Networth total: **{round(float(str(stats['valuation']['lowball']['Soulbound Networth']).replace(",", "")) + float(str(stats['valuation']['lowball']['Unsoulbound Networth']).replace(",", "")) - float(str(stats['valuation']['lowball']['Liquid Coins Value']).replace(",", "")))}$**
    Soulbound: **{stats['valuation']['lowball']['Soulbound Networth']}$**
    Unsoulbound: **{stats['valuation']['lowball']['Unsoulbound Networth']}$**
            """
            catacombs = f"""
    **{stats['valuation']['lowball']['Catacombs Value']}$**
            """
            hotm = f"""
    HOTM total: **{stats['valuation']['lowball']['HOTM Value']}$**
    hotm level: **{stats['valuation']['lowball']['Hotm level value']}$**
    Mithril Powder: **{stats['valuation']['lowball']['mithril']}$**
    Gemstone Powder: **{stats['valuation']['lowball']['gemstone']}$**
            """
            ajustment = f"""
    Coop Ajustment: **x{stats['valuation']['lowball']['adjustment']}** ({coop} Coop members)
    Game Mode Adjustment: **x{stats['valuation']['lowball']['gamemode adjustment']}** (Calculated after accounting for Coop )
            """
            slayer = f"""
    **{stats['valuation']['lowball']['Slayer Value']}$**
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
            handle = await a.handle(traceback.format_exc(), "lowball.py")
            embed = discord.Embed(title="Error", color=discord.Color.red(), timestamp=datetime.datetime.now())
            embed.add_field(name="Error", value=f"An error occurred here is the error message:\n```{traceback.format_exc()}```", inline=False)
            embed.set_footer(text="Please report this to Totally_not_toxic (Round)", icon_url="https://cdn.discordapp.com/avatars/895394445195903047/d84af1c3e97bdb221e20f9c5aaad43db.png?size=1024")
            await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    bot.add_dynamic_items(DynamicButton)
    await bot.add_cog(lowballCommand(bot))
    