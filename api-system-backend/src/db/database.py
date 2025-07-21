from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from src.core.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    """Singleton Database Connection Manager"""
    _instance: Optional['Database'] = None
    _client: Optional[AsyncIOMotorClient] = None
    _database = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    async def connect_to_mongo(self):
        """Create database connection"""
        try:
            if self._client is None:
                logger.info(f"Connecting to MongoDB: {settings.MONGODB_URL}")
                self._client = AsyncIOMotorClient(
                    settings.MONGODB_URL,
                    serverSelectionTimeoutMS=5000,  # 5 second timeout
                    connectTimeoutMS=10000,  # 10 second timeout
                    socketTimeoutMS=10000,   # 10 second timeout
                )
                
                # Test the connection
                await self._client.admin.command('ping')
                
                self._database = self._client[settings.DATABASE_NAME]
                logger.info(f"Successfully connected to MongoDB database: {settings.DATABASE_NAME}")
                
                # Create indexes if needed
                await self._create_indexes()
                
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise e
    
    async def _create_indexes(self):
        """Create necessary indexes for better performance"""
        try:
            # Users collection indexes
            users_collection = self._database.users
            await users_collection.create_index("email", unique=True)
            await users_collection.create_index("username", unique=True)
            
            # Products collection indexes
            products_collection = self._database.products
            await products_collection.create_index("sku", unique=True)
            await products_collection.create_index("barcode")
            await products_collection.create_index("name")
            await products_collection.create_index("category")
            
            # Customers collection indexes
            customers_collection = self._database.customers
            await customers_collection.create_index("email", unique=True)
            await customers_collection.create_index("tax_id", unique=True)
            await customers_collection.create_index("name")
            
            # Suppliers collection indexes
            suppliers_collection = self._database.suppliers
            await suppliers_collection.create_index("email", unique=True)
            await suppliers_collection.create_index("tax_id", unique=True)
            await suppliers_collection.create_index("name")
            
            # Sales collection indexes
            sales_collection = self._database.sales
            await sales_collection.create_index("sale_number", unique=True)
            await sales_collection.create_index("customer_id")
            await sales_collection.create_index("cashier_id")
            await sales_collection.create_index("sale_date")
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Error creating indexes: {e}")
    
    async def close_mongo_connection(self):
        """Close database connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
            logger.info("Disconnected from MongoDB")
    
    def get_database(self):
        """Get database instance"""
        if self._database is None:
            raise Exception("Database not connected. Call connect_to_mongo() first.")
        return self._database
    
    def get_collection(self, collection_name: str):
        """Get collection instance"""
        if self._database is None:
            raise Exception("Database not connected")
        return self._database[collection_name]
    
    async def health_check(self):
        """Check database connection health"""
        try:
            if self._client:
                await self._client.admin.command('ping')
                return True
            return False
        except Exception:
            return False

# Global database instance
database = Database()

async def get_database():
    """Dependency to get database instance"""
    db = database.get_database()
    if db is None:
        raise Exception("Database connection not available")
    return db