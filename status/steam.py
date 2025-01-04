from utils.db import update_user_settings
from utils.env import env

BASE_URL = "https://api.steampowered.com"


async def get_playing(api_key: str, user_id: str) -> dict | None:
    url = f"{BASE_URL}/ISteamUser/GetPlayerSummaries/v2/?key={api_key}&format=json&steamids={user_id}"
    try:
        async with env.aiohttp_session.get(url) as res:
            return await res.json()
    except:
        return None


async def get_steam_status(user) -> tuple[None | str, None | str]:
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
    elif current == None:
        await update_user_settings(user.get("user_id"), {"current_game": None})
        return None, None
    else:
        current_game = current
        await update_user_settings(user.get("user_id"), {"current_game": current_game})
        game_id = players[0].get("gameid")
        url = f"https://store.steampowered.com/app/{game_id}"
        log_message = f"<https://steamcommunity.com/profiles/{user_id}|{username}> is playing <{url}|*{current}*>"
        return current, log_message
