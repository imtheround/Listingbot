import discord
from discord.ext import commands

class ExampleCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name="ads", description="This command works in both DMs and servers!")
    async def dm_example(self, interaction: discord.Interaction):
        if interaction.user.id != 895394445195903047:
            await interaction.response.send_message("abrakadabra", ephemeral=True)
            return
        await interaction.response.send_message("# https://discord.gg/uuid")

async def setup(bot: commands.Bot):
    await bot.add_cog(ExampleCog(bot))
