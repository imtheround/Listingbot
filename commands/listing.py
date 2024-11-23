import discord
import re
import datetime
import random
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
        listing_category = discord.utils.get(interaction.guild.categories, id=listing_category)
        if listing_category is None:
            listing_category = discord.utils.get(interaction.guild.categories, id=listing_category)
            if listing_category is None:
                await interaction.followup.send("Something went wrong, either listing category wasn't set or discord isn't working properly. Wait a few minute before retrying.", ephemeral=True)
        try:
            ticket_channel = await listing_category.create_text_channel(
                name=title,
                overwrites={
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    seller_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                }
            )
        except:
            await interaction.followup.send("Something went wrong, either listing category wasn't set or discord isn't working properly. Wait a few minute before retrying.", ephemeral=True)
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
            stats['sucess']
            await interaction.followup.send("Something went wrong, either listing category wasn't set or discord isn't working properly. Wait a few minute before retrying.", ephemeral=True)
        except:
            pass
        profileName = next(iter(stats.keys()))
        lowball = stats[profileName]['valuation']['lowball']
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
            farming = lowball['Farming']
        except:
            farming = 0
        try:
            foraging = lowball['Foraging']
        except:
            foraging = 0
        try:
            fishing = lowball['Fishing']
        except:
            fishing = 0
        try:
            mining = lowball['Mining']
        except:
            mining = 0
        try:
            combat = lowball['Combat']
        except:
            combat = 0
        try:
            skill_value = lowball['skill_value']
        except:
            skill_value = 0
        try:
            hotm_value = lowball['HOTM Value']
        except:
            hotm_value = 0
        try:
            slayer_value = lowball['Slayer Value']
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
        view.add_item(OwnerButton(str(interaction.user.id)))
        view.add_item
        if anonymous == True:
            usagee = "listinganonymous"
        else:
            usagee = "listing"
        if profile != "":
            view.add_item(DynamicButton(username, profile,usagee))
        else:
            view.add_item(DynamicButton(username, "none", usagee))
        await ticket_channel.send(embed=embed, view=view)
        listing = {
            "id": str(random.randint(1000000, 9999999)),
            "ownerid": str(interaction.user.id),
            "channelid": str(ticket_channel.id),
            "username": username,
            "uuid": uuid
        }
        await dbStuff().save_listing(listing)
        embed2 = discord.Embed(
            title="**Listing Successful**",
            description=f"Listed your account in <#{ticket_channel.id}>",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now(),
        )
        await interaction.followup.send(embed=embed2, ephemeral=True)

class unlist(
    discord.ui.DynamicItem[discord.ui.Button],
    template=r'id:(?P<id>[a-zA-Z0-9]+)',
    
):
    def __init__(self, id: str = "")-> None:
        self.owner = id
        self.dbstuff = dbStuff()
        super().__init__(
            discord.ui.Button(
                label="Unlist Owner",
                style=discord.ButtonStyle.blurple,
                custom_id=f"id:{id}",
                emoji='🗑',
            )
        )

    @classmethod
    async def from_custom_id(cls, interaction: discord.Interaction, item: discord.ui.Button, match: re.Match[str], /):
        id = match['id']
        return cls(id)

    
    async def callback(self, interaction: discord.Interaction) -> None:
        channelid = await self.dbstuff.get_listing(self.owner)
        if channelid is None:
            await interaction.response.send_message("No listing found.", ephemeral=True)
            return
        channelid = channelid[0]
        await self.dbstuff.remove_listing(self.owner)
        channel = interaction.guild.get_channel(int(channelid))
        await channel.delete()
