import discord
from discord.ext import commands

class ExampleCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name="ads", description="Skibidi toilet legit")
    async def dm_example(self, interaction: discord.Interaction):
        if interaction.user.id != 895394445195903047:
            await interaction.response.send_message("abrakadabra", ephemeral=True)
            return
        await interaction.response.send_message("# https://discord.gg/uuid")
    @discord.app_commands.command(name="ltc", description="Skibidi toilet legit")
    async def ltc(self, interaction: discord.Interaction):
        if interaction.user.id != 895394445195903047:
            await interaction.response.send_message("abrakadabra", ephemeral=True)
            return
        embed = discord.Embed(
            title="Round's ltc wallet",
            description="`LWWFqe6RkmrMhz3oqGe4C9AmUHy6x6W8Dm`",
        )
        embed.set_footer(text="Send txid or sum after sent ty")
        await interaction.response.send_message(embed=embed)
        
async def setup(bot: commands.Bot):
    await bot.add_cog(ExampleCog(bot))
