import requests
from slack_bolt import App, Ack
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
        "chat:write.public",
        "chat:write.customize",
        "im:history",
        "users.profile:read",
        "commands",
        "team:read",
        "users:read",
        "emoji:read"
    ],
)

app = App(signing_secret=env.slack_signing_secret, oauth_settings=oauth_settings)


@app.command("/current")
def current_command(ack: Ack, body):
    ack()
    print('running')
    user_id = body["user_id"]
    channel_id = body["channel_id"]
    user = get_user_settings(user_id)
    if not user: return
    
    installation = env.installation_store.find_installation(user_id=user_id)
    if not installation: return
    token = installation.bot_token or ""

    print(user)
    log_to_slack(f"Fetching current status for {user.get('user_id')}\nCurrently listening to {user.get('current_song')}\nCurrently playing {user.get('current_game')}\nCurrently watching: {user.get('current_jellyfin')}", token, channel_id)


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
        user.get(emoji_name, next((status.get("default_emoji") for status in STATUSES if status.get("emoji") == emoji_name), ""))
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


def log_to_slack(message: str, token: str, channel_id: str = env.slack_log_channel, pfp: str | None = None, username: str | None = None):
    """
    Log a message to the #log channel. Wrapper around chat.postMessage.
    """
    app.client.chat_postMessage(
        channel=channel_id, text=message, token=token, username=username, icon_url=pfp, unfurl_links=False
    )
