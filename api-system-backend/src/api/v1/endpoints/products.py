from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from src.models.product import ProductCreate, ProductUpdate, ProductResponse
from src.repositories.product_repository import ProductRepository
from src.services.product_service import ProductService
from src.db.database import get_database
from src.api.deps import get_current_active_user, require_permissions
import logging
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[ProductResponse])
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db = Depends(get_database),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get all products
    """
    try:
        product_repository = ProductRepository(db.products)
        product_service = ProductService(product_repository)
        
        products = await product_service.get_all(skip=skip, limit=limit)
        logger.info(f"Retrieved {len(products)} products")
        
        return [ProductResponse(**product) for product in products]
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving products"
        )

@router.get("/search")
async def search_products(
    q: str = Query(..., min_length=1),
    db = Depends(get_database),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Search products by name, SKU, or category
    """
    try:
        product_repository = ProductRepository(db.products)
        product_service = ProductService(product_repository)
        
        products = await product_service.search_products(q)
        logger.info(f"Found {len(products)} products for search term: {q}")
        
        return [ProductResponse(**product) for product in products]
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching products"
        )

@router.get("/product/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get product by ID
    """
    try:
        product_repository = ProductRepository(db.products)
        product_service = ProductService(product_repository)
        
        product = await product_service.get_by_id(product_id)
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        return ProductResponse(**product)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving product"
        )

@router.post("/product/create", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Create new product
    """
    try:
        logger.info(f"Creating product: {product_data.name}")
        product_repository = ProductRepository(db.products)
        product_service = ProductService(product_repository)
        
        product_id = await product_service.create(product_data)
        product = await product_service.get_by_id(product_id)
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create product"
            )
        
        logger.info(f"Product created successfully with ID: {product_id}")
        return JSONResponse(
            status_code=200,
            content={"message": "Product created successfully"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating product: {str(e)}"
        )

@router.put("/product/update/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    product_data: ProductUpdate,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Update product
    """
    try:
        logger.info(f"Updating product: {product_id}")
        product_repository = ProductRepository(db.products)
        product_service = ProductService(product_repository)
        
        success = await product_service.update(product_id, product_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        product = await product_service.get_by_id(product_id)
        logger.info(f"Product updated successfully: {product_id}")
        
        return JSONResponse(
            status_code=200,
            content={"message": "Product updated successfully"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating product"
        )

@router.put("/product/deactivate/{product_id}")
async def deactivate_product(
    product_id: str,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Deactivate product (soft delete)
    """
    try:
        logger.info(f"Deactivate product: {product_id}")
        product_repository = ProductRepository(db.products)
        product_service = ProductService(product_repository)
        
        success = await product_service.deactivate(product_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        logger.info(f"Product deactivate successfully: {product_id}")
        return JSONResponse(
            status_code=200,
            content={"message": "Product deactivate successfully"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivate product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deactivate product"
        )
    

@router.put("/product/activate/{product_id}")
async def activate_product(
    product_id: str,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Activate product (soft delete)
    """
    try:
        logger.info(f"Activate product: {product_id}")
        product_repository = ProductRepository(db.products)
        product_service = ProductService(product_repository)
        
        success = await product_service.activate(product_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        logger.info(f"Product activate successfully: {product_id}")
        return JSONResponse(
            status_code=200,
            content={"message": "Product activate successfully"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activate product {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error activate product"
        )