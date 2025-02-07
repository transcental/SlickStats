import logging

import aiohttp

from utils.db import update_user_settings


async def get_playing(base_url: str, api_key: str) -> dict:
    """Returns a JSON response with the currently playing media from Jellyfin

    Keyword arguments:

    base_url -- URL of the Jellyfin server (e.g. http://localhost:8096)

    api_key -- API key for the Jellyfin server (e.g. 1234567890abcdef1234567890abcdef)

    If there's an error executing the request it returns an empty dictionary.
    """
    url = f"{base_url}/Sessions?active=true"
    try:
        async with aiohttp.ClientSession().get(
            url, headers={"X-Emby-Token": api_key}
        ) as res:
            return await res.json()
    except Exception as e:
        logging.error(e)
        return {}


async def get_jellyfin_status(user: dict) -> tuple[str | None, str | None]:
    """Returns a tuple with the current Jellyfin media and a log message if the media has changed. If the user has no settings, is not playing anything, the media isn't a Movie or Episode or the request errors, returns None, None

    Keyword arguments:

    user -- A dictionary with the user's settings
    """
    if not user:
        return None, None
    base_url = user.get("jellyfin_url")
    api_key = user.get("jellyfin_api_key")
    username = user.get("jellyfin_username")
    if not base_url or not api_key or not username:
        await update_user_settings(user.get("user_id"), {"current_jellyfin": None})
        return None, None

    sessions = await get_playing(base_url, api_key) or []
    res = None
    for session in sessions:
        if session.get("UserName") == username and session.get("NowPlayingItem"):
            res = session
            break

    if not res:
        await update_user_settings(user.get("user_id"), {"current_jellyfin": None})
        return None, None

    type = res.get("NowPlayingItem", {}).get("Type")
    if type not in ["Movie", "Episode"]:
        await update_user_settings(user.get("user_id"), {"current_jellyfin": None})
        return None, None
    current = (
        res.get("NowPlayingItem", {}).get("Name")
        if type == "Movie"
        else f"{res.get('NowPlayingItem', {}).get('SeriesName')}: {res.get('NowPlayingItem', {}).get('Name')}"
    )
    if not current:
        await update_user_settings(user.get("user_id"), {"current_jellyfin": None})
        return None, None

    datestring = res.get("NowPlayingItem", {}).get("PremiereDate")
    year = datestring.split("-")[0] if datestring else None

    new = f"{current} ({year})" if year else current

    current_jellyfin = user.get("current_jellyfin")
    if current_jellyfin == new:
        return current, None
    else:
        current_jellyfin = new
        await update_user_settings(
            user.get("user_id"), {"current_jellyfin": current_jellyfin}
        )
        external_urls = res.get("NowPlayingItem", {}).get("ExternalUrls", [])
        imdb = next(
            (url.get("Url") for url in external_urls if url.get("Name") == "IMDb")
        )
        if imdb:
            dynamic_msg = (
                f"<{imdb}|*{current}*> ({year})" if year else f"<{imdb}|*{current}*>"
            )
        else:
            dynamic_msg = f"*{current}* ({year})" if year else current
        log_message = f"{username} is watching {dynamic_msg}"
        return current_jellyfin, log_message
