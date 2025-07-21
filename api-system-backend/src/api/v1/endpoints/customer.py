from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from src.models.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from src.repositories.customer_repository import CustomerRepository
from src.services.customer_service import CustomerService
from src.db.database import get_database
from src.api.deps import get_current_active_user, require_permissions
import logging
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=List[CustomerResponse])
async def get_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db = Depends(get_database),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get all customers
    """
    try:
        customer_repository = CustomerRepository(db.customers)
        customer_service = CustomerService(customer_repository)
        
        customers = await customer_service.get_all(skip=skip, limit=limit)
        logger.info(f"Retrieved {len(customers)} customers")
        
        return [CustomerResponse(**customer) for customer in customers]
    except Exception as e:
        logger.error(f"Error getting customers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving customers"
        )

@router.get("/search")
async def search_customers(
    q: str = Query(..., min_length=1),
    db = Depends(get_database),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Search customers by name, email, or phone
    """
    try:
        customer_repository = CustomerRepository(db.customers)
        customer_service = CustomerService(customer_repository)
        
        customers = await customer_service.search_customers(q)
        logger.info(f"Found {len(customers)} customers for search term: {q}")
        
        return [CustomerResponse(**customer) for customer in customers]
    except Exception as e:
        logger.error(f"Error searching customers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching customers"
        )

@router.get("/customer/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: str,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Get customer by ID
    """
    try:
        customer_repository = CustomerRepository(db.customers)
        customer_service = CustomerService(customer_repository)
        
        customer = await customer_service.get_by_id(customer_id)
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        return CustomerResponse(**customer)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting customer {customer_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving customer"
        )

@router.post("/customer/create", response_model=CustomerResponse)
async def create_customer(
    customer_data: CustomerCreate,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Create new customer
    """
    try:
        logger.info(f"Creating customer: {customer_data.name}")
        customer_repository = CustomerRepository(db.customers)
        customer_service = CustomerService(customer_repository)
        
        customer_id = await customer_service.create(customer_data)
        customer = await customer_service.get_by_id(customer_id)
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create customer"
            )
        
        logger.info(f"Customer created successfully with ID: {customer_id}")

        return JSONResponse(
            status_code=200,
            content={"message": "Customer created successfully"}
        )
        #return CustomerResponse(**customer)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating customer: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating customer: {str(e)}"
        )

@router.put("/customer/update/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: str,
    customer_data: CustomerUpdate,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Update customer
    """
    try:
        logger.info(f"Updating customer: {customer_id}")
        customer_repository = CustomerRepository(db.customers)
        customer_service = CustomerService(customer_repository)
        
        success = await customer_service.update(customer_id, customer_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        return JSONResponse(
            status_code=200,
            content={"message": "Customer updated successfully"}
        )
        
        # customer = await customer_service.get_by_id(customer_id)
        # logger.info(f"Customer updated successfully: {customer_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating customer {customer_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating customer"
        )

@router.put("/customer/deactivate/{customer_id}")
async def deactivate_customer(
    customer_id: str,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Deactivate customer (soft delete)
    """
    try:
        logger.info(f"Deactivate customer: {customer_id}")
        customer_repository = CustomerRepository(db.customers)
        customer_service = CustomerService(customer_repository)
        
        success = await customer_service.deactivate(customer_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        logger.info(f"Customer deactivate successfully: {customer_id}")
        
        return JSONResponse(
            status_code=200,
            content={"message": "Customer deactivate successfully"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivate customer {customer_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deactivate customer"
        )
    

@router.put("/customer/activate/{customer_id}")
async def activate_customer(
    customer_id: str,
    db = Depends(get_database),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Activate customer (soft delete)
    """
    try:
        logger.info(f"Activate customer: {customer_id}")
        customer_repository = CustomerRepository(db.customers)
        customer_service = CustomerService(customer_repository)
        
        success = await customer_service.activate(customer_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        logger.info(f"Customer activate successfully: {customer_id}")
        
        return JSONResponse(
            status_code=200,
            content={"message": "Customer activate successfully"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activate customer {customer_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error activate customer"
        )