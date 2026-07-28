"""Database repository package for AutoSecure."""

from autosecure.db.accounts import AccountRepo
from autosecure.db.blacklist import BlacklistRepo
from autosecure.db.bots import BotRepo
from autosecure.db.emails import EmailRepo
from autosecure.db.embeds import EmbedRepo
from autosecure.db.leaderboard import LeaderboardRepo
from autosecure.db.licenses import LicenseRepo
from autosecure.db.quarantine import QuarantineRepo
from autosecure.db.settings import SettingsRepo
from autosecure.db.users import UserRepo

__all__ = [
    "AccountRepo",
    "BlacklistRepo",
    "BotRepo",
    "EmailRepo",
    "EmbedRepo",
    "LeaderboardRepo",
    "LicenseRepo",
    "QuarantineRepo",
    "SettingsRepo",
    "UserRepo",
]
