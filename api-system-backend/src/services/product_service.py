from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from src.services.base import BaseService
from src.repositories.product_repository import ProductRepository
from src.models.product import ProductCreate, ProductUpdate
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ProductService(BaseService):
    """Product service implementing business logic"""
    
    def __init__(self, repository: ProductRepository):
        super().__init__(repository)
        self.repository = repository
    
    async def create(self, product_data: ProductCreate) -> str:
        """Create new product"""
        try:
            # Check if SKU already exists
            if await self.repository.sku_exists(product_data.sku):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="SKU already exists"
                )
            
            # Prepare product document
            product_dict = product_data.dict()
            product_dict["created_at"] = datetime.utcnow()
            product_dict["updated_at"] = datetime.utcnow()
            product_dict["is_active"] = True
            
            logger.info(f"Creating product with data: {product_dict}")
            product_id = await self.repository.create(product_dict)
            logger.info(f"Product created with ID: {product_id}")
            
            return product_id
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in product service create: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create product: {str(e)}"
            )
    
    async def get_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product by ID"""
        try:
            return await self.repository.get_by_id(product_id)
        except Exception as e:
            logger.error(f"Error getting product by ID {product_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving product"
            )
    
    async def get_by_sku(self, sku: str) -> Optional[Dict[str, Any]]:
        """Get product by SKU"""
        try:
            return await self.repository.get_by_sku(sku)
        except Exception as e:
            logger.error(f"Error getting product by SKU {sku}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving product"
            )
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all products"""
        try:
            return await self.repository.get_all(skip=skip, limit=limit, filters={"is_active": True})
        except Exception as e:
            logger.error(f"Error getting all products: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving products"
            )
    
    async def update(self, product_id: str, product_data: ProductUpdate) -> bool:
        """Update product"""
        try:
            # Check if product exists
            existing_product = await self.repository.get_by_id(product_id)
            if not existing_product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product not found"
                )
            
            update_dict = product_data.dict(exclude_unset=True)
            
            # Check SKU uniqueness if SKU is being updated
            if "sku" in update_dict:
                if await self.repository.sku_exists(update_dict["sku"], product_id):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="SKU already exists"
                    )
            
            update_dict["updated_at"] = datetime.utcnow()
            return await self.repository.update(product_id, update_dict)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating product {product_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating product"
            )
    
    async def deactivate(self, product_id: str) -> bool:
        """Deactivate product (soft delete)"""
        try:
            return await self.repository.deactivate(product_id)
        except Exception as e:
            logger.error(f"Error deactivate product {product_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deactivate product"
            )

    async def activate(self, product_id: str) -> bool:
        """Activate product (soft delete)"""
        try:
            return await self.repository.activate(product_id)
        except Exception as e:
            logger.error(f"Error activate product {product_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error activate product"
            )
    
    async def search_products(self, search_term: str) -> List[Dict[str, Any]]:
        """Search products by name, SKU, or category"""
        try:
            return await self.repository.search_products(search_term)
        except Exception as e:
            logger.error(f"Error searching products with term {search_term}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error searching products"
            )
    
    async def get_low_stock_products(self) -> List[Dict[str, Any]]:
        """Get products with low stock"""
        try:
            return await self.repository.get_low_stock_products()
        except Exception as e:
            logger.error(f"Error getting low stock products: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving low stock products"
            )
    
    async def update_stock(self, product_id: str, quantity_change: int) -> bool:
        """Update product stock quantity"""
        try:
            return await self.repository.update_stock(product_id, quantity_change)
        except Exception as e:
            logger.error(f"Error updating stock for product {product_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating product stock"
            )