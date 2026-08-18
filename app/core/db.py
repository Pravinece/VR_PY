from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None
    
    async def connect(self):
        self.client = AsyncIOMotorClient(settings.MONGO_URL)
        self.db = self.client[settings.DB_NAME]
        
    async def close(self):
        if(self.client):
            self.client.close()
            
    async def get_database(self) -> AsyncIOMotorDatabase:
        return self.db
    
mongodb = MongoDB()
