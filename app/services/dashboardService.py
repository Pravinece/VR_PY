import logging
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.schema.dashboardSchema import GameStatsRes, MonthlyGameStat
from app.core.exception import AppException

logger = logging.getLogger(__name__)

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


class DashboardService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.skate_collection = db["skate_sessions"]
        self.cleandeal_collection = db["cleandeal_sessions"]

    async def get_monthly_game_stats(self) -> GameStatsRes:
        try:
            current_year = datetime.now(timezone.utc).year
            start = datetime(current_year, 1, 1, tzinfo=timezone.utc)
            end = datetime(current_year + 1, 1, 1, tzinfo=timezone.utc)

            pipeline = [
                {"$match": {"played_at": {"$gte": start, "$lt": end}}},
                {"$group": {"_id": {"$month": "$played_at"}, "count": {"$sum": 1}}},
            ]

            skate_docs, cleandeal_docs = await self._run_both(pipeline)

            skate_map = {doc["_id"]: doc["count"] for doc in skate_docs}
            cleandeal_map = {doc["_id"]: doc["count"] for doc in cleandeal_docs}

            months = [
                MonthlyGameStat(
                    month=MONTH_NAMES[i],
                    skating=skate_map.get(i + 1, 0),
                    cleandeal=cleandeal_map.get(i + 1, 0),
                )
                for i in range(12)
            ]

            return GameStatsRes(year=current_year, months=months)

        except AppException:
            raise
        except Exception:
            logger.exception("Unexpected error in get_monthly_game_stats")
            raise AppException(status_code=500, message="Failed to fetch game stats")

    async def _run_both(self, pipeline):
        skate_docs = await self.skate_collection.aggregate(pipeline).to_list(length=12)
        cleandeal_docs = await self.cleandeal_collection.aggregate(pipeline).to_list(length=12)
        return skate_docs, cleandeal_docs
