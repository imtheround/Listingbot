import discord
from discord.ext import commands

class ExampleCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Explicitly set dm_permission to True
    @discord.app_commands.command(name="dm_example", description="This command works in both DMs and servers!")
    async def dm_example(self, interaction: discord.Interaction):
        await interaction.response.send_message("This command works everywhere, including DMs!")

# Setup function to add the cog to the bot
async def setup(bot: commands.Bot):
    await bot.add_cog(ExampleCog(bot))
