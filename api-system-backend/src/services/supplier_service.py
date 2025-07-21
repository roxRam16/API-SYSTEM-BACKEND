from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from src.services.base import BaseService
from src.repositories.supplier_repository import SupplierRepository
from src.models.supplier import SupplierCreate, SupplierUpdate
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SupplierService(BaseService):
    """Supplier service implementing business logic"""
    
    def __init__(self, repository: SupplierRepository):
        super().__init__(repository)
        self.repository = repository
    
    async def create(self, supplier_data: SupplierCreate) -> str:
        """Create new supplier"""
        try:
            # Check if email already exists
            existing_supplier = await self.repository.get_by_email(supplier_data.email)
            if existing_supplier:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Check if tax ID already exists
            existing_tax_id = await self.repository.get_by_tax_id(supplier_data.tax_id)
            if existing_tax_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tax ID already registered"
                )
            
            # Prepare supplier document
            supplier_dict = supplier_data.dict()
            supplier_dict["created_at"] = datetime.utcnow()
            supplier_dict["updated_at"] = datetime.utcnow()
            supplier_dict["is_active"] = True
            supplier_dict["current_balance"] = 0.0
            
            logger.info(f"Creating supplier with data: {supplier_dict}")
            supplier_id = await self.repository.create(supplier_dict)
            logger.info(f"Supplier created with ID: {supplier_id}")
            
            return supplier_id
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in supplier service create: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create supplier: {str(e)}"
            )
    
    async def get_by_id(self, supplier_id: str) -> Optional[Dict[str, Any]]:
        """Get supplier by ID"""
        try:
            return await self.repository.get_by_id(supplier_id)
        except Exception as e:
            logger.error(f"Error getting supplier by ID {supplier_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving supplier"
            )
    
    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get supplier by email"""
        try:
            return await self.repository.get_by_email(email)
        except Exception as e:
            logger.error(f"Error getting supplier by email {email}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving supplier"
            )
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all suppliers"""
        try:
            return await self.repository.get_all(skip=skip, limit=limit, filters={"is_active": True})
        except Exception as e:
            logger.error(f"Error getting all suppliers: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving suppliers"
            )
    
    async def update(self, supplier_id: str, supplier_data: SupplierUpdate) -> bool:
        """Update supplier"""
        try:
            # Check if supplier exists
            existing_supplier = await self.repository.get_by_id(supplier_id)
            if not existing_supplier:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Supplier not found"
                )
            
            update_dict = supplier_data.dict(exclude_unset=True)
            
            # Check email uniqueness if email is being updated
            if "email" in update_dict:
                existing_email = await self.repository.get_by_email(update_dict["email"])
                if existing_email and existing_email["_id"] != supplier_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already registered"
                    )
            
            # Check tax ID uniqueness if tax_id is being updated
            if "tax_id" in update_dict:
                existing_tax_id = await self.repository.get_by_tax_id(update_dict["tax_id"])
                if existing_tax_id and existing_tax_id["_id"] != supplier_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Tax ID already registered"
                    )
            
            update_dict["updated_at"] = datetime.utcnow()
            return await self.repository.update(supplier_id, update_dict)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating supplier {supplier_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating supplier"
            )
    
    async def deactivate(self, supplier_id: str) -> bool:
        """Deactivate supplier (soft deactivate)"""
        try:
            return await self.repository.deactivte(supplier_id)
        except Exception as e:
            logger.error(f"Error deactivate supplier {supplier_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deactivate supplier"
            )
        
    async def activate(self, supplier_id: str) -> bool:
        """Activate supplier (soft activate)"""
        try:
            return await self.repository.activate(supplier_id)
        except Exception as e:
            logger.error(f"Error activate supplier {supplier_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error activate supplier"
            )
    
    async def search_suppliers(self, search_term: str) -> List[Dict[str, Any]]:
        """Search suppliers by name, email, or contact person"""
        try:
            return await self.repository.search_suppliers(search_term)
        except Exception as e:
            logger.error(f"Error searching suppliers with term {search_term}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error searching suppliers"
            )
    
    async def update_balance(self, supplier_id: str, amount: float) -> bool:
        """Update supplier balance"""
        try:
            return await self.repository.update_balance(supplier_id, amount)
        except Exception as e:
            logger.error(f"Error updating balance for supplier {supplier_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating supplier balance"
            )