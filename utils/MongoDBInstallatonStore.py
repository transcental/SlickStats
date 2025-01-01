from typing import Optional

from pymongo import MongoClient
from slack_sdk.oauth import InstallationStore
from slack_sdk.oauth.installation_store.models.bot import Bot
from slack_sdk.oauth.installation_store.models.installation import Installation


class MongoDBInstallationStore(InstallationStore):
    """ """

    def __init__(
        self,
        mongo_client: MongoClient,
        db_name: str = "slack",
        collection_name: str = "installations",
    ):
        self.mongo_client = mongo_client
        self.db = mongo_client[db_name]
        self.collection = self.db[collection_name]

    def save(self, installation: Installation):
        """

        :param installation: Installation:

        """
        data = installation.to_dict()
        self.collection.update_one(
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
        users.update_one(
            {"user_id": installation.user_id},
            {"$set": {"user_id": installation.user_id, "enabled": True}},
            upsert=True,
        )

    def find_bot(
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
        record = self.collection.find_one(
            {
                "enterprise_id": enterprise_id,
                "team_id": team_id,
                "bot": {"$exists": True},
            }
        )
        if record:
            return Bot(**record["bot"])
        return None

    def find_installation(
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
            record = self.collection.find_one({"user_id": user_id})
        elif team_id:
            record = self.collection.find_one({"team_id": team_id})
        else:
            record = self.collection.find_one({"enterprise_id": enterprise_id})
        if record:
            record.pop("_id", None)
            return Installation(**record)
        return None

    def delete_bot(
        self, *, enterprise_id: Optional[str] = None, team_id: Optional[str]
    ) -> None:
        """

        :param *:
        :param enterprise_id: Optional[str]:  (Default value = None)
        :param team_id: Optional[str]:

        """
        self.collection.update_one(
            {"enterprise_id": enterprise_id, "team_id": team_id},
            {"$unset": {"bot": ""}},
        )

    def delete_installation(
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
        self.collection.delete_one(query)
        self.mongo_client["slickstats"].users.delete_one({"user_id": user_id})

    def find_installations(
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
        records = self.collection.find(query)
        records = [
            {k: v for k, v in record.items() if k != "_id"} for record in records
        ]
        return [Installation(**record) for record in records]
