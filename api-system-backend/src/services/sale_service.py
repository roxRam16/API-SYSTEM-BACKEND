from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from src.services.base import BaseService
from src.repositories.sale_repository import SaleRepository
from src.models.sale import SaleCreate, SaleUpdate, SaleItem
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SaleService(BaseService):
    """Sale service implementing business logic"""
    
    def __init__(self, repository: SaleRepository):
        super().__init__(repository)
        self.repository = repository
    
    async def create(self, sale_data: SaleCreate, current_user: Dict[str, Any]) -> str:
        """Create new sale"""
        try:
            # Generate sale number
            sale_number = await self.repository.generate_sale_number()
            
            # Calculate totals
            subtotal = sum(item.total for item in sale_data.items)
            tax_amount = sum(item.tax_amount for item in sale_data.items)
            total_amount = subtotal + tax_amount - sale_data.discount_amount
            
            # Prepare sale document
            sale_dict = {
                "sale_number": sale_number,
                "customer_id": sale_data.customer_id,
                "customer_name": sale_data.customer_name if hasattr(sale_data, 'customer_name') else "Unknown",
                "cashier_id": current_user["_id"],
                "cashier_name": current_user.get("name", "Unknown"),
                "items": [item.dict() for item in sale_data.items],
                "subtotal": subtotal,
                "discount_amount": sale_data.discount_amount,
                "tax_amount": tax_amount,
                "total_amount": total_amount,
                "payment_method": sale_data.payment_method,
                "payment_reference": sale_data.payment_reference,
                "status": "completed",
                "notes": sale_data.notes,
                "sale_date": datetime.utcnow(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_active": True
            }
            
            logger.info(f"Creating sale with data: {sale_dict}")
            sale_id = await self.repository.create(sale_dict)
            logger.info(f"Sale created with ID: {sale_id}")
            
            return sale_id
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in sale service create: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create sale: {str(e)}"
            )
    
    async def get_by_id(self, sale_id: str) -> Optional[Dict[str, Any]]:
        """Get sale by ID"""
        try:
            return await self.repository.get_by_id(sale_id)
        except Exception as e:
            logger.error(f"Error getting sale by ID {sale_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving sale"
            )
    
    async def get_by_sale_number(self, sale_number: str) -> Optional[Dict[str, Any]]:
        """Get sale by sale number"""
        try:
            return await self.repository.get_by_sale_number(sale_number)
        except Exception as e:
            logger.error(f"Error getting sale by number {sale_number}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving sale"
            )
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all sales"""
        try:
            return await self.repository.get_all(skip=skip, limit=limit, filters={"is_active": True})
        except Exception as e:
            logger.error(f"Error getting all sales: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving sales"
            )
    
    async def update(self, sale_id: str, sale_data: SaleUpdate) -> bool:
        """Update sale"""
        try:
            # Check if sale exists
            existing_sale = await self.repository.get_by_id(sale_id)
            if not existing_sale:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sale not found"
                )
            
            update_dict = sale_data.dict(exclude_unset=True)
            update_dict["updated_at"] = datetime.utcnow()
            
            return await self.repository.update(sale_id, update_dict)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating sale {sale_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating sale"
            )
    
    async def deactivate(self, sale_id: str) -> bool:
        """Deactivate sale (soft deactivate)"""
        try:
            return await self.repository.deactivate(sale_id)
        except Exception as e:
            logger.error(f"Error deactivate sale {sale_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deactivate sale"
            )
        
    async def activate(self, sale_id: str) -> bool:
        """Activate sale (soft activate)"""
        try:
            return await self.repository.activate(sale_id)
        except Exception as e:
            logger.error(f"Error activate sale {sale_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error activate sale"
            )
    
    async def cancel_sale(self, sale_id: str) -> bool:
        """Cancel a sale"""
        try:
            # Check if sale exists
            existing_sale = await self.repository.get_by_id(sale_id)
            if not existing_sale:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Sale not found"
                )
            
            # Only allow canceling pending sales
            if existing_sale.get("status") != "pending":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only pending sales can be cancelled"
                )
            
            update_data = {
                "status": "cancelled",
                "updated_at": datetime.utcnow()
            }
            
            return await self.repository.update(sale_id, update_data)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error cancelling sale {sale_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error cancelling sale"
            )
    
    async def get_sales_by_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get sales by customer ID"""
        try:
            return await self.repository.get_sales_by_customer(customer_id)
        except Exception as e:
            logger.error(f"Error getting sales for customer {customer_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving customer sales"
            )
    
    async def get_sales_by_cashier(self, cashier_id: str) -> List[Dict[str, Any]]:
        """Get sales by cashier ID"""
        try:
            return await self.repository.get_sales_by_cashier(cashier_id)
        except Exception as e:
            logger.error(f"Error getting sales for cashier {cashier_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving cashier sales"
            )
    
    async def get_daily_sales_summary(self, date: datetime) -> Dict[str, Any]:
        """Get daily sales summary"""
        try:
            return await self.repository.get_daily_sales_summary(date)
        except Exception as e:
            logger.error(f"Error getting daily sales summary for {date}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error generating sales summary"
            )
    
    async def get_top_selling_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top selling products"""
        try:
            return await self.repository.get_top_selling_products(limit)
        except Exception as e:
            logger.error(f"Error getting top selling products: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving top selling products"
            )