from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from src.repositories.base import BaseRepository
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

class ProductRepository(BaseRepository):
    """Product repository implementing specific product operations"""
    
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection)
    
    async def get_by_sku(self, sku: str) -> Optional[Dict[str, Any]]:
        """Get product by SKU"""
        try:
            document = await self.collection.find_one({"sku": sku, "is_active": True})
            if document:
                document["_id"] = str(document["_id"])
            return document
        except Exception as e:
            logger.error(f"Error getting product by SKU {sku}: {e}")
            raise e
    
    async def get_by_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Get product by barcode"""
        try:
            document = await self.collection.find_one({"barcode": barcode, "is_active": True})
            if document:
                document["_id"] = str(document["_id"])
            return document
        except Exception as e:
            logger.error(f"Error getting product by barcode {barcode}: {e}")
            raise e
    
    async def search_products(self, search_term: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search products by name, SKU, or barcode"""
        try:
            query = {
                "$and": [
                    {"is_active": True},
                    {
                        "$or": [
                            {"name": {"$regex": search_term, "$options": "i"}},
                            {"sku": {"$regex": search_term, "$options": "i"}},
                            {"barcode": {"$regex": search_term, "$options": "i"}},
                            {"category": {"$regex": search_term, "$options": "i"}}
                        ]
                    }
                ]
            }
            
            cursor = self.collection.find(query).limit(limit)
            print(cursor)
            documents = await cursor.to_list(length=limit)
            
            for doc in documents:
                doc["_id"] = str(doc["_id"])
            
            logger.info(f"Found {len(documents)} products for search term: {search_term}")
            return documents
        except Exception as e:
            logger.error(f"Error searching products with term {search_term}: {e}")
            raise e
    
    async def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get products by category"""
        try:
            query = {"category": category, "is_active": True}
            cursor = self.collection.find(query)
            documents = await cursor.to_list(length=None)
            
            for doc in documents:
                doc["_id"] = str(doc["_id"])
            
            return documents
        except Exception as e:
            logger.error(f"Error getting products by category {category}: {e}")
            raise e
    
    async def get_low_stock_products(self) -> List[Dict[str, Any]]:
        """Get products with low stock"""
        try:
            query = {
                "$and": [
                    {"is_active": True},
                    {"$expr": {"$lte": ["$stock_quantity", "$min_stock_level"]}}
                ]
            }
            
            cursor = self.collection.find(query)
            documents = await cursor.to_list(length=None)
            
            for doc in documents:
                doc["_id"] = str(doc["_id"])
            
            return documents
        except Exception as e:
            logger.error(f"Error getting low stock products: {e}")
            raise e
    
    async def update_stock(self, product_id: str, quantity_change: int) -> bool:
        """Update product stock quantity"""
        try:
            if not ObjectId.is_valid(product_id):
                return False
            
            result = await self.collection.update_one(
                {"_id": ObjectId(product_id)},
                {"$inc": {"stock_quantity": quantity_change}}
            )
            
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating stock for product {product_id}: {e}")
            raise e
    
    async def sku_exists(self, sku: str, exclude_id: Optional[str] = None) -> bool:
        """Check if SKU already exists"""
        try:
            query = {"sku": sku, "is_active": True}
            if exclude_id and ObjectId.is_valid(exclude_id):
                query["_id"] = {"$ne": ObjectId(exclude_id)}
            return await self.exists(query)
        except Exception as e:
            logger.error(f"Error checking SKU existence {sku}: {e}")
            raise e