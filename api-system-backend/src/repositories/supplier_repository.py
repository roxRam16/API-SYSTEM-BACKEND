from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from src.repositories.base import BaseRepository
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

class SupplierRepository(BaseRepository):
    """Supplier repository implementing specific supplier operations"""
    
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection)
    
    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get supplier by email"""
        try:
            document = await self.collection.find_one({"email": email, "is_active": True})
            if document:
                document["_id"] = str(document["_id"])
            return document
        except Exception as e:
            logger.error(f"Error getting supplier by email {email}: {e}")
            raise e
    
    async def get_by_tax_id(self, tax_id: str) -> Optional[Dict[str, Any]]:
        """Get supplier by tax ID"""
        try:
            document = await self.collection.find_one({"tax_id": tax_id, "is_active": True})
            if document:
                document["_id"] = str(document["_id"])
            return document
        except Exception as e:
            logger.error(f"Error getting supplier by tax ID {tax_id}: {e}")
            raise e
    
    async def search_suppliers(self, search_term: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search suppliers by name, email, or contact person"""
        try:
            query = {
                "$and": [
                    {"is_active": True},
                    {
                        "$or": [
                            {"name": {"$regex": search_term, "$options": "i"}},
                            {"email": {"$regex": search_term, "$options": "i"}},
                            {"contact_person": {"$regex": search_term, "$options": "i"}},
                            {"phone": {"$regex": search_term, "$options": "i"}}
                        ]
                    }
                ]
            }
            
            cursor = self.collection.find(query).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            for doc in documents:
                doc["_id"] = str(doc["_id"])
            
            logger.info(f"Found {len(documents)} suppliers for search term: {search_term}")
            return documents
        except Exception as e:
            logger.error(f"Error searching suppliers with term {search_term}: {e}")
            raise e
    
    async def update_balance(self, supplier_id: str, amount: float) -> bool:
        """Update supplier balance"""
        try:
            if not ObjectId.is_valid(supplier_id):
                return False
            
            result = await self.collection.update_one(
                {"_id": ObjectId(supplier_id)},
                {"$inc": {"current_balance": amount}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating balance for supplier {supplier_id}: {e}")
            raise e