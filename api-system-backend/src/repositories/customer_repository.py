from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from src.repositories.base import BaseRepository
from bson import ObjectId

class CustomerRepository(BaseRepository):
    """Customer repository implementing specific customer operations"""
    
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection)
    
    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get customer by email"""
        document = await self.collection.find_one({"email": email, "is_active": True})
        if document:
            document["_id"] = str(document["_id"])
        return document
    
    async def get_by_tax_id(self, tax_id: str) -> Optional[Dict[str, Any]]:
        """Get customer by tax ID"""
        document = await self.collection.find_one({"tax_id": tax_id, "is_active": True})
        if document:
            document["_id"] = str(document["_id"])
        return document
    
    async def search_customers(self, search_term: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search customers by name, email, or phone"""
        query = {
            "$and": [
                {"is_active": True},
                {
                    "$or": [
                        {"name": {"$regex": search_term, "$options": "i"}},
                        {"email": {"$regex": search_term, "$options": "i"}},
                        {"phone": {"$regex": search_term, "$options": "i"}}
                    ]
                }
            ]
        }
        
        cursor = self.collection.find(query).limit(limit)
        documents = await cursor.to_list(length=limit)
        
        for doc in documents:
            doc["_id"] = str(doc["_id"])
        
        return documents
    
    async def update_balance(self, customer_id: str, amount: float) -> bool:
        """Update customer balance"""
        result = await self.collection.update_one(
            {"_id": ObjectId(customer_id)},
            {"$inc": {"current_balance": amount}}
        )
        return result.modified_count > 0