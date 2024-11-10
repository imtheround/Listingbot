# roxco made dis (need revamp)
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View, Modal, TextInput
import os
import sqlite3
import chat_exporter
import datetime
import io
import random
from db.dbStuff import dbStuff
import string
from utils.getStatsForCmd import getStatsForCmd
from utils.caching import Caching
from utils.getProfile import get_profile
from utils.generalUtils import handleError
from utils.getUuid import get_uuid
from utils.fetchStats import fetchNetworth

#this is so weird
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


SELLER_ROLE_ID = 1302366645204811808


class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name="ticket", description="Create a ticket to sell your Macro Ready Account!")
    async def ticket(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator == False:
            await interaction.response.send_message("Not sigma enough!", ephemeral=True)
            return
        embed = discord.Embed(
            title="Open a account selling ticket",
            description=( 
                "Click the button below to create a ticket."
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
        profile = TextInput(label="Profile", placeholder="Enter your profile",required=False)
        offer = TextInput(label="Offer", placeholder="Enter your offer", required=True)
        macro = TextInput(label="Macro Type", placeholder="Farming or Mining", required=True)
        def __init__(self):
            super().__init__()
            self.export = chat_exporter
        async def on_submit(self, interaction: discord.Interaction):
            await interaction.response.defer()
            guild = interaction.guild
            ADMIN_ROLE_ID = await dbStuff().get_seller_role()
            ADMIN_ROLE_ID = ADMIN_ROLE_ID[0]
            if ADMIN_ROLE_ID == "foo":
                await interaction.response.send_message("No seller role found.", ephemeral=True)
                return
            # Create a new ticket channel with a nicer name format
            ticket_channel_name = f"💲｜sell {self.username.value}｜{self.offer.value}"
            ticket_channel = await guild.create_text_channel(
                name=ticket_channel_name,
                overwrites={
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    guild.get_role(int(ADMIN_ROLE_ID)): discord.PermissionOverwrite(read_messages=True, send_messages=True)
                }
            )

            ticket_key = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

            cursor.execute('INSERT INTO tickets (ticket_key, user_id, claimed_user_id, channel_id, messages) VALUES (?, ?, ?, ?, ?)',
                           (ticket_key, interaction.user.id, None, ticket_channel.id, ""))
            conn.commit()

            ticket_embed = discord.Embed(
                title="📝 Ticket Created",
                description=f"Ticket created by {interaction.user.mention}\n**Ticket Key:** {ticket_key}",
                color=discord.Color.green()
            )
            ticket_embed.add_field(name="Username", value=self.username.value, inline=False)
            ticket_embed.add_field(name="Offer", value=self.offer.value, inline=False)
            ticket_embed.add_field(name="Macro Type", value=self.macro.value, inline=False)
            ticket_embed.add_field(name="Skycrypt Link", value=f"https://sky.shiiyu.moe/stats/{self.username.value}", inline=False)

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
                await self.close_ticket(interaction, ticket_channel, ticket_key)

            add_button.callback = add_button_callback
            claim_button.callback = claim_button_callback
            unclaim_button.callback = unclaim_button_callback
            close_button.callback = close_button_callback

            view.add_item(add_button)
            view.add_item(claim_button)
            view.add_item(unclaim_button)
            view.add_item(close_button)
            LOGS_CHANNEL_ID = await dbStuff().get_logs_channel()
            try:
                LOGS_CHANNEL_ID = LOGS_CHANNEL_ID[0]
            except:
                await interaction.response.send_message("No logs channel found.", ephemeral=True)
                return
            await ticket_channel.send(embed=ticket_embed, view=view)
            await ticket_channel.send(f"# PLEASE ONLY DEAL WITHIN THIS TICKET, IF SOMEONE DMS YOU, WE ARE NOT RESPONSIBLE FOR ANYTHING IT. (note that only the deal within the ticket will be noted)")
            username = self.username.value
            uuid = await get_uuid(username)
            profile = self.profile.value.capitalize()
            stats = getStatsForCmd()
            if not profile:
                stats = await stats.get_stats(username)
            else:
                stats = await stats.get_stats(username, profile)
            if stats['sucess'] == False:
                await ticket_channel.send(embed=discord.Embed(title="Error", description=stats['cause']))
                return
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
            await ticket_channel.send(embed=embed)
            logs_channel = guild.get_channel(LOGS_CHANNEL_ID)
            if logs_channel:
                log_embed = discord.Embed(
                    title="📑 Ticket Created",
                    description=f"Ticket Key: {ticket_key}\nCreated by: {interaction.user.mention}",
                    color=discord.Color.blue()
                )
                await logs_channel.send(embed=log_embed)
        
            SELLER_ROLE_ID = await dbStuff().get_seller_role()
            seller_role = guild.get_role(SELLER_ROLE_ID)
            
            if seller_role:
                await ticket_channel.send(f"{seller_role.mention} A new ticket has been created!")
        async def add_user(self, interaction: discord.Interaction, ticket_channel):
            user_id_modal = self.UserIDModal()
            await interaction.response.send_modal(user_id_modal)

            await user_id_modal.wait()  
            user_id = user_id_modal.user_id

            if user_id:
                try:
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

        async def close_ticket(self, interaction: discord.Interaction, ticket_channel, ticket_key):
            await interaction.response.defer()
            transcript = await self.export.export(ticket_channel)
            transcript_file = discord.File(
                    io.BytesIO(transcript.encode()),
                    filename=f"transcript{ticket_key}.html",
                )
            e = await dbStuff().get_logs_channel()
            if e == "foo":
                await interaction.response.send_message("No logs channel found.", ephemeral=True)
                return
            e = e[0]
            logs_channel = interaction.guild.get_channel(int(e))
            message = await logs_channel.send(f"Chat exported for ticket {ticket_key}", file=transcript_file)
            link = await chat_exporter.link(message)
            embed = discord.Embed(
                title="📝 Chat Exported",
                description=f"Chat exported for ticket {ticket_key}\n[View transcript]({link})",
                color=discord.Color.green()
            )
            await interaction.user.send(embed=embed)
            cursor.execute('DELETE FROM tickets WHERE ticket_key = ?', (ticket_channel.id,))
            await ticket_channel.delete()
        class UserIDModal(Modal, title="Add User to Ticket"):
            user_id_input = TextInput(label="User ID", placeholder="Enter the user's ID", required=True)

            async def on_submit(self, interaction: discord.Interaction):
                try:
                    self.user_id = int(self.user_id_input.value)
                    await interaction.response.send_message(f"User ID {self.user_id} submitted.", ephemeral=True)
                except ValueError:
                    await interaction.response.send_message("Invalid user ID. Please enter a valid number.", ephemeral=True)



async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
