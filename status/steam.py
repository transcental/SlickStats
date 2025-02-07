import logging

import aiohttp

from utils.db import update_user_settings

BASE_URL = "https://api.steampowered.com"


async def get_playing(api_key: str, user_id: str) -> dict | None:
    """Returns a JSON response with the currently playing game from Steam

    Keyword arguments:

    api_key -- API key for the Steam API (e.g. 1234567890abcdef1234567890abcdef)

    user_id -- Steam User ID (e.g. 76561198012345678)

    If there's an error executing the request it returns None
    """
    url = f"{BASE_URL}/ISteamUser/GetPlayerSummaries/v2/?key={api_key}&format=json&steamids={user_id}"
    try:
        async with aiohttp.ClientSession().get(url) as res:
            return await res.json()
    except Exception as e:
        logging.error(e)
        return None


async def get_steam_status(user: dict) -> tuple[None | str, None | str]:
    """Returns a tuple with the Steam game currently being played and a log message if the media has changed. If the user has no settings, is not playing anything or the request errors, returns None, None

    Keyword arguments:

    user -- A dictionary with the user's settings
    """
    if not user:
        return None, None
    api_key = user.get("steam_api_key")
    user_id = user.get("steam_id")
    if not api_key or not user_id:
        await update_user_settings(user.get("user_id"), {"current_game": None})
        return None, None
    playing = await get_playing(api_key, user_id)
    if not playing:
        await update_user_settings(user.get("user_id"), {"current_game": None})
        return None, None
    players = playing.get("response", {}).get("players", [])
    if not players:
        await update_user_settings(user.get("user_id"), {"current_game": None})
        return None, None
    current = players[0].get("gameextrainfo")
    username = players[0].get("personaname")
    current_game = user.get("current_game")
    if current_game == current:
        return current, None
    elif current is None:
        await update_user_settings(user.get("user_id"), {"current_game": None})
        return None, None
    else:
        current_game = current
        await update_user_settings(user.get("user_id"), {"current_game": current_game})
        game_id = players[0].get("gameid")
        url = f"https://store.steampowered.com/app/{game_id}"
        log_message = f"<https://steamcommunity.com/profiles/{user_id}|{username}> is playing <{url}|*{current}*>"
        return current, log_message
