"""Default embed, button, and modal templates."""

from __future__ import annotations

from typing import Any

import discord

DEFAULT_EMBEDS: dict[str, dict[str, Any]] = {
    "welcome": {
        "title": "Welcome to AutoSecure!",
        "description": "Secure your Microsoft accounts with ease.",
        "color": 0x7289DA,
    },
    "error": {
        "title": "Error",
        "description": "An unexpected error occurred.",
        "color": 0xFF0000,
    },
    "success": {
        "title": "Success",
        "description": "Operation completed successfully.",
        "color": 0x00FF00,
    },
    "loading": {
        "title": "Loading...",
        "description": "Please wait while we process your request.",
        "color": 0xFFFF00,
    },
    "no_license": {
        "title": "No License",
        "description": "You do not have an active license. Use `/redeem` to activate one.",
        "color": 0xFF0000,
    },
    "blacklisted": {
        "title": "Blacklisted",
        "description": "You are blacklisted from using this bot.",
        "color": 0xFF0000,
    },
    "rate_limited": {
        "title": "Rate Limited",
        "description": "You are being rate limited. Please wait.",
        "color": 0xFFAA00,
    },
    "account_secured": {
        "title": "Account Secured",
        "description": "Your account has been secured successfully.",
        "color": 0x00FF00,
    },
    "account_deleted": {
        "title": "Account Deleted",
        "description": "The account has been removed.",
        "color": 0xFF0000,
    },
    "quarantine": {
        "title": "Quarantined",
        "description": "This account has been moved to quarantine.",
        "color": 0xFFAA00,
    },
    "leaderboard": {
        "title": "Leaderboard",
        "description": "Top secured accounts by net worth.",
        "color": 0xFFD700,
    },
    "guide": {
        "title": "Setup Guide",
        "description": "Follow these steps to get started with AutoSecure.",
        "color": 0x7289DA,
    },
    "settings": {
        "title": "Settings",
        "description": "Configure your preferences.",
        "color": 0x7289DA,
    },
    "mail_inbox": {
        "title": "Email Inbox",
        "description": "Your recent emails.",
        "color": 0x00BFFF,
    },
    "mail_registered": {
        "title": "Email Registered",
        "description": "Email address registered successfully.",
        "color": 0x00FF00,
    },
    "bot_started": {
        "title": "Bot Started",
        "description": "Worker bot is now running.",
        "color": 0x00FF00,
    },
    "bot_stopped": {
        "title": "Bot Stopped",
        "description": "Worker bot has been stopped.",
        "color": 0xFF0000,
    },
    "license_redeemed": {
        "title": "License Redeemed",
        "description": "Your license has been activated.",
        "color": 0x00FF00,
    },
    "license_expired": {
        "title": "License Expired",
        "description": "Your license has expired.",
        "color": 0xFF0000,
    },
    "transfer": {
        "title": "License Transfer",
        "description": "License transferred successfully.",
        "color": 0x7289DA,
    },
    "admin_panel": {
        "title": "Admin Panel",
        "description": "Platform management tools.",
        "color": 0xFF5555,
    },
    "feature_overview": {
        "title": "Features",
        "description": "Everything AutoSecure can do.",
        "color": 0x7289DA,
    },
    "support": {
        "title": "Support",
        "description": "Need help? Join our support server.",
        "color": 0x7289DA,
    },
    "stats": {
        "title": "Statistics",
        "description": "Your account statistics.",
        "color": 0xFF5555,
    },
    "email_detail": {
        "title": "Email Detail",
        "description": "Email content.",
        "color": 0x00BFFF,
    },
    "confirm_action": {
        "title": "Confirm Action",
        "description": "Are you sure you want to proceed?",
        "color": 0xFFAA00,
    },
    "maintenance": {
        "title": "Maintenance",
        "description": "The bot is currently under maintenance.",
        "color": 0xFF5555,
    },
    "dm_notification": {
        "title": "Notification",
        "description": "You have a new notification.",
        "color": 0x00BFFF,
    },
}

DEFAULT_BUTTONS: dict[str, dict[str, Any]] = {
    "confirm": {
        "label": "Confirm",
        "style": discord.ButtonStyle.success,
        "custom_id": "btn_confirm",
    },
    "cancel": {
        "label": "Cancel",
        "style": discord.ButtonStyle.danger,
        "custom_id": "btn_cancel",
    },
    "close": {
        "label": "Close",
        "style": discord.ButtonStyle.danger,
        "custom_id": "btn_close",
    },
    "refresh": {
        "label": "Refresh",
        "style": discord.ButtonStyle.primary,
        "custom_id": "btn_refresh",
    },
    "next": {
        "label": "Next",
        "style": discord.ButtonStyle.secondary,
        "custom_id": "btn_next",
    },
    "previous": {
        "label": "Previous",
        "style": discord.ButtonStyle.secondary,
        "custom_id": "btn_previous",
    },
    "support": {
        "label": "Support Server",
        "style": discord.ButtonStyle.link,
        "url": "https://discord.gg/autosecure",
    },
    "website": {
        "label": "Website",
        "style": discord.ButtonStyle.link,
        "url": "https://autosecure.me",
    },
    "redeem": {
        "label": "Redeem License",
        "style": discord.ButtonStyle.success,
        "custom_id": "btn_redeem",
    },
    "secure": {
        "label": "Secure Account",
        "style": discord.ButtonStyle.primary,
        "custom_id": "btn_secure",
    },
    "guide": {
        "label": "Setup Guide",
        "style": discord.ButtonStyle.secondary,
        "custom_id": "btn_guide",
    },
}

DEFAULT_MODALS: dict[str, dict[str, Any]] = {
    "secure_account": {
        "title": "Secure Account",
        "fields": [
            {"custom_id": "email", "label": "Email", "style": "short", "required": True},
            {"custom_id": "password", "label": "Password", "style": "short", "required": False},
            {"custom_id": "recovery", "label": "Recovery Code", "style": "short", "required": False},
        ],
    },
    "redeem_license": {
        "title": "Redeem License",
        "fields": [
            {"custom_id": "key", "label": "License Key", "style": "short", "required": True},
        ],
    },
    "dm_message": {
        "title": "Send DM",
        "fields": [
            {"custom_id": "user_id", "label": "User ID", "style": "short", "required": True},
            {"custom_id": "message", "label": "Message", "style": "paragraph", "required": True},
        ],
    },
}
