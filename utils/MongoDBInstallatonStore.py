from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient
from slack_sdk.oauth.installation_store.async_installation_store import (
    AsyncInstallationStore,
)
from slack_sdk.oauth.installation_store.models.bot import Bot
from slack_sdk.oauth.installation_store.models.installation import Installation


class MongoDBInstallationStore(AsyncInstallationStore):
    def __init__(
        self,
        mongo_client: AsyncIOMotorClient,
        db_name: str = "slack",
        collection_name: str = "installations",
    ):
        self.mongo_client = mongo_client
        self.db = mongo_client[db_name]
        self.collection = self.db[collection_name]

    async def async_save(self, installation: Installation):
        """

        :param installation: Installation:

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
        db = self.mongo_client["slickstats"]
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
        is_enterprise_install: Optional[bool] = False
    ) -> Optional[Bot]:
        """

        :param *:
        :param enterprise_id: Optional[str]:  (Default value = None)
        :param team_id: Optional[str]:  (Default value = None)
        :param is_enterprise_install: Optional[bool]:  (Default value = False)

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
        is_enterprise_install: Optional[bool] = False
    ) -> Optional[Installation]:
        """

        :param *:
        :param enterprise_id: Optional[str]:  (Default value = None)
        :param team_id: Optional[str]:  (Default value = None)
        :param user_id: Optional[str]:  (Default value = None)
        :param is_enterprise_install: Optional[bool]:  (Default value = False)

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
    ) -> None:
        """

        :param *:
        :param enterprise_id: Optional[str]:  (Default value = None)
        :param team_id: Optional[str]:

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
        user_id: Optional[str] = None
    ) -> None:
        """

        :param *:
        :param enterprise_id: Optional[str]:  (Default value = None)
        :param team_id: Optional[str]:  (Default value = None)
        :param user_id: Optional[str]:  (Default value = None)

        """
        if user_id:
            query = {"user_id": user_id}
        elif team_id:
            query = {"team_id": team_id}
        else:
            query = {"enterprise_id": enterprise_id}
        await self.collection.delete_one(query)
        await self.mongo_client["slickstats"].users.delete_one({"user_id": user_id})

    async def async_find_installations(
        self, *, enterprise_id: Optional[str] = None, team_id: Optional[str] = None
    ):
        """

        :param *:
        :param enterprise_id: Optional[str]:  (Default value = None)
        :param team_id: Optional[str]:  (Default value = None)

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
