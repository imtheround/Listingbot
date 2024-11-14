import discord
import datetime
from discord.ui import Button, View, Modal, TextInput
from discord.ext import commands
from db.dbStuff import dbStuff
from utils.caching import Caching
from utils.getStatsForCmd import getStatsForCmd
from utils.getUuid import get_uuid
from utils.generalUtils import handleError
from commands.lowball import DynamicButton
class Listing(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = dbStuff()
        self.utils = handleError()
    @discord.app_commands.command(name="list", description="Mieow")
    @discord.app_commands.describe(username="username")
    @discord.app_commands.describe(profile="profile")
    @discord.app_commands.describe(price="price")
    @discord.app_commands.describe(payment_method="payment method")
    @discord.app_commands.describe(anonymous="show username or not")
    @discord.app_commands.describe(star = "star?")
    @discord.app_commands.describe(extra_info="extra info?")
    async def listing(self, interaction: discord.Interaction, username: str,profile: str = "",price: int  = 0, payment_method: str = "", anonymous: bool = True, star: bool = False, extra_info: str = ""):
        await interaction.response.defer()
        cache = Caching().load_cache()
        guild = interaction.guild
        try:
            seller_role = discord.utils.get(interaction.guild.roles, id=cache["seller_role"])
        except:
            a = await self.db.get_seller_role()
            a = int(a[0])
            cache["seller_role"] = a
            Caching().save_cache("seller_role",cache)
            seller_role = discord.utils.get(interaction.guild.roles, id=a)
        if seller_role in interaction.user.roles:
            pass
        else:
            await interaction.followup.send(f"Not sigma enough fr", ephemeral=True)
            return
        listing_category = await self.db.get_listing_category()
        if listing_category is None:
            await interaction.followup.send(f"No listing category set", ephemeral=True)
            return
        if anonymous == True:
            title = f"💲{str(price)}｜account"
        else:
            title = f"💲{str(price)}｜{username}"
        if star == True:
            title = f"⭐{title}"
        listing_category = int(listing_category[0][0])
        listing_category = discord.utils.get(interaction.guild.categories, id=listing_category)
        ticket_channel = await listing_category.create_text_channel(
            name=title,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                seller_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            }
        )
        self.username = username
        self.profile = profile
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
        rank = stats[profileName]['rank']
        if anonymous == True:
            title = f"**Account information**"
        else:
            title = f"**{username}'s information**"
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
        
        embed = discord.Embed(title=title, color=discord.Color.green(), timestamp=datetime.datetime.now())
        if anonymous == True:
            embed.url = f"https://sky.shiiyu.moe/stats/refraction"
        else:
            embed.url = f"https://sky.shiiyu.moe/stats/{uuid}"
        skill_average = stats[profileName]['skills']['avg']
        sblvl = stats[profileName]['levels']
        classaverage = str(round((int(stats[profileName]['catacombs']['archer']) + int(stats[profileName]['catacombs']['mage'])+ int(stats[profileName]['catacombs']['berserk'])+ int(stats[profileName]['catacombs']['tank'])+ int(stats[profileName]['catacombs']['healer']))/5, 2))
        catacombs = f"Level: {stats[profileName]['catacombs']['level']}\nClass Average: {classaverage}"
        slayer = f"{stats[profileName]['slayers']['zombie']}/{stats[profileName]['slayers']['spider']}/{stats[profileName]['slayers']['wolf']}/{stats[profileName]['slayers']['enderman']}/{stats[profileName]['slayers']['blaze']}/{stats[profileName]['slayers']['vampire']} "
        networth = f"{self.utils.format_large_number(stats[profileName]['networth'])} (Soulbound: {self.utils.format_large_number(stats[profileName]['soulboundNetworth'])}) - Liquid: {self.utils.format_large_number(stats[profileName]['liquid'])}"
        hotm = f"Hotm level: {stats[profileName]['hotm']['HotmLevel']}\nGemstone Powder: {stats[profileName]['hotm']['gemstonePowder']}\nMithril Powder: {stats[profileName]['hotm']['mithrilPowder']}"
        embed.add_field(name="**Rank**", value=f"{rank}")
        embed.add_field(name="**Skyblock Level**", value=f"{sblvl}", inline=False)
        embed.add_field(name="**Skill Average**", value=f"{skill_average}")
        embed.add_field(name="**Slayers**", value=f"{slayer}")
        embed.add_field(name="**Catacombs**", value=f"{catacombs}")
        embed.add_field(name="**Networth**", value=f"{networth}", inline=False)
        embed.add_field(name="**Hotm**", value=f"{hotm}")
        embed.add_field(name="**Price**", value=f"{price}", inline=False)
        if extra_info:
            embed.add_field(name="**Extra Info**", value=f"{extra_info}")
        if payment_method:
            embed.add_field(name="**Payment Method**", value=f"{payment_method}")
        if anonymous == True:
            embed.set_thumbnail(url=f"https://mc-heads.net/body/anonymous/left")
        else:
            embed.set_thumbnail(url=f"https://mc-heads.net/body/{uuid}/left")
        embed.set_footer(text="Made by Totally_not_toxic (Round) with ♡", icon_url="https://cdn.discordapp.com/avatars/895394445195903047/d84af1c3e97bdb221e20f9c5aaad43db.png?size=1024")
        view = View(timeout=60)
        if profile != "":
            view.add_item(DynamicButton(username, profile, "listing"))
        else:
            view.add_item(DynamicButton(username=username, profile="none", usage="listing"))
        await ticket_channel.send(embed=embed, view=view)
        embed2 = discord.Embed(
            title="**Listing Successful**",
            description=f"Listed your account in <#{ticket_channel.id}>",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now(),
        )
        await interaction.followup.send(embed=embed2, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Listing(bot))
