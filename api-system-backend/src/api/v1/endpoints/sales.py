from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from src.models.sale import SaleCreate, SaleUpdate, SaleResponse
from src.repositories.sale_repository import SaleRepository
from src.services.sale_service import SaleService
from src.db.database import get_database
from src.api.deps import get_current_active_user, require_permissions
import logging
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[SaleResponse])
async def get_sales(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db = Depends(get_database),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get all sales
    """
    try:
        sale_repository = SaleRepository(db.sales)
        sale_service = SaleService(sale_repository)
        
        sales = await sale_service.get_all(skip=skip, limit=limit)
        logger.info(f"Retrieved {len(sales)} sales")
        
        return [SaleResponse(**sale) for sale in sales]
    except Exception as e:
        logger.error(f"Error getting sales: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving sales"
        )

@router.get("/{sale_id}", response_model=SaleResponse)
async def get_sale(
    sale_id: str,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get sale by ID
    """
    try:
        sale_repository = SaleRepository(db.sales)
        sale_service = SaleService(sale_repository)
        
        sale = await sale_service.get_by_id(sale_id)
        
        if not sale:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sale not found"
            )
        
        return SaleResponse(**sale)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sale {sale_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving sale"
        )

@router.post("/sale/create", response_model=SaleResponse)
async def create_sale(
    sale_data: SaleCreate,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Create new sale
    """
    try:
        logger.info(f"Creating sale for customer: {sale_data.customer_id}")
        sale_repository = SaleRepository(db.sales)
        sale_service = SaleService(sale_repository)
        
        sale_id = await sale_service.create(sale_data, current_user)
        sale = await sale_service.get_by_id(sale_id)
        
        if not sale:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create sale"
            )
        
        logger.info(f"Sale created successfully with ID: {sale_id}")
        return JSONResponse(
            status_code=200,
            content={"message": "Sale creacted successfully"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating sale: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating sale: {str(e)}"
        )

@router.put("/sale/update/{sale_id}", response_model=SaleResponse)
async def update_sale(
    sale_id: str,
    sale_data: SaleUpdate,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Update sale
    """
    try:
        logger.info(f"Updating sale: {sale_id}")
        sale_repository = SaleRepository(db.sales)
        sale_service = SaleService(sale_repository)
        
        success = await sale_service.update(sale_id, sale_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sale not found"
            )
        
        sale = await sale_service.get_by_id(sale_id)
        logger.info(f"Sale updated successfully: {sale_id}")
        
        return JSONResponse(
            status_code=200,
            content={"message": "Sale updated successfully"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating sale {sale_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating sale"
        )
    
@router.put("/sale/cancel/{sale_id}")
async def cancel_sale(
    sale_id: str,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Cancel sale (soft delete)
    """
    try:
        logger.info(f"Cancelling sale: {sale_id}")
        sale_repository = SaleRepository(db.sales)
        sale_service = SaleService(sale_repository)
        
        success = await sale_service.cancel_sale(sale_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sale not found"
            )
        
        logger.info(f"Sale cancelled successfully: {sale_id}")
        return JSONResponse(
            status_code=200,
            content={"message": "Sale cancelled successfully"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling sale {sale_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error cancelling sale"
        )

@router.get("/customer/{customer_id}")
async def get_sales_by_customer(
    customer_id: str,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get sales by customer ID
    """
    try:
        sale_repository = SaleRepository(db.sales)
        sale_service = SaleService(sale_repository)
        
        sales = await sale_service.get_sales_by_customer(customer_id)
        logger.info(f"Found {len(sales)} sales for customer: {customer_id}")
        
        return [SaleResponse(**sale) for sale in sales]
    except Exception as e:
        logger.error(f"Error getting sales for customer {customer_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving customer sales"
        )

@router.get("/reports/daily")
async def get_daily_sales_report(
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    db = Depends(get_database),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get daily sales report
    """
    try:
        from datetime import datetime
        report_date = datetime.strptime(date, "%Y-%m-%d")
        
        sale_repository = SaleRepository(db.sales)
        sale_service = SaleService(sale_repository)
        
        report = await sale_service.get_daily_sales_summary(report_date)
        logger.info(f"Generated daily sales report for: {date}")
        
        return report
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    except Exception as e:
        logger.error(f"Error generating daily sales report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating sales report"
        )