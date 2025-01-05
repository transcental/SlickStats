from utils.env import env


async def update_user_settings(user_id: str, data: dict):
    """Updates the user settings in the DB via an upsert operation

    Keyword arguments:

    user_id -- The user's ID

    data -- The data to be updated in the DB
    """
    client = env.motor_client
    db = client["slickstats"]
    users = db.users
    await users.update_one({"user_id": user_id}, {"$set": data}, upsert=True)


async def get_all_users(enabled: bool = False):
    """Returns a list of all users from the DB that have the app enabled if enabled is True

    Keyword arguments:

    enabled -- If True, only returns users that have the app enabled (default False)
    """
    client = env.motor_client
    db = client["slickstats"]
    users = db.users
    all_users = await users.find().to_list()
    if enabled:
        return [user for user in all_users if user.get("enabled", True)]


async def get_user_settings(user_id: str):
    """Returns the user's settings from the DB

    Keyword arguments:

    user_id -- The user's ID
    """
    client = env.motor_client
    db = client["slickstats"]
    users = db.users
    return await users.find_one({"user_id": user_id})
