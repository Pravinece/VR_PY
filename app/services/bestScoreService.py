import logging
import math
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.userModel import UserBestScoreModel
from app.schema.bestScoreSchema import BestScoreLeaderboardRes, BestScoreEntry, CurrentUserBestScore, BestScoreUser

logger = logging.getLogger(__name__)


class BestScoreService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["user_best_scores"]

    async def upsert_best_score(self, user_id: str, game_type: str, mode: str, score: int, time_taken: int, session_id: str, session=None):
        existing = await self.collection.find_one({"user_id": user_id, "game_type": game_type, "mode": mode}, session=session)
        if not existing:
            doc = UserBestScoreModel(
                user_id=user_id,
                game_type=game_type,
                mode=mode,
                best_score=score,
                time_taken=time_taken,
                session_id=session_id,
                achieved_at=datetime.now(timezone.utc),
            )
            await self.collection.insert_one(doc.model_dump(by_alias=True), session=session)
        elif score > existing["best_score"]:
            await self.collection.update_one(
                {"_id": existing["_id"]},
                {"$set": {"best_score": score, "time_taken": time_taken, "session_id": session_id, "achieved_at": datetime.now(timezone.utc)}},
                session=session,
            )

    async def get_best_user(self, game_type: str, mode: str, page: int, limit: int):
        skip = (page - 1) * limit
        total = await self.collection.count_documents({"game_type": game_type, "mode": mode})
        docs = await self.collection.find(
            {"game_type": game_type, "mode": mode}
        ).sort("best_score", -1).skip(skip).limit(limit).to_list(length=limit)
        return {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": math.ceil(total / limit) if total > 0 else 0,
            "results": docs,
        }
    
    async def get_my_best_scores(self, user_id: str, game_type: str, mode: str):
        return await self.collection.find_one({"user_id": user_id, "game_type": game_type, "mode": mode})

    async def get_leaderboard(self, game_type: str, mode: str, page: int, limit: int, current_user_id: str) -> BestScoreLeaderboardRes:
        paginated = await self.get_best_user(game_type, mode, page, limit)
        my_score = await self.get_my_best_scores(current_user_id, game_type, mode)

        # collect all user_ids and fetch in one query
        user_ids = [doc["user_id"] for doc in paginated["results"]]
        users_collection = self.collection.database["users"]
        user_docs = await users_collection.find({"_id": {"$in": user_ids}}).to_list(length=None)
        user_map = {u["_id"]: u for u in user_docs}

        if my_score:
            rank = await self.collection.count_documents({
                "game_type": game_type,
                "mode": mode,
                "best_score": {"$gt": my_score["best_score"]},
            }) + 1
            current_user = CurrentUserBestScore(
                rank=rank,
                best_score=my_score["best_score"],
                time_taken=my_score.get("time_taken"),
                session_id=my_score["session_id"],
                achieved_at=my_score["achieved_at"],
            )
        else:
            current_user = CurrentUserBestScore()

        results = [
            BestScoreEntry(
                id=str(doc["_id"]),
                user=BestScoreUser(
                    id=doc["user_id"],
                    username=user_map[doc["user_id"]]["username"] if doc["user_id"] in user_map else "Unknown",
                    emp_id=user_map[doc["user_id"]]["emp_id"] if doc["user_id"] in user_map else "",
                ),
                game_type=doc["game_type"],
                mode=doc["mode"],
                best_score=doc["best_score"],
                time_taken=doc.get("time_taken", 0),
                session_id=doc["session_id"],
                achieved_at=doc["achieved_at"],
            )
            for doc in paginated["results"]
        ]

        return BestScoreLeaderboardRes(
            total=paginated["total"],
            page=paginated["page"],
            limit=paginated["limit"],
            total_pages=paginated["total_pages"],
            current_user=current_user,
            results=results,
        )
    
        
    async def get_user_count(self):
        skating = await get_user_count_by_game(self, "skating")
        clean_deal = await get_user_count_by_game(self, "cleandeal")
        return {"skating_count" : skating, "clean_deal_count": clean_deal, "total_user": (skating+clean_deal)}
            
        
        
async def get_user_count_by_game(self, game_type):
    count = await self.collection.count_documents(filter={"game_type": game_type})
    return count
