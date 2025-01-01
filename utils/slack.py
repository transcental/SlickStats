import requests
from slack_bolt import App
from slack_bolt.oauth.oauth_settings import OAuthSettings

from status.jellyfin import get_jellyfin_status
from status.lastfm import get_lastfm_status
from status.steam import get_steam_status
from utils.db import update_user_settings, get_user_settings
from utils.env import env

from io import BytesIO

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

oauth_settings = OAuthSettings(
    client_id=env.slack_client_id,
    client_secret=env.slack_client_secret,
    installation_store=env.installation_store,
    user_scopes=["users.profile:read", "users.profile:write", "users:read"],
    scopes=[
        "chat:write",
        "im:history",
        "users.profile:read",
        "commands",
        "team:read",
        "users:read",
        "emoji:read"
    ],
)

app = App(signing_secret=env.slack_signing_secret, oauth_settings=oauth_settings)


def update_slack_status(emoji, status, user_id, token, expiry=0):
    """

    :param emoji:
    :param status:
    :param user_id:
    :param token:
    :param expiry:  (Default value = 0)

    """
    current_status = app.client.users_profile_get(user=user_id, token=token)
    if current_status.get("ok"):
        status_emoji = current_status["profile"].get("status_emoji", "")
    else:
        status_emoji = ""

    user = get_user_settings(user_id)
    if not user:
        return
    emojis = [
        user.get(emoji_name, "")
        for emoji_name in [status["emoji"] for status in STATUSES]
    ]
    emojis.append(user.get("huddle_emoji", ":headphones:"))

    if status_emoji in emojis or status_emoji == "":
        current_status_text = current_status["profile"].get("status_text", "")
        if current_status_text == status:
            return

        app.client.users_profile_set(
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


def update_slack_pfp(new_pfp_type, user_id, current_pfp, bot_token, token, img_url):
    """
    Update Slack profile picture if the new type is different from the current one and a valid image URL is provided.

    :param new_pfp_type: The new profile picture type.
    :param user_id: The Slack user ID.
    :param current_pfp: The current profile picture type.
    :param token: The Slack API token.
    :param img_url: The URL of the new profile picture.
    """
    if new_pfp_type != current_pfp and img_url:
        update_user_settings(user_id, {"pfp": new_pfp_type})
        try:
            res = requests.get(img_url)
            if res.status_code != 200 or "image" not in res.headers["Content-Type"]:
                # Notify user that the image is invalid
                app.client.chat_postMessage(
                    channel=user_id,
                    text=f"The supplied image URL for {new_pfp_type} appears to be invalid. Please make sure the correct image URL is supplied on my App home.",
                    token=bot_token,
                )
                return

            content = BytesIO(res.content)
            app.client.users_setPhoto(image=content, token=token)
        except Exception as e:
            # Log the exception or notify the user
            app.client.chat_postMessage(
                channel=user_id,
                text=f"An error occurred while updating the profile picture: {str(e)}",
                token=bot_token,
            )
    return


def log_to_slack(message, token):
    """

    :param message:
    :param token:

    """
    app.client.chat_postMessage(
        channel=env.slack_log_channel, text=message, token=token
    )
