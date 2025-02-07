import logging

import aiohttp

from utils.db import update_user_settings

BASE_URL = "http://ws.audioscrobbler.com/2.0/"


async def get_playing(api_key: str, username: str) -> dict | None:
    """Returns a JSON response with the currently playing media from Last.fm

    Keyword arguments:

    api_key -- API key for the last.fm API (e.g. 1234567890abcdef1234567890abcdef)

    username -- Last.fm username (e.g. user123)

    If there's an error executing the request it returns None
    """
    url = f"{BASE_URL}?method=user.getrecenttracks&api_key={api_key}&format=json&user={username}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:
                return await res.json()
    except Exception as e:
        logging.error(e)
        return None


async def get_lastfm_status(user: dict) -> tuple[str | None, str | None]:
    """Returns a tuple with the current Last.fm media and a log message if the media has changed. If the user has no settings, is not playing anything or the request errors, returns None, None

    Keyword arguments:

    user -- A dictionary with the user's settings
    """
    if not user:
        return None, None
    api_key = user.get("lastfm_api_key")
    username = user.get("lastfm_username")
    if not api_key or not username:
        return None, None

    playing = await get_playing(api_key, username)
    if not playing:
        await update_user_settings(user.get("user_id"), {"current_song": None})
        return None, None
    current = playing.get("recenttracks", {}).get("track", [])
    if not current:
        await update_user_settings(user.get("user_id"), {"current_song": None})
        return None, None
    current = current[0]
    if current.get("@attr") and current.get("@attr").get("nowplaying"):
        new = f"{current.get('name')} - {current.get('artist')['#text']}"
        current_song = user.get("current_song")
        if current_song == new:
            return new, None
        else:
            current_song = new
            await update_user_settings(
                user.get("user_id"), {"current_song": current_song}
            )
            log_message = f"<https://last.fm/user/{username}|{username}> is listening to <{current.get('url')}|*{current.get('name')}*> by {current.get('artist')['#text']}"
            return new, log_message

    else:
        return None, None
