from slack_sdk import WebClient

from utils.db import get_user_settings, update_user_settings
from utils.env import env
from utils.slack import app, update_slack_pfp, update_slack_status
from utils.update import update_status
from utils.views import generate_home_view


@app.event("app_home_opened")
def update_home_tab(client: WebClient, event, logger):
    """

    :param client: WebClient:
    :param event:
    :param logger:

    """
    try:
        user_data = get_user_settings(user_id=event["user"]) or {
            "user_id": event["user"]
        }

        team_id = client.team_info()["team"]["id"]
        installations = env.installation_store.find_installations(team_id=team_id)
        if not installations:
            return
        installation = installations[0]
        token = installation.bot_token
        client.views_publish(
            user_id=event["user"],
            token=token,
            view=generate_home_view(
                lastfm_username=user_data.get("lastfm_username", None),
                lastfm_api_key=user_data.get("lastfm_api_key", None),
                steam_id=user_data.get("steam_id", None),
                steam_api_key=user_data.get("steam_api_key", None),
                jellyfin_url=user_data.get("jellyfin_url", None),
                jellyfin_api_key=user_data.get("jellyfin_api_key", None),
                jellyfin_username=user_data.get("jellyfin_username", None),
                default_pfp=user_data.get("default_pfp", None),
                huddle_pfp=user_data.get("huddle_pfp", None),
                music_pfp=user_data.get("music_pfp", None),
                film_pfp=user_data.get("film_pfp", None),
                gaming_pfp=user_data.get("gaming_pfp", None),
                user_exists=bool(user_data),
                enabled=user_data.get("enabled", True)
            ),
        )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")


@app.action("authorise-btn")
def authorise_btn(ack):
    """

    :param ack:

    """
    ack()
    return


@app.action("submit_settings")
def submit_settings(ack, body):
    ack()
    settings = ["lastfm_username", "lastfm_api_key", "steam_id", "steam_api_key", "jellyfin_url", "jellyfin_api_key", "jellyfin_username", "default_pfp", "huddle_pfp", "music_pfp", "film_pfp", "gaming_pfp"]
    data = {}
    for block in body["view"]["state"]["values"].values():
        for setting in settings:
            if setting in block:
                data[setting] = block[setting]["value"]

    update_user_settings(body["user"]["id"], data)


@app.action("toggle_enabled")
def toggle_enabled(ack, body):
    ack()
    user = get_user_settings(user_id=body["user"]["id"])
    if not user: return
    update_user_settings(body["user"]["id"], {"enabled": not user.get("enabled", True)})
    installation = env.installation_store.find_installation(user_id=body["user"]["id"])
    if not installation: return
    update_slack_status(
        emoji="",
        status="",
        user_id=body["user"]["id"],
        token=installation.user_token,
    )

@app.event("user_huddle_changed")
def huddle_changed(event):
    in_huddle = event.get("user", {}).get("profile", {}).get("huddle_state", None)
    user = get_user_settings(user_id=event["user"]["id"])
    if not user: return
    match in_huddle:
        case "in_a_huddle":
            if user.get('pfp') != "huddle_pfp":
                installation = env.installation_store.find_installation(user_id=event["user"]["id"])
                if not installation: return
                update_slack_pfp(
                    new_pfp_type="huddle_pfp",
                    user_id=event["user"]["id"],
                    bot_token=installation.bot_token,
                    token=installation.user_token,
                    current_pfp=user.get("pfp"),
                    img_url=user.get("huddle_pfp", None),
                )
        case "default_unset" | None:
            if user.get('pfp') == "huddle_pfp":
                installation = env.installation_store.find_installation(user_id=event["user"]["id"])
                if not installation: return
                update_slack_pfp(
                    new_pfp_type="default_pfp",
                    user_id=event["user"]["id"],
                    bot_token=installation.bot_token,
                    token=installation.user_token,
                    current_pfp=user.get("pfp"),
                    img_url=user.get("default_pfp", None),
                )


if __name__ == "__main__":
    env.mongo_client.admin.command("ping")
    print("Connected to MongoDB")
    update_status()
    print(f"App is running on port {env.port}")
    app.start(port=env.port)
