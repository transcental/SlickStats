import json
import logging
import os
import subprocess
import time

from utils.db import update_user_settings

NXAPI_PATH = "../node_modules/nxapi/.bin/nxapi"
USER_AGENT = "slick-stats (+https://github.com/transcental/slickstats)"

data = {}


async def send_friend_request(user: dict) -> bool:
    friend_code = user.get("switch_friend_code", "").removeprefix("SW-")
    try:
        env = os.environ.copy()
        env["NXAPI_USER_AGENT"] = USER_AGENT
        subprocess.run(
            [NXAPI_PATH, "nso", "add-friend", friend_code],
            capture_output=True,
            text=True,
            check=True,
            env=env,
        )

        result = subprocess.run(
            [NXAPI_PATH, "nso", "lookup", friend_code, "--json"],
            capture_output=True,
            text=True,
            check=True,
            env=env,
        )
        response = json.loads(result.stdout)
        nsa_id = response.get("nsaId")

        await update_user_settings(user.get("user_id"), {"switch_nsa_id": nsa_id})
        return True
    except Exception as e:
        logging.error(e)
        return False


def update_data() -> bool:
    global data

    try:
        env = os.environ.copy()
        env["NXAPI_USER_AGENT"] = USER_AGENT
        result = subprocess.run(
            [NXAPI_PATH, "nso", "friends", "--json"],
            capture_output=True,
            text=True,
            check=True,
        )
        data["friends"] = json.loads(result.stdout)
        if not result.stdout:
            return False
        expiry = time.time() + 30
        data["expiry"] = expiry
        return True

    except Exception as e:
        logging.error(e)
        return False


def get_playing(nsa_id: str) -> dict | None:
    global data

    if not data or time.time() > data.get("expiry", 0):
        if not update_data():
            return None

    friends = data.get("friends", [])
    friend = next((f for f in friends if f.get("nsaId") == nsa_id), None)
    if not friend:
        return None

    presence = friend.get("presence", {})
    state = presence.get("state")
    if state == "ONLINE":
        return friend
    return None


async def get_switch_status(user: dict) -> tuple[None | str, None | str]:
    """Returns a tuple with the Nintendo Switch game currently being played and a log message if the media has changed. If the user has no settings, is not playing anything or the request errors, returns None, None

    Keyword arguments:

    user -- A dictionary with the user's settings
    """
    if not user:
        return None, None
    friend_code = user.get("switch_friend_code")

    if not friend_code:
        await update_user_settings(user.get("user_id"), {"current_switch_game": None})
        return None, None
    nsa_id = user.get("switch_nsa_id")
    while not nsa_id:
        # If the user has no nsa_id, send a friend request
        if not await send_friend_request(user):
            return None, None
        nsa_id = user.get("switch_nsa_id")

    user = get_playing(nsa_id)

    if not user:
        await update_user_settings(user.get("user_id"), {"current_switch_game": None})
        return None, None

    game = user.get("presence", {}).get("game", {})
    logging.info(game)
    game_name = game.get("name", "")

    current_game = user.get("current_switch_game")
    if current_game == game_name:
        return game_name, None
    else:
        await update_user_settings(
            user.get("user_id"), {"current_switch_game": game_name}
        )

        username = user.get("name")

        log_message = f"{username} is playing {game_name}"
        return game_name, log_message
