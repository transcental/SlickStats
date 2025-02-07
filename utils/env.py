import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from utils.MongoDBInstallatonStore import MongoDBInstallationStore

load_dotenv()


class Environment:
    """Class to store environment variables and initialise necessary resources"""

    def __init__(self):
        """Initialises the environment variables and sets up all the required environments for the app"""
        self.slack_client_id = os.environ.get("SLACK_CLIENT_ID", "unset")
        self.slack_client_secret = os.environ.get("SLACK_CLIENT_SECRET", "unset")
        self.slack_signing_secret = os.environ.get("SLACK_SIGNING_SECRET", "unset")

        self.slack_log_channel = os.environ.get("SLACK_LOG_CHANNEL", "unset")

        self.mongo_uri = os.environ.get("MONGO_URI", "unset")

        self.environment = os.environ.get("ENV", "development")
        self.port = int(os.environ.get("PORT", 3000))

        unset = [key for key, value in self.__dict__.items() if value == "unset"]

        if unset:
            raise ValueError(f"Missing environment variables: {', '.join(unset)}")

        self.motor_client = AsyncIOMotorClient(self.mongo_uri)
        self.installation_store = MongoDBInstallationStore(self.motor_client)


env = Environment()
