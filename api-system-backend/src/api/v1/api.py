from fastapi import APIRouter
from src.api.v1.endpoints import auth, users, products, sales, customer, supplier

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(customer.router, prefix="/customers", tags=["customers"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(supplier.router, prefix="/suppliers", tags=["suppliers"])
api_router.include_router(sales.router, prefix="/sales", tags=["sales"])