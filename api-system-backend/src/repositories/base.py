from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from datetime import datetime

class BaseRepository(ABC):
    """Abstract base repository implementing Repository pattern"""
    
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection
    
    async def create(self, document: Dict[str, Any]) -> str:
        """Create a new document"""
        document["created_at"] = datetime.utcnow()
        document["updated_at"] = datetime.utcnow()
        document["is_active"] = True
        
        result = await self.collection.insert_one(document)
        return str(result.inserted_id)
    
    async def get_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID"""
        if not ObjectId.is_valid(document_id):
            return None
        
        document = await self.collection.find_one({"_id": ObjectId(document_id)})
        if document:
            document["_id"] = str(document["_id"])
        return document
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get all documents with pagination and filters"""
        query = filters or {}
        cursor = self.collection.find(query).skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)
        
        for doc in documents:
            doc["_id"] = str(doc["_id"])
        
        return documents
    
    async def update(self, document_id: str, update_data: Dict[str, Any]) -> bool:
        """Update document by ID"""
        if not ObjectId.is_valid(document_id):
            return False
        
        update_data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    async def deactivate(self, document_id: str) -> bool:
        """Soft delete document by ID"""
        if not ObjectId.is_valid(document_id):
            return False
        
        result = await self.collection.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        
        return result.modified_count > 0
    
    async def activate(self, document_id: str) -> bool:
        """Soft activate document by ID"""
        if not ObjectId.is_valid(document_id):
            return False
        
        result = await self.collection.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": {"is_active": True, "updated_at": datetime.utcnow()}}
        )
        
        return result.modified_count > 0
    
    async def hard_delete(self, document_id: str) -> bool:
        """Hard delete document by ID"""
        if not ObjectId.is_valid(document_id):
            return False
        
        result = await self.collection.delete_one({"_id": ObjectId(document_id)})
        return result.deleted_count > 0
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count documents with filters"""
        query = filters or {}
        return await self.collection.count_documents(query)
    
    async def exists(self, filters: Dict[str, Any]) -> bool:
        """Check if document exists with given filters"""
        count = await self.collection.count_documents(filters, limit=1)
        return count > 0