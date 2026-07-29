import sys, os
sys.path.insert(0, "/opt/autosec")
os.chdir("/opt/autosec")

from dotenv import load_dotenv
load_dotenv()

import yaml
with open("config.yaml") as f:
    cfg = yaml.safe_load(f)
cfg["security"]["jwt_secret"] = "super_secret_jwt_2026_autosecure"
cfg["security"]["encryption_key"] = "super_secret_jwt_2026_autosecure"
cfg["security"]["session_secret"] = "super_secret_jwt_2026_autosecure"
with open("config.yaml", "w") as f:
    yaml.dump(cfg, f, default_flow_style=False, sort_keys=False)
print("Config OK")

from passlib.hash import bcrypt
import asyncio
from sqlalchemy import select
import autosecure.core.database as db
from autosecure.models.user import User

async def create_user():
    await db.init_db()
    async with db.session_factory() as session:
        existing = await session.execute(select(User).where(User.user_id == "round"))
        if existing.scalar_one_or_none():
            print("User already exists")
            return
        pw_hash = bcrypt.hash("round7878")
        user = User(
            user_id="round",
            permissions={"password_hash": pw_hash, "role": "owner"},
            claiming="none",
            rest_split=0,
        )
        session.add(user)
        await session.commit()
        print("User round created successfully")

asyncio.run(create_user())
