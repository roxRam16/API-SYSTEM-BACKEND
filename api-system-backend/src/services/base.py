from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

class BaseService(ABC):
    """Abstract base service implementing Service pattern"""
    
    def __init__(self, repository):
        self.repository = repository
    
    @abstractmethod
    async def create(self, data: Dict[str, Any]) -> str:
        """Create new entity"""
        pass
    
    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get entity by ID"""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all entities"""
        pass
    
    @abstractmethod
    async def update(self, entity_id: str, data: Dict[str, Any]) -> bool:
        """Update entity"""
        pass

        
    @abstractmethod
    async def deactivate(self, entity_id: str) -> bool:
        """Deactivate entity"""
        pass

        
    @abstractmethod
    async def activate(self, entity_id: str) -> bool:
        """Activate entity"""
        pass
    
    # @abstractmethod
    # async def delete(self, entity_id: str) -> bool:
    #     """Delete entity"""
    #     pass