import threading

from utils.db import get_all_users
from utils.env import env
from utils.slack import log_to_slack
from utils.slack import STATUSES
from utils.slack import update_slack_pfp
from utils.slack import update_slack_status


def update_status():
    """ """
    threading.Timer(25, update_status).start()
    users = get_all_users(enabled=True)
    if not users:
        print("No users found")
        return

    for user in users:
        set = False
        installation = env.installation_store.find_installation(
            user_id=user.get("user_id")
        )
        if not installation:
            print("No installation found for user", user.get("user_id"))
            continue
        bot_token = installation.bot_token
        user_token = installation.user_token
        user_id = user.get("user_id")
        current_pfp = user.get("pfp")
        for status in STATUSES:
            custom, log_message = status.get(
                "function",
                lambda _: print(
                    f'Failed to run status fetching function for {status.get("name")}'
                ),
            )(user)
            if log_message:
                log_to_slack(log_message, bot_token)

            if custom:
                update_slack_status(
                    status.get("emoji"),
                    status.get("status", "").replace("(custom)", custom),
                    user_id=user_id,
                    token=user_token,
                )
                update_slack_pfp(
                    new_pfp_type=status.get("pfp"),
                    current_pfp=current_pfp,
                    user_id=user_id,
                    bot_token=bot_token,
                    token=user_token,
                    img_url=user.get(status.get("pfp"), None),
                )
                set = True
                break

        if not set or current_pfp is None:
            if current_pfp == "huddle_pfp":
                return
            update_slack_status(emoji="", status="", user_id=user_id, token=user_token)
            update_slack_pfp(
                new_pfp_type="default_pfp",
                current_pfp=current_pfp,
                user_id=user_id,
                bot_token=bot_token,
                token=user_token,
                img_url=user.get("default_pfp", None),
            )
