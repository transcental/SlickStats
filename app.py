import asyncio
import logging
import uvicorn
from concurrent.futures import ThreadPoolExecutor
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_sdk.web.async_client import AsyncWebClient
from slack_bolt.async_app import AsyncAck
from utils.db import get_user_settings, update_user_settings
from utils.env import env
from utils.slack import app, update_slack_pfp, update_slack_status
from utils.update import update_status
from utils.views import generate_home_view

executor = ThreadPoolExecutor(2)


def get_home(user_data):
    return generate_home_view(
        lastfm_username=user_data.get("lastfm_username", None),
        lastfm_api_key=user_data.get("lastfm_api_key", None),
        steam_id=user_data.get("steam_id", None),
        steam_api_key=user_data.get("steam_api_key", None),
        jellyfin_url=user_data.get("jellyfin_url", None),
        jellyfin_api_key=user_data.get("jellyfin_api_key", None),
        jellyfin_username=user_data.get("jellyfin_username", None),
        music_emoji=user_data.get("music_emoji", ":musical_note:"),
        gaming_emoji=user_data.get("gaming_emoji", ":video_game:"),
        film_emoji=user_data.get("film_emoji", ":tv:"),
        huddle_emoji=user_data.get("huddle_emoji", ":headphones:"),
        default_pfp=user_data.get("default_pfp", None),
        huddle_pfp=user_data.get("huddle_pfp", None),
        music_pfp=user_data.get("music_pfp", None),
        film_pfp=user_data.get("film_pfp", None),
        gaming_pfp=user_data.get("gaming_pfp", None),
        user_exists=bool(user_data),
        enabled=user_data.get("enabled", True),
    )


@app.event("app_home_opened")
async def update_home_tab(client: AsyncWebClient, event, logger):
    """

    :param client: WebClient:
    :param event:
    :param logger:

    """
    try:
        user_data = get_user_settings(user_id=event["user"]) or {
            "user_id": event["user"]
        }

        team_info = await client.team_info()
        team_id = team_info["team"]["id"]
        installations = await env.installation_store.find_installations(team_id=team_id)
        if not installations:
            return
        installation = installations[0]
        token = installation.bot_token
        await client.views_publish(
            user_id=event["user"], token=token, view=get_home(user_data)
        )
    except Exception as e:
        logger.error(f"Error publishing home tab: {e}")


@app.action("authorise-btn")
async def authorise_btn(ack: AsyncAck):
    """

    :param ack:

    """
    await ack()
    return


@app.action("submit_settings")
async def submit_settings(ack: AsyncAck, body):
    await ack()
    settings = [
        "lastfm_username",
        "lastfm_api_key",
        "steam_id",
        "steam_api_key",
        "jellyfin_url",
        "jellyfin_api_key",
        "jellyfin_username",
        "default_pfp",
        "huddle_pfp",
        "music_pfp",
        "film_pfp",
        "gaming_pfp",
        "music_emoji",
        "gaming_emoji",
        "film_emoji",
        "huddle_emoji",
    ]
    data = {}
    for block_id, block in body["view"]["state"]["values"].items():
        if block_id in settings:
            for action in block.values():
                if "value" in action:
                    data[block_id] = action["value"]
                elif "selected_option" in action:
                    data[block_id] = action["selected_option"]["value"]

    await update_user_settings(body["user"]["id"], data)
    user = await get_user_settings(user_id=body["user"]["id"])
    installation = await env.installation_store.find_installation(
        user_id=body["user"]["id"]
    )
    if not installation:
        return
    await app.client.views_publish(
        user_id=body["user"]["id"], token=installation.bot_token, view=get_home(user)
    )


@app.action("toggle_enabled")
async def toggle_enabled(ack: AsyncAck, body):
    await ack()
    user = await get_user_settings(user_id=body["user"]["id"])
    if not user:
        return
    await update_user_settings(
        body["user"]["id"], {"enabled": not user.get("enabled", True)}
    )
    installation = await env.installation_store.find_installation(
        user_id=body["user"]["id"]
    )
    if not installation:
        return
    await update_slack_status(
        emoji="",
        status="",
        user_id=body["user"]["id"],
        token=installation.user_token,
    )


@app.options("emojis")
async def emojis_data_source_handler(ack: AsyncAck, body):
    keyword = body.get("value")
    installation = await env.installation_store.find_installation(
        user_id=body["user"]["id"]
    )
    if not installation:
        await ack()
        return

    emojis_info = await app.client.emoji_list(token=installation.bot_token)
    emojis = emojis_info.get("emoji", [])

    options = [
        {
            "text": {"type": "plain_text", "text": f":{emoji}: {emoji}"},
            "value": f":{emoji}:",
        }
        for emoji in emojis
    ]

    if keyword and len(keyword) > 0:
        options = [option for option in options if keyword in option["text"]["text"]]
        await ack(options=options[:100])
    else:
        await ack(options=options[:100])


@app.event("user_huddle_changed")
async def huddle_changed(event):
    in_huddle = event.get("user", {}).get("profile", {}).get("huddle_state", None)
    user = await get_user_settings(user_id=event["user"]["id"])
    if not user or not user.get("enabled", True):
        return

    installation = await env.installation_store.find_installation(
        user_id=event["user"]["id"]
    )
    if not installation:
        return

    match in_huddle:
        case "in_a_huddle":
            if user.get("pfp") != "huddle_pfp":
                await update_user_settings(event["user"]["id"], {"in_huddle": True})
                await update_slack_pfp(
                    new_pfp_type="huddle_pfp",
                    user_id=event["user"]["id"],
                    bot_token=installation.bot_token,
                    token=installation.user_token,
                    current_pfp=user.get("pfp"),
                    img_url=user.get("huddle_pfp", None),
                )
                if user.get("huddle_emoji", ":headphones:") != ":headphones:":
                    await update_slack_status(
                        emoji="huddle_emoji",
                        status="In a huddle",
                        user_id=event["user"]["id"],
                        token=installation.user_token,
                    )
        case "default_unset" | None:
            if user.get("pfp") == "huddle_pfp":
                await update_user_settings(event["user"]["id"], {"in_huddle": False})
                await update_slack_pfp(
                    new_pfp_type="default_pfp",
                    user_id=event["user"]["id"],
                    bot_token=installation.bot_token,
                    token=installation.user_token,
                    current_pfp=user.get("pfp"),
                    img_url=user.get("default_pfp", None),
                )
                if user.get("huddle_emoji", ":headphones:") != ":headphones:":
                    await update_slack_status(
                        emoji="",
                        status="",
                        user_id=event["user"]["id"],
                        token=installation.user_token,
                    )


def run_uvicorn():
    uvicorn.run(
        "utils.starlette:app",
        host="0.0.0.0",
        port=env.port,
        log_level="info" if env.environment != "production" else "warning",
    )


async def main():
    await env.async_init()
    await env.mongo_client.admin.command("ping")
    logging.info("Connected to MongoDB")

    asyncio.create_task(update_status(25))

    handler = AsyncSocketModeHandler(app, env.slack_app_token)
    logging.info("Starting Socket Mode handler")
    executor.submit(run_uvicorn)
    logging.info(f"Uvicorn app is running on port {env.port}")
    await handler.start_async()


if __name__ == "__main__":
    try:
        import uvloop

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass

    asyncio.run(main())
