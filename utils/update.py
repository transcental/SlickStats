import asyncio
import logging

from utils.db import get_all_users
from utils.env import env
from utils.slack import app
from utils.slack import check_token
from utils.slack import log_to_slack
from utils.slack import STATUSES
from utils.slack import update_slack_pfp
from utils.slack import update_slack_status


async def run_updater(delay: int = 10):
    """Runs the updater every `delay` seconds"""
    while True:
        asyncio.create_task(update_status())
        await asyncio.sleep(delay)


async def update_status(delay: int = 10):
    """Fetches the status of all users from all services and then updates Slack status and profile pictures accordingly"""
    users = await get_all_users(enabled=True)
    if not users:
        return

    for user in users:
        set = False
        if user.get("in_huddle", False):
            continue

        installation = await env.installation_store.async_find_installation(
            user_id=user.get("user_id")
        )
        if not installation:
            continue

        bot_token = installation.bot_token or ""
        user_token = installation.user_token or ""
        user_id = user.get("user_id")

        if not await check_token(user_token):
            try:
                await app.client.chat_postMessage(
                    channel=user.get("user_id"),
                    text="Your token is invalid. Please reauthenticate with the app via the red button at the bottom of the app home.",
                    token=installation.bot_token,
                )
            finally:
                logging.error(
                    f"User {user.get('user_id')} has an invalid token. Skipping."
                )
                continue

        current_pfp = user.get("pfp")
        for status in STATUSES:
            custom, log_message = await status.get(
                "function",
                lambda _: logging.error(
                    f'Failed to run status fetching function for {status.get("name")}'
                ),
            )(user)
            if custom:
                await update_slack_status(
                    status.get("emoji"),
                    status.get("status", "").replace("(custom)", custom)[:100],
                    user_id=user_id,
                    token=user_token,
                )
                await update_slack_pfp(
                    new_pfp_type=status.get("pfp"),
                    current_pfp=current_pfp,
                    user_id=user_id,
                    bot_token=bot_token,
                    token=user_token,
                    img_url=user.get(status.get("pfp"), None),
                )
                set = True
            if log_message:
                slack_user = await app.client.users_info(user=user_id, token=bot_token)
                pfp = slack_user["user"]["profile"]["image_512"]
                username = (
                    slack_user["user"]["profile"]["display_name"]
                    or slack_user["user"]["real_name"]
                    or slack_user["user"]["name"]
                )
                await log_to_slack(log_message, bot_token, pfp=pfp, username=username)
                continue

        if not set:
            await update_slack_status(
                emoji="", status="", user_id=user_id, token=user_token
            )
            await update_slack_pfp(
                new_pfp_type="default_pfp",
                current_pfp=current_pfp,
                user_id=user_id,
                bot_token=bot_token,
                token=user_token,
                img_url=user.get("default_pfp", None),
            )