class OwnerButton(
    discord.ui.DynamicItem[discord.ui.Button],
    template=r'owner:(?P<owner>[a-zA-Z0-9_]+)',
    
):

    def __init__(self, owner: str = "")-> None:
        self.owner = owner
        super().__init__(
            discord.ui.Button(
                label="Account Owner",
                style=discord.ButtonStyle.blurple,
                custom_id=f"owner:{owner}",
                emoji='👤',
            )
        )

    @classmethod
    async def from_custom_id(cls, interaction: discord.Interaction, item: discord.ui.Button, match: re.Match[str], /):
        owner = match['owner']
        return cls(owner)

    
    async def callback(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(
            title="Account Owner",
            description=f"<@{self.owner}>",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
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
                    discord.SelectOption(label="Slayers", value="Slayers", emoji="<:1236756046098202625:1307528780889329675>"),
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
        view = View(timeout=30)
        view.add_item(Dynamicselect(self.username, self.profile))
        if self.item.values[0] == "Networth":
            stats = await self.stats.get_stats(self.username, self.profile)
            profileName = next(iter(stats.keys()))
            lowval = stats[profileName]['valuation']['lowball']
            gamemode = stats[profileName]['gameMode']
            rank = stats[profileName]['rank'].lower()
            if gamemode == "ironman":
                title=f"Account's networth details on {profileName} ♻️"
            else: 
                title=f"Account's networth details on {profileName}"
            embed = discord.embeds.Embed(
                title=title
            )
            liquide = f"{self.utils.format_large_number(stats[profileName]['liquid'])}\n ↳ Bank: {self.utils.format_large_number(stats[profileName]['bank'])}\n ↳ Purse: {self.utils.format_large_number(stats[profileName]['purse'])}\n ↳ Value: {float(str(lowval['Liquid Coins Value']).replace(",", ""))}$"
            soulbound = f"{self.utils.format_large_number(stats[profileName]['soulboundNetworth'])} ({lowval['Soulbound Networth']}$)"
            unsoulbound = f"{self.utils.format_large_number(stats[profileName]['unsoulboundNetworth'])} ({lowval['Unsoulbound Networth']}$)"
            totalnw = f"{self.utils.format_large_number(float(stats[profileName]['soulboundNetworth']) + float(stats[profileName]['unsoulboundNetworth']))} ({round(float(str(lowval['Soulbound Networth']).replace(",", "")) + float(str(lowval['Unsoulbound Networth']).replace(",", "")) - float(str(stats['valuation']['lowball']['Liquid Coins Value']).replace(",", "")))}$)" 
            embed.add_field(name="**<:1236755419221987328:1306809621549420574> Liquid**", value=liquide)
            embed.add_field(name="**<:1236756044588253184:1306809865318043719> Unsoulbound networth**", value=unsoulbound, inline=False)
            embed.add_field(name="**<:1236756044588253184:1306809865318043719> Soulbound networth**", value=soulbound, inline=False)
            embed.add_field(name="**Total**", value=totalnw)
            await interaction.followup.send(embed=embed, ephemeral=True, view=view)
        if self.item.values[0] == "Skills":
            stats = await self.stats.get_stats(self.username, self.profile)
            lowball = stats['valuation']['lowball']
            profileName = next(iter(stats.keys()))
            gamemode = stats[profileName]['gameMode']
            rank = stats[profileName]['rank'].lower()
            emojis = self.utils.load_emojis()
            if gamemode == "ironman":
                title=f"Account's skills details on {profileName} ♻️"
            else: 
                title=f"Account's skills details on {profileName}"
            embed = discord.embeds.Embed(
                title=title
            )
            progression = calculate_skill_progression(stats[profileName]['skills'])
            for key, value in progression.items():
                if key == "avg" or key == "Social" or key == "Runecrafting":
                    continue
                worth = stats[profileName]['valuation']['lowball'][key]
                embed.add_field(name=f"{emojis[key]} {key}", value=f"{value}% to max level - value: {worth}$", inline=False)
            await interaction.followup.send(embed=embed, ephemeral=True, view=view)
        if self.item.values[0] == "Slayers":
            stats = await self.stats.get_stats(self.username, self.profile)
            profileName = next(iter(stats.keys()))
            gamemode = stats[profileName]['gameMode']
            if gamemode == "ironman":
                title=f"Account's skills details on {profileName} ♻️"
            else: 
                title=f"Account's skills details on {profileName}"
            slayer = f"{stats[profileName]['slayers']['zombie']}/{stats[profileName]['slayers']['spider']}/{stats[profileName]['slayers']['wolf']}/{stats[profileName]['slayers']['enderman']}/{stats[profileName]['slayers']['blaze']}/{stats[profileName]['slayers']['vampire']} "
            embed = discord.Embed(
                title=title,
                color=discord.Color.green(),
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="**Revenant Horror**", value=f"Level: {stats[profileName]['slayers']['zombie']}", inline=False)
            embed.add_field(name="**Tarantula Broodmother**", value=f"Level: {stats[profileName]['slayers']['spider']}", inline=False)
            embed.add_field(name="**Sven Packmaster**", value=f"Level: {stats[profileName]['slayers']['wolf']}", inline=False)
            embed.add_field(name="**Voidgloom Seraphr**", value=f"Level: {stats[profileName]['slayers']['enderman']}", inline=False)
            embed.add_field(name="**Inferno Demonlord**", value=f"Level: {stats[profileName]['slayers']['blaze']}", inline=False)
            embed.add_field(name="**Riftstalker Bloodfiend**", value=f"Level: {stats[profileName]['slayers']['vampire']}", inline=False)
            embed.set_footer(text="Yes I didnt't include emojis :D")
            await interaction.followup.send(embed=embed, ephemeral=True, view=view)
def calculate_skill_progression(player_levels):
    exp = {
        0: 0, 1: 50, 2: 175, 3: 375, 4: 675, 5: 1175, 6: 1925, 7: 2925, 8: 4425, 9: 6425,
        10: 9925, 11: 14925, 12: 22425, 13: 32425, 14: 47425, 15: 67425, 16: 97425,
        17: 147425, 18: 222425, 19: 322425, 20: 522425, 21: 822425, 22: 1222425,
        23: 1722425, 24: 2322425, 25: 3022425, 26: 3822425, 27: 4722425, 28: 5722425,
        29: 6822425, 30: 8022425, 31: 9322425, 32: 10722425, 33: 12222425, 34: 13822425,
        35: 15522425, 36: 17322425, 37: 19222425, 38: 21222425, 39: 23322425, 40: 25522425,
        41: 27822425, 42: 30222425, 43: 32722425, 44: 35322425, 45: 38072425, 46: 40972425,
        47: 44072425, 48: 47472425, 49: 51172425, 50: 55172425
    }
    max_level_dict = {
        "Fishing": 50,
        "Mining": 60,
        "Combat": 60,
        "Foraging": 50,
        "Taming": 51,
        "Enchanting": 60,
        "Alchemy": 50,
        "Carpentry": 50,
        "Runecrafting": 25,
        "Farming": 50,
    }
    def scale_exp_dict(base_exp, target_max_level):
        base_max_level = max(base_exp.keys())
        scaled_exp = {}
        for level in range(target_max_level + 1):
            scaled_level = level * base_max_level / target_max_level
            lower_level = int(scaled_level)
            upper_level = min(lower_level + 1, base_max_level)
            if lower_level == upper_level:
                scaled_exp[level] = base_exp[lower_level]
            else:
                fraction = scaled_level - lower_level
                exp = base_exp[lower_level] + fraction * (base_exp[upper_level] - base_exp[lower_level])
                scaled_exp[level] = int(exp)
        return scaled_exp

    exp_dicts = {
        skill: scale_exp_dict(exp, max_level)
        for skill, max_level in max_level_dict.items()
    }
    progression = {}
    for skill, level in player_levels.items():
        if skill in exp_dicts:
            exp_dict = exp_dicts[skill]
            max_level = max(exp_dict.keys())
            max_exp = exp_dict[max_level]
            current_exp = exp_dict.get(level, 0)

    return progression


async def setup(bot: commands.Bot):
    await bot.add_cog(Listing(bot))
