import logging
from io import BytesIO

import requests
from slack_bolt.async_app import AsyncApp
from slack_bolt.oauth.async_oauth_settings import AsyncOAuthSettings

from status.jellyfin import get_jellyfin_status
from status.lastfm import get_lastfm_status
from status.steam import get_steam_status
from utils.db import get_user_settings
from utils.db import update_user_settings
from utils.env import env

STATUSES = [
    {
        "name": "Steam",
        "emoji": "gaming_emoji",
        "default_emoji": ":video_game:",
        "status": "Playing (custom) via Steam",
        "pfp": "gaming_pfp",
        "function": get_steam_status,
    },
    {
        "name": "Jellyfin",
        "emoji": "film_emoji",
        "default_emoji": ":tv:",
        "status": "Watching (custom)",
        "pfp": "film_pfp",
        "function": get_jellyfin_status,
    },
    {
        "name": "Last.fm",
        "emoji": "music_emoji",
        "default_emoji": ":musical_note:",
        "status": "(custom)",
        "pfp": "music_pfp",
        "function": get_lastfm_status,
    },
]

oauth_settings = AsyncOAuthSettings(
    client_id=env.slack_client_id,
    client_secret=env.slack_client_secret,
    installation_store=env.installation_store,
    user_scopes=["users.profile:read", "users.profile:write", "users:read"],
    scopes=[
        "chat:write",
        "chat:write.public",
        "chat:write.customize",
        "im:history",
        "users.profile:read",
        "commands",
        "team:read",
        "users:read",
        "emoji:read",
    ],
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = AsyncApp(
    signing_secret=env.slack_signing_secret,
    oauth_settings=oauth_settings,
    logger=logger,
)


## NOT IMPLEMENTED YET
# @app.command("/current")
# async def current_command(ack: AsyncAck, body):
#     await ack()
# user_id = body["user_id"]
# channel_id = body["channel_id"]
# user = await get_user_settings(user_id)
# if not user: return

# installation = await env.installation_store.find_installation(user_id=user_id)
# if not installation: return
# token = installation.bot_token or ""

# print(user)
# await log_to_slack(f"Fetching current status for {user.get('user_id')}\nCurrently listening to {user.get('current_song')}\nCurrently playing {user.get('current_game')}\nCurrently watching: {user.get('current_jellyfin')}", token, channel_id)


async def check_token(token: str) -> bool:
    """Checks if the given token is valid."""

    res = await app.client.auth_test(token=token)
    return res.get("ok", False)


async def update_slack_status(emoji, status, user_id, token, expiry=0):
    """Update the user's Slack status with the given emoji and status.

    Keyword arguments:

    emoji -- The emoji to set as the status.

    status -- The status text.

    user_id -- The user's Slack ID.

    token -- The Slack API token.

    expiry -- The time in seconds until the status expires (default 0).
    """
    current_status = await app.client.users_profile_get(user=user_id, token=token)
    if current_status.get("ok"):
        status_emoji = current_status["profile"].get("status_emoji", "")
    else:
        status_emoji = ""

    user = await get_user_settings(user_id)
    if not user:
        return
    emojis = [
        user.get(
            emoji_name,
            next(
                (
                    status.get("default_emoji")
                    for status in STATUSES
                    if status.get("emoji") == emoji_name
                ),
                "",
            ),
        )
        for emoji_name in [status["emoji"] for status in STATUSES]
    ]
    emojis.append(user.get("huddle_emoji", ":headphones:"))

    if status_emoji in emojis or status_emoji == "":
        current_status_text = current_status["profile"].get("status_text", "")
        if current_status_text == status:
            return
        await app.client.users_profile_set(
            user=user_id,
            profile={
                "status_text": status,
                "status_emoji": user.get(
                    emoji,
                    next(
                        (
                            status.get("default_emoji")
                            for status in STATUSES
                            if status.get("emoji") == emoji
                        ),
                        "",
                    ),
                ),
                "status_expiration": expiry,
            },
            token=token,
        )


async def update_slack_pfp(
    new_pfp_type, user_id, current_pfp, bot_token, token, img_url
):
    """Update Slack profile picture if the new type is different from the current one and a valid image URL is provided.

    Keyword arguments:

    new_pfp_type -- The new profile picture type.

    user_id -- The user's Slack ID.

    current_pfp -- The current profile picture type.

    bot_token -- The bot's Slack API token.

    token -- The user's Slack API token.

    img_url -- The URL of the new profile picture.
    """
    if new_pfp_type != current_pfp and img_url:
        await update_user_settings(user_id, {"pfp": new_pfp_type})
        try:
            res = requests.get(img_url)
            if res.status_code != 200 or "image" not in res.headers["Content-Type"]:
                # Notify user that the image is invalid
                await app.client.chat_postMessage(
                    channel=user_id,
                    text=f"The supplied image URL for {new_pfp_type} appears to be invalid. Please make sure the correct image URL is supplied on my App home.",
                    token=bot_token,
                )
                return

            content = BytesIO(res.content)
            await app.client.users_setPhoto(image=content, token=token)
        except Exception as e:
            # Log the exception or notify the user
            await app.client.chat_postMessage(
                channel=user_id,
                text=f"An error occurred while updating the profile picture: {str(e)}",
                token=bot_token,
            )
    return


async def log_to_slack(
    message: str,
    token: str,
    channel_id: str = env.slack_log_channel,
    pfp: str | None = None,
    username: str | None = None,
):
    """Log a message to the #log channel. Wrapper around chat.postMessage.

    Keyword arguments:

    message -- The message to log.

    token -- The Slack API token.

    channel_id -- The channel ID to post the message to (default env.slack_log_channel).

    pfp -- The profile picture URL of the user posting the message.

    username -- The username of the user posting the message.
    """
    await app.client.chat_postMessage(
        channel=channel_id,
        text=message,
        token=token,
        username=username,
        icon_url=pfp,
        unfurl_links=False,
    )
