# froget this
import asqlite3
import json
import os
import asyncio

class dbStuff:
    def __init__(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.init())
    async def init(self):
        async with asqlite3.connect("database.db") as db:
            self.db = db
            self.cursor = await self.db.cursor()
            await self.cursor.execute("CREATE TABLE IF NOT EXISTS seller (id TEXT PRIMARY KEY)")
            await self.cursor.execute("SELECT * FROM seller")
            
        if self.cursor.fetchone() is None:
            self.cursor.execute("INSERT INTO seller (id) VALUES ('foo')")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS ownerids (id INTEGER PRIMARY KEY)")
        self.db.commit()
    async def set_seller_role(self, role_id):
        self.cursor.execute("UPDATE seller SET id = ?", (role_id,))
        self.db.commit()
        
    async def add_owner(self, owner_id):
        self.cursor.execute("INSERT INTO ownerids (id) VALUES (?)", (owner_id,))
        self.db.commit()
    
    async def remove_owner(self, owner_id):
        self.cursor.execute("DELETE FROM ownerids WHERE id = ?", (owner_id,))
        self.db.commit()
    
    async def check_owner(self, owner_id):
        self.cursor.execute("SELECT * FROM ownerids WHERE id = ?", (owner_id,))
        return self.cursor.fetchone() is not None
 
