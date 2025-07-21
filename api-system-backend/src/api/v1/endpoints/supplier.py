from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from src.models.supplier import SupplierCreate, SupplierUpdate, SupplierResponse
from src.repositories.supplier_repository import SupplierRepository
from src.services.supplier_service import SupplierService
from src.db.database import get_database
from src.api.deps import get_current_active_user, require_permissions
import logging
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[SupplierResponse])
async def get_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db = Depends(get_database),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get all suppliers
    """
    try:
        supplier_repository = SupplierRepository(db.suppliers)
        supplier_service = SupplierService(supplier_repository)
        
        suppliers = await supplier_service.get_all(skip=skip, limit=limit)
        logger.info(f"Retrieved {len(suppliers)} suppliers")
        
        return [SupplierResponse(**supplier) for supplier in suppliers]
    except Exception as e:
        logger.error(f"Error getting suppliers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving suppliers"
        )

@router.get("/search")
async def search_suppliers(
    q: str = Query(..., min_length=1),
    db = Depends(get_database),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Search suppliers by name, email, or contact person
    """
    try:
        supplier_repository = SupplierRepository(db.suppliers)
        supplier_service = SupplierService(supplier_repository)
        
        suppliers = await supplier_service.search_suppliers(q)
        logger.info(f"Found {len(suppliers)} suppliers for search term: {q}")
        
        return [SupplierResponse(**supplier) for supplier in suppliers]
    except Exception as e:
        logger.error(f"Error searching suppliers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching suppliers"
        )

@router.get("/supplier/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(
    supplier_id: str,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get supplier by ID
    """
    try:
        supplier_repository = SupplierRepository(db.suppliers)
        supplier_service = SupplierService(supplier_repository)
        
        supplier = await supplier_service.get_by_id(supplier_id)
        
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier not found"
            )
        
        return SupplierResponse(**supplier)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting supplier {supplier_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving supplier"
        )

@router.post("/supplier/create", response_model=SupplierResponse)
async def create_supplier(
    supplier_data: SupplierCreate,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Create new supplier
    """
    try:
        logger.info(f"Creating supplier: {supplier_data.name}")
        supplier_repository = SupplierRepository(db.suppliers)
        supplier_service = SupplierService(supplier_repository)
        
        supplier_id = await supplier_service.create(supplier_data)
        supplier = await supplier_service.get_by_id(supplier_id)
        
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create supplier"
            )
        
        logger.info(f"Supplier created successfully with ID: {supplier_id}")
        return JSONResponse(
            status_code=200,
            content={"message": "Supplier created successfully"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating supplier: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating supplier: {str(e)}"
        )

@router.put("/supplier/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: str,
    supplier_data: SupplierUpdate,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Update supplier
    """
    try:
        logger.info(f"Updating supplier: {supplier_id}")
        supplier_repository = SupplierRepository(db.suppliers)
        supplier_service = SupplierService(supplier_repository)
        
        success = await supplier_service.update(supplier_id, supplier_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier not found"
            )
        
        supplier = await supplier_service.get_by_id(supplier_id)
        logger.info(f"Supplier updated successfully: {supplier_id}")
        
        return JSONResponse(
            status_code=200,
            content={"message": "Supplier updated successfully"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating supplier {supplier_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating supplier"
        )

@router.put("/supplier/deactivate/{supplier_id}")
async def deactivate_supplier(
    supplier_id: str,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Deactivate supplier (soft delete)
    """
    try:
        logger.info(f"Deactivate supplier: {supplier_id}")
        supplier_repository = SupplierRepository(db.suppliers)
        supplier_service = SupplierService(supplier_repository)
        
        success = await supplier_service.deactivate(supplier_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier not found"
            )
        
        logger.info(f"Supplier deactivate successfully: {supplier_id}")
        return JSONResponse(
            status_code=200,
            content={"message": "Supplier deactivate successfully"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivate supplier {supplier_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deactivate supplier"
        )
    

@router.put("/supplier/activate/{supplier_id}")
async def activate_supplier(
    supplier_id: str,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Activate supplier (soft delete)
    """
    try:
        logger.info(f"Activate supplier: {supplier_id}")
        supplier_repository = SupplierRepository(db.suppliers)
        supplier_service = SupplierService(supplier_repository)
        
        success = await supplier_service.activate(supplier_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier not found"
            )
        
        logger.info(f"Supplier activate successfully: {supplier_id}")
        return JSONResponse(
            status_code=200,
            content={"message": "Supplier activate successfully"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activate supplier {supplier_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error activate supplier"
        )