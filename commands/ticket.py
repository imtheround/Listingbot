# roxco made dis (need revamp)
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View, Modal, TextInput
import os
import sqlite3
import random
import string


# Initialize SQLite3 database
conn = sqlite3.connect('tickets.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS tickets (
    ticket_key TEXT PRIMARY KEY,
    user_id INTEGER,
    claimed_user_id INTEGER,
    channel_id INTEGER,
    messages TEXT
)''')
conn.commit()

# Admin and role IDs
ADMIN_ROLE_ID = 1301953795999404053
SELLER_ROLE_ID = 1302366645204811808
LOGS_CHANNEL_ID = 1302378520009375814

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticket", description="Create a ticket to sell your Macro Ready Account!")
    async def ticket(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Open a account selling ticket",
            description=( 
                "**TOS:**\n"
                "By creating a ticket, you agree to the following terms:\n"
                "- You must wait **24 hours** before payment to ensure your session has expired.\n"
                "- Refunds are not possible if any of the terms are broken.\n"
                "- Be honest about your account's condition and details.\n"
                "Please click the button below to create a ticket."
            ),
            color=discord.Color.blue()
        )

        button = Button(label="Make Ticket", style=discord.ButtonStyle.primary)

        async def button_callback(interaction: discord.Interaction):
            modal = self.TicketModal()
            await interaction.response.send_modal(modal)

        button.callback = button_callback

        view = View()
        view.add_item(button)
        await interaction.response.send_message(embed=embed, view=view)

    class TicketModal(Modal, title="Ticket Information"):
        username = TextInput(label="Username", placeholder="Enter your in-game name", required=True)
        offer = TextInput(label="Offer", placeholder="Enter your offer", required=True)
        macro = TextInput(label="Macro Type", placeholder="Farming or Mining", required=True)

        async def on_submit(self, interaction: discord.Interaction):
            guild = interaction.guild

            # Create a new ticket channel with a nicer name format
            ticket_channel_name = f"💲｜{self.username.value}｜{self.offer.value}"
            ticket_channel = await guild.create_text_channel(
                name=ticket_channel_name,
                overwrites={
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    guild.get_role(ADMIN_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True)
                }
            )

            # Generate a unique 8-character random key for the ticket
            ticket_key = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

            # Store the ticket information in the SQLite database
            cursor.execute('INSERT INTO tickets (ticket_key, user_id, claimed_user_id, channel_id, messages) VALUES (?, ?, ?, ?, ?)',
                           (ticket_key, interaction.user.id, None, ticket_channel.id, ""))
            conn.commit()

            # Create an embed for the ticket creation
            ticket_embed = discord.Embed(
                title="📝 Ticket Created",
                description=f"Ticket created by {interaction.user.mention}\n**Ticket Key:** {ticket_key}",
                color=discord.Color.green()
            )
            ticket_embed.add_field(name="Username", value=self.username.value, inline=False)
            ticket_embed.add_field(name="Offer", value=self.offer.value, inline=False)
            ticket_embed.add_field(name="Macro Type", value=self.macro.value, inline=False)
            ticket_embed.add_field(name="Skycrypt Link", value=f"https://sky.shiiyu.moe/stats/{self.username.value}", inline=False)

            # Create buttons for the ticket
            view = View()
            add_button = Button(label="Add User", style=discord.ButtonStyle.secondary)
            claim_button = Button(label="Claim", style=discord.ButtonStyle.success)
            unclaim_button = Button(label="Unclaim", style=discord.ButtonStyle.secondary)
            close_button = Button(label="Close", style=discord.ButtonStyle.danger)

            async def add_button_callback(interaction: discord.Interaction):
                await self.add_user(interaction, ticket_channel)

            async def claim_button_callback(interaction: discord.Interaction):
                await self.claim_ticket(interaction, ticket_key)

            async def unclaim_button_callback(interaction: discord.Interaction):
                await self.unclaim_ticket(interaction, ticket_key)

            async def close_button_callback(interaction: discord.Interaction):
                await self.close_ticket(interaction, ticket_channel)

            add_button.callback = add_button_callback
            claim_button.callback = claim_button_callback
            unclaim_button.callback = unclaim_button_callback
            close_button.callback = close_button_callback

            view.add_item(add_button)
            view.add_item(claim_button)
            view.add_item(unclaim_button)
            view.add_item(close_button)

            await ticket_channel.send(embed=ticket_embed, view=view)

            # Log the ticket creation in the logs channel
            logs_channel = guild.get_channel(LOGS_CHANNEL_ID)
            if logs_channel:
                log_embed = discord.Embed(
                    title="📑 Ticket Created",
                    description=f"Ticket Key: {ticket_key}\nCreated by: {interaction.user.mention}",
                    color=discord.Color.blue()
                )
                await logs_channel.send(embed=log_embed)

            # Ping the seller role
            seller_role = guild.get_role(SELLER_ROLE_ID)
            if seller_role:
                await ticket_channel.send(f"{seller_role.mention} A new ticket has been created!")

            await interaction.response.send_message(f"Ticket created! Ticket Key: {ticket_key}", ephemeral=True)

        async def add_user(self, interaction: discord.Interaction, ticket_channel):
            user_id_modal = self.UserIDModal()
            await interaction.response.send_modal(user_id_modal)

            await user_id_modal.wait()  # Wait for modal submission
            user_id = user_id_modal.user_id

            if user_id:
                try:
                    # Attempt to fetch the user directly from the server
                    user = await interaction.guild.fetch_member(user_id)
                    await ticket_channel.set_permissions(user, read_messages=True, send_messages=True)
                    await interaction.followup.send(f"{user.mention} has been added to the ticket.", ephemeral=True)
                except discord.NotFound:
                    await interaction.followup.send("User not found in the server.", ephemeral=True)
                except discord.HTTPException:
                    await interaction.followup.send("An error occurred while trying to add the user.", ephemeral=True)

        async def claim_ticket(self, interaction: discord.Interaction, ticket_key):
            cursor.execute('SELECT claimed_user_id FROM tickets WHERE ticket_key = ?', (ticket_key,))
            result = cursor.fetchone()

            if result[0] is None:
                cursor.execute('UPDATE tickets SET claimed_user_id = ? WHERE ticket_key = ?', (interaction.user.id, ticket_key))
                conn.commit()
                await interaction.response.send_message(f"You have claimed the ticket: {ticket_key}", ephemeral=True)
            else:
                await interaction.response.send_message("This ticket is already claimed.", ephemeral=True)

        async def unclaim_ticket(self, interaction: discord.Interaction, ticket_key):
            cursor.execute('SELECT claimed_user_id FROM tickets WHERE ticket_key = ?', (ticket_key,))
            result = cursor.fetchone()

            if result[0] == interaction.user.id:
                cursor.execute('UPDATE tickets SET claimed_user_id = NULL WHERE ticket_key = ?', (ticket_key,))
                conn.commit()
                await interaction.response.send_message(f"You have unclaimed the ticket: {ticket_key}", ephemeral=True)
            else:
                await interaction.response.send_message("You cannot unclaim a ticket that you haven't claimed.", ephemeral=True)

        async def close_ticket(self, interaction: discord.Interaction, ticket_channel):
            await ticket_channel.delete()
            await interaction.response.send_message(f"The ticket channel has been closed.", ephemeral=True)

        class UserIDModal(Modal, title="Add User to Ticket"):
            user_id_input = TextInput(label="User ID", placeholder="Enter the user's ID", required=True)

            async def on_submit(self, interaction: discord.Interaction):
                try:
                    self.user_id = int(self.user_id_input.value)
                    await interaction.response.send_message(f"User ID {self.user_id} submitted.", ephemeral=True)
                except ValueError:
                    await interaction.response.send_message("Invalid user ID. Please enter a valid number.", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return  # Ignore bot messages

        cursor.execute('SELECT channel_id FROM tickets')
        ticket_channel_ids = [row[0] for row in cursor.fetchall()]

        if message.channel.id in ticket_channel_ids:
            cursor.execute('SELECT messages FROM tickets WHERE channel_id = ?', (message.channel.id,))
            result = cursor.fetchone()
            if result:
                messages = result[0]
                messages += f"{message.author}: {message.content}\n"
                cursor.execute('UPDATE tickets SET messages = ? WHERE channel_id = ?', (messages, message.channel.id))
                conn.commit()

    @app_commands.command(name="transcript", description="View the transcript of a ticket")
    async def transcript(self, interaction: discord.Interaction, key: str):
        cursor.execute('SELECT messages FROM tickets WHERE ticket_key = ?', (key,))
        result = cursor.fetchone()

        if result:
            messages = result[0]
            await interaction.response.send_message(f"Transcript for ticket {key}:\n{messages}", ephemeral=True)
        else:
            await interaction.response.send_message("No transcript found for this ticket key.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))