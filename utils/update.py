import asyncio, logging
from utils.db import get_all_users
from utils.env import env
from utils.slack import (
    log_to_slack,
    app,
    STATUSES,
    update_slack_pfp,
    update_slack_status,
)


async def update_status(delay: int = 25):
    """
    Fetches the status of all users from all services and then updates Slack status and profile pictures accordingly every delay seconds
    """
    await asyncio.sleep(delay)
    users = await get_all_users(enabled=True)
    if not users:
        return

    for user in users:
        set = False
        if user.get("in_huddle", False):
            continue

        installation = await env.installation_store.find_installation(
            user_id=user.get("user_id")
        )
        if not installation:
            continue

        bot_token = installation.bot_token or ""
        user_token = installation.user_token
        user_id = user.get("user_id")
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
