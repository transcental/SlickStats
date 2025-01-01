from utils.env import env


def update_user_settings(user_id, data):
    """

    :param user_id:
    :param data:

    """
    client = env.mongo_client
    db = client["slickstats"]
    users = db.users
    users.update_one({"user_id": user_id}, {"$set": data}, upsert=True)


def get_all_users(enabled: bool = False):
    """ """
    client = env.mongo_client
    db = client["slickstats"]
    users = db.users
    all_users = users.find()
    if enabled:
        return [user for user in all_users if user.get("enabled", True)]


def get_user_settings(user_id):
    """

    :param user_id:

    """
    client = env.mongo_client
    db = client["slickstats"]
    users = db.users
    return users.find_one({"user_id": user_id})
