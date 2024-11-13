import aiosqlite
import json
import os
import asyncio

import aiosqlite

class dbStuff:
    def __init__(self):
        self.db = None
        self.cursor = None

    async def init(self):
        # Open a persistent database connection
        self.db = await aiosqlite.connect("database.db")
        self.cursor = await self.db.cursor()

        # Create tables with specified column types
        await self.cursor.execute("CREATE TABLE IF NOT EXISTS seller (id TEXT PRIMARY KEY)")
        await self.cursor.execute("CREATE TABLE IF NOT EXISTS ownerids (id INTEGER PRIMARY KEY)")
        await self.cursor.execute("CREATE TABLE IF NOT EXISTS verified (id TEXT PRIMARY KEY)")
        await self.cursor.execute("CREATE TABLE IF NOT EXISTS logs (id TEXT)")
        await self.cursor.execute("CREATE TABLE IF NOT EXISTS listing (id TEXT PRIMARY KEY)")
        # Ensure the 'seller' table has at least one row with a TEXT value for 'id'
        await self.cursor.execute("SELECT COUNT(*) FROM seller")
        if (await self.cursor.fetchone())[0] == 0:
            await self.cursor.execute("INSERT INTO seller (id) VALUES (?)", ('foo',))

        # Ensure the 'verified' table has at least one row with a TEXT value for 'id'
        await self.cursor.execute("SELECT COUNT(*) FROM verified")
        if (await self.cursor.fetchone())[0] == 0:
            await self.cursor.execute("INSERT INTO verified (id) VALUES (?)", ('foo',))

        # Ensure the 'logs' table has at least one row with a TEXT value for 'id'
        await self.cursor.execute("SELECT COUNT(*) FROM logs")
        if (await self.cursor.fetchone())[0] == 0:
            await self.cursor.execute("INSERT INTO logs (id) VALUES (?)", ('foo',))
        await self.cursor.execute("SELECT COUNT(*) FROM listing")
        if (await self.cursor.fetchone())[0] == 0:
            await self.cursor.execute("INSERT INTO listing (id) VALUES (?)", ('foo',))
        # Commit the changes to the database
        await self.db.commit()



            
    async def set_seller_role(self, role_id):
        async with aiosqlite.connect("database.db") as db:
            cursor = await db.cursor()
            await cursor.execute("UPDATE seller SET id = ?", (role_id,))
            await db.commit()
    async def get_seller_role(self):
        async with aiosqlite.connect("database.db") as db:
    
            cursor = await db.cursor()
            await cursor.execute("SELECT * FROM seller")
            return await cursor.fetchone()
    async def add_owner(self, owner_id):
        async with aiosqlite.connect("database.db") as db:
            cursor = await db.cursor()
            await cursor.execute("INSERT INTO ownerids (id) VALUES (?)", (owner_id,))
            await db.commit()
    
    async def remove_owner(self, owner_id):
        async with aiosqlite.connect("database.db") as db:
            cursor = await db.cursor()
            await cursor.execute("DELETE FROM ownerids WHERE id = ?", (owner_id,))
            await db.commit()
    
    async def check_owner(self, owner_id):
        async with aiosqlite.connect("database.db") as db:
            
            cursor = await db.cursor()
            await cursor.execute("SELECT * FROM ownerids WHERE id = ?", (owner_id,))
            return await cursor.fetchone() is not None
    async def set_verified(self, verified_id):
        async with aiosqlite.connect("database.db") as db:
            cursor = await db.cursor()
            await cursor.execute("UPDATE verified SET id = ?", (verified_id,))
            await db.commit()
    async def get_verified(self):
        async with aiosqlite.connect("database.db") as db:
            cursor = await db.cursor()
            await cursor.execute("SELECT * FROM verified")
            return await cursor.fetchone() 
    async def set_logs_channel(self, channel_id):
        async with aiosqlite.connect("database.db") as db:
            cursor = await db.cursor()
            await cursor.execute("UPDATE logs SET id = ?", (str(channel_id),))
            await db.commit()

    async def get_logs_channel(self):
        async with aiosqlite.connect("database.db") as db:
            cursor = await db.cursor()
            await cursor.execute("SELECT * FROM logs")
            return await cursor.fetchone()

    async def set_listing_catergory(self, listing_category):
        async with aiosqlite.connect("database.db") as db:
            cursor = await db.cursor()
            await cursor.execute("UPDATE listing SET id = ?", (listing_category,))
            await db.commit()
    async def get_listing_category(self):
        async with aiosqlite.connect("database.db") as db:
            cursor = await db.cursor()
            await cursor.execute("SELECT * FROM listing")
            return await cursor.fetchall()


async def setup(bot):
    await bot.add_cog(dbStuff(bot))