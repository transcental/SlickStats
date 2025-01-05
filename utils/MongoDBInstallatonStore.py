from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient
from slack_sdk.oauth.installation_store.async_installation_store import (
    AsyncInstallationStore,
)
from slack_sdk.oauth.installation_store.models.bot import Bot
from slack_sdk.oauth.installation_store.models.installation import Installation


class MongoDBInstallationStore(AsyncInstallationStore):
    """A MongoDB-based InstallationStore implementation

    This class is an implementation of the InstallationStore interface that uses MongoDB as a backend. It stores installation data in a collection called 'installations' in a database called 'slack'.
    """

    def __init__(
        self,
        motor_client: AsyncIOMotorClient,
        db_name: str = "slack",
        collection_name: str = "installations",
    ):
        """Initialises the MongoDBInstallationStore

        Keyword arguments:
        motor_client -- The Montor client
        db_name -- The name of the database (default 'slack')
        collection_name -- The name of the collection (default 'installations')
        """
        self.motor_client = motor_client
        self.db = motor_client[db_name]
        self.collection = self.db[collection_name]

    async def async_save(self, installation: Installation):
        """Saves the installation data for a user to the database

        Keyword arguments:

        installation -- The installation data to be saved
        """
        data = installation.to_dict()
        await self.collection.update_one(
            {
                "team_id": installation.team_id,
                "enterprise_id": installation.enterprise_id,
                "user_id": installation.user_id,
            },
            {"$set": data},
            upsert=True,
        )
        db = self.motor_client["slickstats"]
        users = db.users
        await users.update_one(
            {"user_id": installation.user_id},
            {"$set": {"user_id": installation.user_id, "enabled": True}},
            upsert=True,
        )

    async def async_find_bot(
        self,
        *,
        enterprise_id: Optional[str] = None,
        team_id: Optional[str] = None,
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Bot]:
        """Finds the bot data for a given team or enterprise ID

        Keyword arguments:

        enterprise_id -- The enterprise ID (default None)

        team_id -- The team ID (default None)

        is_enterprise_install -- Whether the installation is for an enterprise (default False)

        Returns the bot data if found, otherwise None
        """
        record = await self.collection.find_one(
            {
                "enterprise_id": enterprise_id,
                "team_id": team_id,
                "bot": {"$exists": True},
            }
        )
        if record:
            return Bot(**record["bot"])
        return None

    async def async_find_installation(
        self,
        *,
        enterprise_id: Optional[str] = None,
        team_id: Optional[str] = None,
        user_id: Optional[str] = None,
        is_enterprise_install: Optional[bool] = False,
    ) -> Optional[Installation]:
        """Finds the installation data for a given team, enterprise or user ID

        Keyword arguments:

        enterprise_id -- The enterprise ID (default None)

        team_id -- The team ID (default None)

        user_id -- The user ID (default None)

        is_enterprise_install -- Whether the installation is for an enterprise (default False)

        Returns the installation data if found, otherwise None
        """
        if user_id:
            record = await self.collection.find_one({"user_id": user_id})
        elif team_id:
            record = await self.collection.find_one({"team_id": team_id})
        else:
            record = await self.collection.find_one({"enterprise_id": enterprise_id})
        if record:
            record.pop("_id", None)
            return Installation(**record)
        return None

    async def async_delete_bot(
        self, *, enterprise_id: Optional[str] = None, team_id: Optional[str]
    ):
        """Deletes the bot data for a given team or enterprise ID from the database

        Keyword arguments:

        enterprise_id -- The enterprise ID

        team_id -- The team ID
        """
        await self.collection.update_one(
            {"enterprise_id": enterprise_id, "team_id": team_id},
            {"$unset": {"bot": ""}},
        )

    async def async_delete_installation(
        self,
        *,
        enterprise_id: Optional[str] = None,
        team_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ):
        """Deletes the installation data for a given team, enterprise or user ID from the database

        Keyword arguments:

        enterprise_id -- The enterprise ID

        team_id -- The team ID

        user_id -- The user ID

        """
        if user_id:
            query = {"user_id": user_id}
        elif team_id:
            query = {"team_id": team_id}
        else:
            query = {"enterprise_id": enterprise_id}
        await self.collection.delete_one(query)
        await self.motor_client["slickstats"].users.delete_one({"user_id": user_id})

    async def async_find_installations(
        self, *, enterprise_id: Optional[str] = None, team_id: Optional[str] = None
    ) -> list[Installation]:
        """Finds all installation data for a given team or enterprise ID from the database

        Keyword arguments:
        enterprise_id -- The enterprise ID
        team_id -- The team ID

        Returns a list of Installation objects if found, otherwise an empty list
        """
        query = {}
        if enterprise_id:
            query["enterprise_id"] = enterprise_id
        if team_id:
            query["team_id"] = team_id
        records = await self.collection.find(query).to_list()
        records = [
            {k: v for k, v in record.items() if k != "_id"} for record in records
        ]
        return [Installation(**record) for record in records]
