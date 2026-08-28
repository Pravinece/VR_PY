from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None
    
    async def connect(self):
        self.client = AsyncIOMotorClient(settings.MONGO_URL)
        self.db = self.client[settings.DB_NAME]
        await self._create_indexes()

    async def _create_indexes(self):
        await self.db["users"].create_index("emp_id", unique=True)
        await self.db["avatars"].create_index("user_id")
        await self.db["unlocked_assets"].create_index("user_id")
        
    async def close(self):
        if(self.client):
            self.client.close()
            
    async def get_database(self) -> AsyncIOMotorDatabase:
        return self.db
    
mongodb = MongoDB()
