import os

from dotenv import load_dotenv
from git import Repo
from motor.motor_asyncio import AsyncIOMotorClient
from slack_sdk.web.async_client import AsyncWebClient

from utils.MongoDBInstallatonStore import MongoDBInstallationStore

load_dotenv()


def get_git_hash(repo_path="."):
    try:
        repo = Repo(repo_path)
        commit_hash = repo.head.commit.hexsha
        return commit_hash[:7]
    except Exception as e:
        print(f"Error getting git hash: {e}")
        return None


class Environment:
    """Class to store environment variables and initialise necessary resources"""

    def __init__(self):
        """Initialises the environment variables and sets up all the required environments for the app"""
        self.slack_client_id = os.environ.get("SLACK_CLIENT_ID", "unset")
        self.slack_client_secret = os.environ.get("SLACK_CLIENT_SECRET", "unset")
        self.slack_signing_secret = os.environ.get("SLACK_SIGNING_SECRET", "unset")
        self.slack_token = os.environ.get("SLACK_TOKEN", "unset")
        self.slack_team_id = os.environ.get("SLACK_TEAM_ID", "unset")

        self.slack_heartbeat_channel = os.environ.get(
            "SLACK_HEARTBEAT_CHANNEL", "unset"
        )
        self.slack_log_channel = os.environ.get("SLACK_LOG_CHANNEL", "unset")
        self.slack_webhook_url = os.environ.get("SLACK_WEBHOOK_URL", "unset")

        self.domain = os.environ.get("DOMAIN", "unset")
        self.mongo_uri = os.environ.get("MONGO_URI", "unset")

        self.environment = os.environ.get("ENV", "development")
        self.port = int(os.environ.get("PORT", 3000))

        unset = [key for key, value in self.__dict__.items() if value == "unset"]

        if unset:
            raise ValueError(f"Missing environment variables: {', '.join(unset)}")

        self.motor_client = AsyncIOMotorClient(self.mongo_uri)
        self.installation_store = MongoDBInstallationStore(self.motor_client)

        self.slack_client = AsyncWebClient(token=self.slack_token)

        self.git_hash = get_git_hash()


env = Environment()
