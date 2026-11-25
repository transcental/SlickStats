"""One-time DM to users who set up Last.fm with their own API key.

Personal Last.fm API keys stop working for free accounts on 1 Dec 2026. Their
status keeps updating through the server's key and their saved username, but
we ask them to connect properly so we know the username is theirs.
"""

import asyncio
import logging

from utils.env import env
from utils.lastfm_auth import auth_url
from utils.lastfm_auth import DM_STATE_MAX_AGE

DM_FLAG = "lastfm_migration_dm_sent"


def migration_blocks(user_id: str) -> list[dict]:
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    ":wave: Slick Stats now connects to Last.fm by signing in, instead of using your own API key. "
                    "Last.fm is turning off API keys for free accounts on 1 December, so please connect your account "
                    "to keep your music status working smoothly."
                ),
            },
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Connect Last.fm",
                        "emoji": True,
                    },
                    "style": "primary",
                    "url": auth_url(user_id, DM_STATE_MAX_AGE),
                    "action_id": "lastfm_connect",
                }
            ],
        },
    ]


async def users_to_migrate() -> list[dict]:
    """Users with an old Last.fm setup who haven't connected or been DM'd yet"""
    users = env.motor_client["slickstats"].users
    return await users.find(
        {
            "$or": [
                {"lastfm_api_key": {"$nin": [None, ""]}},
                {"lastfm_username": {"$nin": [None, ""]}},
            ],
            "lastfm_session_key": {"$in": [None, ""]},
            DM_FLAG: {"$ne": True},
            "enabled": {"$ne": False},
        }
    ).to_list()


async def send_migration_dms(delay: float = 1.5):
    """DMs every user who still needs to connect Last.fm, once each"""
    if not env.lastfm_enabled:
        return
    from utils.db import update_user_settings
    from utils.slack import app

    users = await users_to_migrate()
    if users:
        logging.info(f"Sending Last.fm migration DMs to {len(users)} users")

    for user in users:
        user_id = user.get("user_id")
        if not user_id:
            continue
        try:
            installation = await env.installation_store.async_find_installation(
                user_id=user_id
            )
            if not installation:
                continue
            await app.client.chat_postMessage(
                channel=user_id,
                token=installation.bot_token,
                text="Slick Stats now connects to Last.fm by signing in. Please connect your Last.fm account from the app home.",
                blocks=migration_blocks(user_id),
            )
            await update_user_settings(user_id, {DM_FLAG: True})
        except Exception as e:
            logging.error(f"Couldn't send Last.fm migration DM to {user_id}: {e}")
        await asyncio.sleep(delay)
