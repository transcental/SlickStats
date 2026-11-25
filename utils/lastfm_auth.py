"""Last.fm web authentication ("OAuth app") helpers.

Flow (https://www.last.fm/api/webauth):
1. Send the user to https://www.last.fm/api/auth/?api_key=KEY&cb=CALLBACK
2. Last.fm redirects back to CALLBACK with ?token=TOKEN once they allow access
3. Exchange the token for a session key with the signed auth.getSession call

The session key never expires unless the user revokes access on Last.fm.
"""

import hashlib
import hmac
import logging
import time
from urllib.parse import urlencode

import aiohttp

from utils.env import env

API_URL = "https://ws.audioscrobbler.com/2.0/"
AUTH_URL = "https://www.last.fm/api/auth/"
CALLBACK_PATH = "/lastfm/callback"

# How long a "Connect Last.fm" link stays valid: links in the app home are
# regenerated every time it opens, links sent by DM need to last longer
STATE_MAX_AGE = 60 * 60 * 24
DM_STATE_MAX_AGE = 60 * 60 * 24 * 30


def sign(params: dict) -> str:
    """Returns the api_sig for a set of Last.fm API parameters.

    Parameters are sorted alphabetically, concatenated as <name><value>, the
    shared secret is appended and the result is md5 hashed. `format` and
    `callback` are not part of the signature.
    """
    raw = "".join(
        f"{key}{params[key]}"
        for key in sorted(params)
        if key not in ("format", "callback")
    )
    raw += env.lastfm_shared_secret
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def _state_mac(payload: str) -> str:
    return hmac.new(
        env.lastfm_shared_secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()[:32]


def make_state(user_id: str, max_age: int = STATE_MAX_AGE) -> str:
    """Returns a signed, URL-safe state tying a callback to a Slack user"""
    payload = f"{user_id}.{int(time.time()) + max_age}"
    return f"{payload}.{_state_mac(payload)}"


def read_state(state: str) -> str | None:
    """Returns the Slack user ID from a state, or None if it's forged or expired"""
    try:
        user_id, expires, mac = state.split(".")
        expires_at = int(expires)
    except ValueError:
        return None
    if not hmac.compare_digest(mac, _state_mac(f"{user_id}.{expires}")):
        return None
    if time.time() > expires_at:
        return None
    return user_id


def callback_url(state: str) -> str:
    # The state lives in the path rather than the query string because Last.fm
    # appends ?token=... to the callback URL itself.
    return f"{env.domain}{CALLBACK_PATH}/{state}"


def auth_url(user_id: str, max_age: int = STATE_MAX_AGE) -> str:
    """Returns the Last.fm URL a Slack user visits to connect their account"""
    query = urlencode(
        {
            "api_key": env.lastfm_api_key,
            "cb": callback_url(make_state(user_id, max_age)),
        }
    )
    return f"{AUTH_URL}?{query}"


async def get_session(token: str) -> dict | None:
    """Exchanges an auth token for a session.

    Returns {"name": <username>, "key": <session key>, ...} or None on error.
    """
    params = {
        "method": "auth.getSession",
        "api_key": env.lastfm_api_key,
        "token": token,
    }
    params["api_sig"] = sign(params)
    params["format"] = "json"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, data=params) as res:
                data = await res.json(content_type=None)
    except Exception as e:
        logging.error(f"Last.fm auth.getSession failed: {e}")
        return None
    if "session" not in data:
        logging.error(f"Last.fm auth.getSession error: {data}")
        return None
    return data["session"]
