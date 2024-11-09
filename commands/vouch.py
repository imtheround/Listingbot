# roxco made dis (need to redo/revamp)
import discord
from discord.ext import commands
from discord import app_commands
import os
import sqlite3

class Vouch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Load vouch channel ID, customer role ID, and admin role ID from environment or default to None
        self.vouch_channel_id = int(os.getenv("VOUCH_CHANNEL_ID", "0"))
        self.customer_role_id = int(os.getenv("CUSTOMER_ROLE_ID", "0"))
        self.admin_role_id = int(os.getenv("ADMIN_ROLE_ID", "0"))
        self.deal_tracker_channel_id = None  # This will be set by the command

        # Connect to (or create) the SQLite database
        self.conn = sqlite3.connect("vouches.db")
        self.cursor = self.conn.cursor()
        
        # Create the vouches table if it doesn't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vouches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vouched_by TEXT,
                seller TEXT,
                amount REAL,
                timestamp TEXT
            )
        """)
        self.conn.commit()

    @app_commands.command(name="setvouchchannel", description="Set the channel for vouches (Admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_vouch_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Slash command to set the channel for vouches."""
        self.vouch_channel_id = channel.id
        await interaction.response.send_message(f"Vouch channel set to {channel.mention}", ephemeral=True)
        await self.update_vouch_channel_name()  # Update channel name when setting

    @app_commands.command(name="setcustomerrole", description="Set the Customer role required for vouching (Admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_customer_role(self, interaction: discord.Interaction, role: discord.Role):
        """Slash command to set the Customer role."""
        self.customer_role_id = role.id
        await interaction.response.send_message(f"Customer role set to {role.mention}", ephemeral=True)

    @app_commands.command(name="setadminrole", description="Set the Admin role required for retrieving vouches (Admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_admin_role(self, interaction: discord.Interaction, role: discord.Role):
        """Slash command to set the Admin role."""
        self.admin_role_id = role.id
        await interaction.response.send_message(f"Admin role set to {role.mention}", ephemeral=True)

    @app_commands.command(name="setdealtrackerchannel", description="Set the voice channel for tracking deal amounts (Admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_deal_tracker_channel(self, interaction: discord.Interaction, channel: discord.VoiceChannel):
        """Command to set the voice channel for tracking the total deal amount."""
        self.deal_tracker_channel_id = channel.id
        await interaction.response.send_message(f"Deal tracker channel set to {channel.mention}", ephemeral=True)
        await self.update_deal_tracker_channel_name()  # Update immediately if any deals exist

    async def update_deal_tracker_channel_name(self):
        """Update the voice channel name with the total deal amount."""
        if not self.deal_tracker_channel_id:
            return

        # Calculate the total amount of all vouches
        self.cursor.execute("SELECT SUM(amount) FROM vouches")
        total_amount = self.cursor.fetchone()[0] or 0.0
        
        # Update the channel name with the total amount
        deal_tracker_channel = self.bot.get_channel(self.deal_tracker_channel_id)
        if deal_tracker_channel:
            new_name = f"💲｜{total_amount:.2f} dealt with"
            await deal_tracker_channel.edit(name=new_name)

    @app_commands.command(name="vouch", description="Vouch for a seller")
    async def vouch(self, interaction: discord.Interaction, seller: discord.User, amount: float):
        """Vouch command allowing only users with the Customer role to vouch."""
        if not self.vouch_channel_id or not self.customer_role_id:
            await interaction.response.send_message(
                "The vouch channel or Customer role is not set. Please contact an admin.", ephemeral=True
            )
            return

        # Check if the user has the Customer role
        customer_role = discord.utils.get(interaction.guild.roles, id=self.customer_role_id)
        if customer_role not in interaction.user.roles:
            await interaction.response.send_message(
                "You must have the Customer role to use this command.", ephemeral=True
            )
            return

        # Send vouch message to the vouch channel
        vouch_channel = self.bot.get_channel(self.vouch_channel_id)
        if not vouch_channel:
            await interaction.response.send_message(
                "The specified vouch channel does not exist. Please contact an admin.", ephemeral=True
            )
            return

        # Create the embed
        embed = discord.Embed(
            title="Vouch",
            color=discord.Color.green()
        )
        embed.add_field(name="Vouched By", value=interaction.user.mention, inline=False)
        embed.add_field(name="Seller", value=seller.mention, inline=False)
        embed.add_field(name="Amount", value=f"${amount:.2f}", inline=False)
        embed.set_footer(text=f"Vouched by {interaction.user}", icon_url=interaction.user.avatar.url)

        await vouch_channel.send(embed=embed)
        await interaction.response.send_message("Your vouch has been recorded.", ephemeral=True)

        # Save vouch to the database
        self.cursor.execute(
            "INSERT INTO vouches (vouched_by, seller, amount, timestamp) VALUES (?, ?, ?, datetime('now'))",
            (str(interaction.user), str(seller), amount)
        )
        self.conn.commit()

        # Update the vouch channel name with the new vouch count
        await self.update_vouch_channel_name()

        # Update deal tracker channel with the new total amount
        await self.update_deal_tracker_channel_name()

    @app_commands.command(name="retrievevouches", description="Retrieve all vouches (Admin only)")
    async def retrieve_vouches(self, interaction: discord.Interaction):
        """Command to retrieve all vouches, restricted to users with the specified admin role."""
        if not self.admin_role_id:
            await interaction.response.send_message("Admin role is not set. Please contact an admin.", ephemeral=True)
            return

        # Check if the user has the Admin role
        admin_role = discord.utils.get(interaction.guild.roles, id=self.admin_role_id)
        if admin_role not in interaction.user.roles:
            await interaction.response.send_message(
                "You do not have the required role to use this command.", ephemeral=True
            )
            return

        # Fetch all vouches from the database
        self.cursor.execute("SELECT vouched_by, seller, amount, timestamp FROM vouches")
        vouches = self.cursor.fetchall()

        if not vouches:
            await interaction.response.send_message("No vouches found in the database.", ephemeral=True)
            return

        # Send each vouch as an embed
        for vouched_by, seller, amount, timestamp in vouches:
            embed = discord.Embed(title="Vouch Record", color=discord.Color.blue())
            embed.add_field(name="Vouched By", value=vouched_by, inline=False)
            embed.add_field(name="Seller", value=seller, inline=False)
            embed.add_field(name="Amount", value=f"${amount:.2f}", inline=False)
            embed.add_field(name="Timestamp", value=timestamp, inline=False)
            await interaction.channel.send(embed=embed)

        await interaction.response.send_message("All vouches have been retrieved.", ephemeral=True)

    async def update_vouch_channel_name(self):
        """Updates the vouch channel name to include the current vouch count."""
        if not self.vouch_channel_id:
            return
        
        # Count vouches in the database
        self.cursor.execute("SELECT COUNT(*) FROM vouches")
        vouch_count = self.cursor.fetchone()[0]
        
        # Update the channel name
        vouch_channel = self.bot.get_channel(self.vouch_channel_id)
        if vouch_channel:
            new_name = f"✅｜{vouch_count}｜vouches"
            await vouch_channel.edit(name=new_name)

async def setup(bot):
    await bot.add_cog(Vouch(bot))