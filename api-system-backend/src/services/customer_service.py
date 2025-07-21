from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from src.services.base import BaseService
from src.repositories.customer_repository import CustomerRepository
from src.models.customer import CustomerCreate, CustomerUpdate
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class CustomerService(BaseService):
    """Customer service implementing business logic"""
    
    def __init__(self, repository: CustomerRepository):
        super().__init__(repository)
        self.repository = repository
    
    async def create(self, customer_data: CustomerCreate) -> str:
        """Create new customer"""
        try:
            # Check if email already exists
            existing_customer = await self.repository.get_by_email(customer_data.email)
            if existing_customer:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Check if tax ID already exists
            existing_tax_id = await self.repository.get_by_tax_id(customer_data.tax_id)
            if existing_tax_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tax ID already registered"
                )
            
            # Prepare customer document
            customer_dict = customer_data.model_dump()
            customer_dict["created_at"] = datetime.utcnow()
            customer_dict["updated_at"] = datetime.utcnow()
            customer_dict["is_active"] = True
            customer_dict["current_balance"] = 0.0
            
            logger.info(f"Creating customer with data: {customer_dict}")
            
            return await self.repository.create(customer_dict)
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in customer service create: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create customer: {str(e)}"
            )
    
    async def get_by_id(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get customer by ID"""
        try:
            return await self.repository.get_by_id(customer_id)
        except Exception as e:
            logger.error(f"Error getting customer by ID {customer_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving customer"
            )
    
    async def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get customer by email"""
        try:
            return await self.repository.get_by_email(email)
        except Exception as e:
            logger.error(f"Error getting customer by email {email}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving customer"
            )
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all customers"""
        try:
            return await self.repository.get_all(skip=skip, limit=limit, filters={"is_active": True})
        except Exception as e:
            logger.error(f"Error getting all customers: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving customers"
            )
    
    async def update(self, customer_id: str, customer_data: CustomerUpdate) -> bool:
        """Update customer"""
        try:
            # Check if customer exists
            existing_customer = await self.repository.get_by_id(customer_id)
            if not existing_customer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Customer not found"
                )
            
            update_dict = customer_data.model_dump(exclude_unset=True)
            
            # Check email uniqueness if email is being updated
            if "email" in update_dict:
                existing_email = await self.repository.get_by_email(update_dict["email"])
                if existing_email and existing_email["_id"] != customer_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already registered"
                    )
            
            # Check tax ID uniqueness if tax_id is being updated
            if "tax_id" in update_dict:
                existing_tax_id = await self.repository.get_by_tax_id(update_dict["tax_id"])
                if existing_tax_id and existing_tax_id["_id"] != customer_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Tax ID already registered"
                    )
            
            update_dict["updated_at"] = datetime.utcnow()
            return await self.repository.update(customer_id, update_dict)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating customer {customer_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating customer"
            )
    
    async def deactivate(self, customer_id: str) -> bool:
        """Desactivar customer (soft delete)"""
        try:
            return await self.repository.deactivate(customer_id)
        except Exception as e:
            logger.error(f"Error deactivate customer {customer_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deactivate customer"
            )
    
    async def activate(self, customer_id: str) -> bool:
        """Activate customer (soft delete)"""
        try:
            return await self.repository.activate(customer_id)
        except Exception as e:
            logger.error(f"Error activate customer {customer_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error activate customer"
            )

    
    async def search_customers(self, search_term: str) -> List[Dict[str, Any]]:
        """Search customers by name, email, or phone"""
        try:
            return await self.repository.search_customers(search_term)
        except Exception as e:
            logger.error(f"Error searching customers with term {search_term}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error searching customers"
            )
    
    async def update_balance(self, customer_id: str, amount: float) -> bool:
        """Update customer balance"""
        try:
            return await self.repository.update_balance(customer_id, amount)
        except Exception as e:
            logger.error(f"Error updating balance for customer {customer_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating customer balance"
            )