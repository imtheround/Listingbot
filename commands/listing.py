import discord
import re
import datetime
from discord.ui import Button, View, Modal, TextInput
from discord.ext import commands
from requests.api import options
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
    async def listing(self, interaction: discord.Interaction, username: str,profile: str = "none",price: int  = 0, payment_method: str = "", anonymous: bool = True, star: bool = False, extra_info: str = ""):
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
        elif interaction.user.guild_permissions.administrator == True:
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
        print(listing_category)
        listing_category = discord.utils.get(interaction.guild.categories, id=listing_category)
        if listing_category is None:
            listing_category = discord.utils.get(interaction.guild.categories, id=listing_category)
            if listing_category is None:
                await interaction.followup.send("Something went wrong, either listing category wasn't set or discord isn't working properly. Wait a few minute before retrying.")
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
        rank = stats[profileName]['rank'].lower()
        if rank == "vip":
            rank = "<:1236748763150684252:1307516197415419964><:1236748822726840411:1306809827690938368>"
        elif rank == "vip+":
            rank = "<:1236748763150684252:1307516197415419964><:1236748767403708448:1307516196488351767>"
        elif rank == "mvp":
            rank = "<:1236748751218020393:1307516207380828221> <:1236748752652472421:1307516267422421115>"
        elif rank == "mvp+":
            rank = "<:1236748751218020393:1307516207380828221><:1236748754158092378:1307516204704862228>"
        elif rank == "youtuber":
            rank = "<:1236748769920553122:1307516014006898768><:1236748772831264899:1307516012454744115><:1236748821275611186:1307516010651193364>"
        elif rank == "None":
            rank="<:1236748760353341472:1307516199936069663><:1236748762131726537:1306809670924505159>"
        else:
            rank = "<:1236748755986940065:1307516203186655324><:1236748757597683753:1307516202108583956><:1236748758679814305:1306809642810081311>"
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
        hotm = f"Hotm level: {stats[profileName]['hotm']['HotmLevel']}\nGemstone Powder: {self.utils.format_large_number(float(stats[profileName]['hotm']['gemstonePowder']))}\nMithril Powder: {self.utils.format_large_number(float(stats[profileName]['hotm']['mithrilPowder']))}"
        embed.add_field(name="**Rank**", value=f"{rank}", inline=False)
        embed.add_field(name="**<:1236755617918619751:1307515820284313629> Skyblock Level**", value=f"{sblvl}", inline=True)
        embed.add_field(name="**<:1236755374254850099:1306809891767189616> Skill Average**", value=f"{skill_average}")
        embed.add_field(name="**<:1236756046098202625:1307528780889329675> Slayers**", value=f"{slayer}", inline=False)
        embed.add_field(name="**<:1236755555775807609:1307527942062084218> Catacombs**", value=f"{catacombs}", inline=False)
        embed.add_field(name="**<:1236756044588253184:1306809865318043719> Networth**", value=f"{networth}", inline=False)
        embed.add_field(name="**<:1236755608494149735:1307528085876375662> Hotm**", value=f"{hotm}")
        embed.add_field(name="**💸 Price**", value=f"{price}", inline=False)
        if extra_info:
            embed.add_field(name="**❗ Extra Info**", value=f"{extra_info}", inline=False)
        if payment_method:
            embed.add_field(name="**<:1236755419221987328:1306809621549420574> Payment Method**", value=f"{payment_method}", inline=True)
        if anonymous == True:
            embed.set_thumbnail(url=f"https://mc-heads.net/body/anonymous/left")
        else:
            embed.set_thumbnail(url=f"https://mc-heads.net/body/{uuid}/left")
        embed.set_footer(text="Made by Totally_not_toxic (Round) with ♡", icon_url="https://cdn.discordapp.com/avatars/895394445195903047/d84af1c3e97bdb221e20f9c5aaad43db.png?size=1024")
        view = View(timeout=None)
        view.add_item(Dynamicselect(username, profile))
        if anonymous == True:
            usagee = "listinganonymous"
        else:
            usagee = "listing"
        if profile != "":
            view.add_item(DynamicButton(username, profile,usagee))
        else:
            view.add_item(DynamicButton(username, "none", usagee))
        await ticket_channel.send(embed=embed, view=view)
        embed2 = discord.Embed(
            title="**Listing Successful**",
            description=f"Listed your account in <#{ticket_channel.id}>",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now(),
        )
        await interaction.followup.send(embed=embed2, ephemeral=True)
        
        
        

