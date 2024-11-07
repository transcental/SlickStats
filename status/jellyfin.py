import requests
from utils.db import update_user_settings


def get_playing(base_url: str, api_key: str) -> dict:
    url = f"{base_url}/Sessions?active=true"
    try:
        response = requests.get(url, headers={
            "X-Emby-Token": api_key,
        })
        return response.json()
    except Exception as e:
        print(e)
        return {}


def get_jellyfin_status(user) -> tuple[str | None, str | None]:
    if not user:
        return None, None
    base_url = user.get("jellyfin_url")
    api_key = user.get("jellyfin_api_key")
    username = user.get("jellyfin_username")
    if not base_url or not api_key or not username:
        return None, None

    sessions = get_playing(base_url, api_key) or []
    res = None
    for session in sessions:
        if session.get("UserName") == username and session.get("NowPlayingItem"):
            res = session
            break
    
    if not res:
        return None, None
    
    type = res.get("NowPlayingItem", {}).get("Type")
    if type not in ["Movie", "Episode"]:
        return None, None
    current = res.get("NowPlayingItem", {}).get("Name") if type == "Movie" else f"{res.get('NowPlayingItem', {}).get('SeriesName')} - {res.get('NowPlayingItem', {}).get('Name')}"
    if not current:
        return None, None
    
    datestring = res.get("NowPlayingItem", {}).get("PremiereDate")
    year = datestring.split("-")[0] if datestring else None

    new = f"{current} ({year})" if year else current
    
    current_jellyfin = user.get("current_jellyfin")
    if current_jellyfin == new:
        return current, None
    else:
        current_jellyfin = new
        update_user_settings(user.get("user_id"), {"current_jellyfin": current_jellyfin})
        log_message = f"Jellyfin: {username} is watching {new}"
        return current_jellyfin, log_message
