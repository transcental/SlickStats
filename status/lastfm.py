import logging

import aiohttp

from utils.db import update_user_settings
from utils.env import env
from utils.lastfm_auth import API_URL


async def get_playing(username: str) -> dict | None:
    """Returns a JSON response with the currently playing media from Last.fm

    Uses the app's own API key (LASTFM_API_KEY), so users don't need their own.

    Keyword arguments:

    username -- Last.fm username (e.g. user123)

    If there's an error executing the request it returns None
    """
    params = {
        "method": "user.getrecenttracks",
        "api_key": env.lastfm_api_key,
        "user": username,
        "format": "json",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params=params) as res:
                return await res.json(content_type=None)
    except Exception as e:
        logging.error(e)
        return None


async def get_lastfm_status(user: dict) -> tuple[str | None, str | None]:
    """Returns a tuple with the current Last.fm media and a log message if the media has changed. If the user has no settings, is not playing anything or the request errors, returns None, None

    Keyword arguments:

    user -- A dictionary with the user's settings
    """
    if not user or not env.lastfm_enabled:
        return None, None
    # Set when the user connects through Last.fm. Users from before the switch
    # still have a username they typed in, which keeps working until they
    # connect, since recent tracks are public.
    username = user.get("lastfm_username")
    if not username:
        return None, None

    playing = await get_playing(username)
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