class Dynamicselect(
    discord.ui.DynamicItem[discord.ui.Select],
    template=r'username:(?P<username>[a-zA-Z0-9_]+):profile:(?P<profile>[a-zA-Z0-9]+)',
):

    def __init__(self, username: str = "", profile: str = "none", usage: str = "")-> None:
        self.username: str = username
        self.profile = profile
        self.stats = getStatsForCmd()
        self.utils = handleError()
        super().__init__(
            discord.ui.Select(
                options=[
                    discord.SelectOption(label="Networth", value="Networth", emoji="<:1236756044588253184:1306809865318043719>"),
                    discord.SelectOption(label="Skills", emoji="<:1236755374254850099:1306809891767189616>", value="Skills"),
                    discord.SelectOption(label="Mining", value="Mining", emoji="<:1236755797048823943:1306809794744815677>"),
                ],
                placeholder="Stats breakdown",
                max_values=1,
                min_values=1,
                custom_id=f"username:{username}:profile:{profile}"
            )
        )

    @classmethod
    async def from_custom_id(cls, interaction: discord.Interaction, item: discord.ui.Select, match: re.Match[str], /):
        username = match['username']
        profile = match['profile']
        return cls(username, profile)
    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        if self.item.values[0] == "Networth":
            stats = await self.stats.get_stats(self.username, self.profile)
            lowball = stats['valuation']['lowball']
            profileName = next(iter(stats.keys()))
            gamemode = stats[profileName]['gameMode']
            rank = stats[profileName]['rank'].lower()
            if gamemode == "ironman":
                title=f"Account's networth details on {profileName} ♻️"
            else: 
                title=f"Account's networth details on {profileName}"
            embed = discord.embeds.Embed(
                title=title
            )
            liquide = f"{self.utils.format_large_number(stats[profileName]['liquid'])}\n -> Bank: {self.utils.format_large_number(stats[profileName]['bank'])}\n -> Purse: {self.utils.format_large_number(stats[profileName]['purse'])}\n -> Value: {float(str(stats['valuation']['lowball']['Liquid Coins Value']).replace(",", ""))}$"
            soulbound = f"{self.utils.format_large_number(stats[profileName]['soulboundNetworth'])} ({stats['valuation']['lowball']['Soulbound Networth']}$)"
            unsoulbound = f"{self.utils.format_large_number(stats[profileName]['unsoulboundNetworth'])} ({stats['valuation']['lowball']['Unsoulbound Networth']}$)"
            totalnw = f"{self.utils.format_large_number(float(stats[profileName]['soulboundNetworth']) + float(stats[profileName]['unsoulboundNetworth']))} ({round(float(str(stats['valuation']['lowball']['Soulbound Networth']).replace(",", "")) + float(str(stats['valuation']['lowball']['Unsoulbound Networth']).replace(",", "")) - float(str(stats['valuation']['lowball']['Liquid Coins Value']).replace(",", "")))}$)" 
            embed.add_field(name="**<:1236755419221987328:1306809621549420574> Liquid**", value=liquide)
            embed.add_field(name="**<:1236756044588253184:1306809865318043719> Unsoulbound networth**", value=unsoulbound, inline=False)
            embed.add_field(name="**<:1236756044588253184:1306809865318043719> Soulbound networth**", value=soulbound, inline=False)
            embed.add_field(name="**Total**", value=totalnw)
            await interaction.followup.send(embed=embed, ephemeral=True)
        if self.item.values[0] == "Skills":
            stats = await self.stats.get_stats(self.username, self.profile)
            lowball = stats['valuation']['lowball']
            profileName = next(iter(stats.keys()))
            gamemode = stats[profileName]['gameMode']
            rank = stats[profileName]['rank'].lower()
            if gamemode == "ironman":
                title=f"Account's skills details on {profileName} ♻️"
            else: 
                title=f"Account's skills details on {profileName}"
            embed = discord.embeds.Embed(
                title=title
            )
        if self.item.values[0] == "Mining":
            await interaction.response.send_message("Mining", ephemeral=True)
async def setup(bot: commands.Bot):
    await bot.add_cog(Listing(bot))
