import requests
from utils.db import update_user_settings

BASE_URL = "https://api.steampowered.com"


def get_playing(api_key: str, user_id: str) -> dict | None:
    url = f"{BASE_URL}/ISteamUser/GetPlayerSummaries/v2/?key={api_key}&format=json&steamids={user_id}"
    response = requests.get(url)
    try:
        return response.json()
    except:
        return None


def get_steam_status(user) -> tuple[None | str, None | str]:
    if not user:
        return None, None
    api_key = user.get("steam_api_key")
    user_id = user.get("steam_id")
    if not api_key or not user_id:
        return None, None
    playing = get_playing(api_key, user_id)
    if not playing:
        return None, None
    players = playing.get("response", {}).get("players", [])
    if not players:
        return None, None
    current = players[0].get("gameextrainfo")
    username = players[0].get("personaname")
    current_game = user.get("current_game")
    if current_game == current:
        return current, None
    else:
        current_game = current
        update_user_settings(user.get("user_id"), {"current_game": current_game})
        log_message = f"Steam: <https://steamcommunity.com/profiles/{user_id}|{username}> is playing {current}"
        return current, log_message
