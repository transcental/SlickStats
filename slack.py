from slack_bolt import App
import os

app = App(token=os.environ.get("SLACK_BOT_TOKEN"), signing_secret=os.environ.get(
    "SLACK_SIGNING_SECRET"))
app.user_token = os.environ.get("SLACK_USER_TOKEN")

EMOJIS = {
    "music": ":musical_note:",
    "gaming": ":video_game:",
}

USER_ID = "U054VC2KM9P"
current_pfp = "normal"

def update_status(emoji, status, expiry=0):
    current_status = app.client.users_profile_get(user=USER_ID)
    if current_status.get("ok"):
        status_emoji = current_status["profile"].get("status_emoji", ":ghost:")
    else:
        status_emoji = ":ghost:"

    if status_emoji == '' or (emoji in EMOJIS and list(EMOJIS.values()).index(EMOJIS[emoji]) > list(EMOJIS.values()).index(status_emoji)):
        app.client.users_profile_set(
            token=app.user_token,
            profile={
                "status_text": status,
                "status_emoji": EMOJIS.get(emoji, ""),
                "status_expiration": expiry
            }
        )


def update_pfp(type):
    global current_pfp
    path = f'pfps/{type}.png'
    if type != current_pfp:
        current_pfp = type
        app.client.users_setPhoto(
            token=app.user_token,
            image=open(path, 'rb')
        )
