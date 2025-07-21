from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from src.repositories.base import BaseRepository
from datetime import datetime, timedelta

class SaleRepository(BaseRepository):
    """Sale repository implementing specific sale operations"""
    
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection)
    
    async def get_by_sale_number(self, sale_number: str) -> Optional[Dict[str, Any]]:
        """Get sale by sale number"""
        document = await self.collection.find_one({"sale_number": sale_number})
        if document:
            document["_id"] = str(document["_id"])
        return document
    
    async def get_sales_by_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get sales by customer ID"""
        cursor = self.collection.find({"customer_id": customer_id}).sort("sale_date", -1)
        documents = await cursor.to_list(length=None)
        
        for doc in documents:
            doc["_id"] = str(doc["_id"])
        
        return documents
    
    async def get_sales_by_cashier(self, cashier_id: str) -> List[Dict[str, Any]]:
        """Get sales by cashier ID"""
        cursor = self.collection.find({"cashier_id": cashier_id}).sort("sale_date", -1)
        documents = await cursor.to_list(length=None)
        
        for doc in documents:
            doc["_id"] = str(doc["_id"])
        
        return documents
    
    async def get_sales_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get sales within date range"""
        query = {
            "sale_date": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
        
        cursor = self.collection.find(query).sort("sale_date", -1)
        documents = await cursor.to_list(length=None)
        
        for doc in documents:
            doc["_id"] = str(doc["_id"])
        
        return documents
    
    async def get_daily_sales_summary(self, date: datetime) -> Dict[str, Any]:
        """Get daily sales summary"""
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        pipeline = [
            {
                "$match": {
                    "sale_date": {"$gte": start_date, "$lt": end_date},
                    "status": "completed"
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_sales": {"$sum": 1},
                    "total_amount": {"$sum": "$total_amount"},
                    "total_tax": {"$sum": "$tax_amount"},
                    "total_discount": {"$sum": "$discount_amount"}
                }
            }
        ]
        
        result = await self.collection.aggregate(pipeline).to_list(length=1)
        return result[0] if result else {
            "total_sales": 0,
            "total_amount": 0.0,
            "total_tax": 0.0,
            "total_discount": 0.0
        }
    
    async def get_top_selling_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top selling products"""
        pipeline = [
            {"$unwind": "$items"},
            {
                "$group": {
                    "_id": "$items.product_id",
                    "product_name": {"$first": "$items.product_name"},
                    "total_quantity": {"$sum": "$items.quantity"},
                    "total_revenue": {"$sum": "$items.total"}
                }
            },
            {"$sort": {"total_quantity": -1}},
            {"$limit": limit}
        ]
        
        return await self.collection.aggregate(pipeline).to_list(length=limit)
    
    async def generate_sale_number(self) -> str:
        """Generate unique sale number"""
        from datetime import datetime
        today = datetime.now()
        prefix = f"SALE-{today.strftime('%Y%m%d')}"
        
        # Get the last sale number for today
        last_sale = await self.collection.find_one(
            {"sale_number": {"$regex": f"^{prefix}"}},
            sort=[("sale_number", -1)]
        )
        
        if last_sale:
            last_number = int(last_sale["sale_number"].split("-")[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f"{prefix}-{new_number:04d}"