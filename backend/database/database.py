import asyncpg
from databases import Database as AsyncDatabase
import logging
from config import settings

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.database: AsyncDatabase = None
        self.pool: asyncpg.Pool = None
    
    async def connect(self):
        """Connect to the database."""
        try:
            self.database = AsyncDatabase(settings.database_url)
            await self.database.connect()
            logger.info("Database connected successfully")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from the database."""
        if self.database:
            await self.database.disconnect()
            logger.info("Database disconnected")
    
    async def execute(self, query: str, values: dict = None):
        """Execute a query."""
        if values:
            return await self.database.execute(query, values)
        return await self.database.execute(query)
    
    async def fetch_one(self, query: str, values: dict = None):
        """Fetch one record."""
        if values:
            return await self.database.fetch_one(query, values)
        return await self.database.fetch_one(query)
    
    async def fetch_all(self, query: str, values: dict = None):
        """Fetch all records."""
        if values:
            return await self.database.fetch_all(query, values)
        return await self.database.fetch_all(query)
