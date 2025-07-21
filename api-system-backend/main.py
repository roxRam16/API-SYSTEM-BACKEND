from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.core.config import settings
from src.db.database import database
from src.api.v1.api import api_router
import logging
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        await database.connect_to_mongo()
        logger.info("✅ Database connected successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to connect to database: {e}")
        raise e
    
    yield
    
    # Shutdown
    await database.close_mongo_connection()
    logger.info("Database connection closed")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "message": "AI POS System API",
        "version": settings.PROJECT_VERSION,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    try:
        # Check database connection
        db_healthy = await database.health_check()
        
        return {
            "status": "healthy" if db_healthy else "unhealthy",
            "database": "connected" if db_healthy else "disconnected",
            "api": "running"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "error",
            "api": "running",
            "error": str(e)
        }

async def startup():
    """Initialize database connection on startup"""
    try:
        await database.connect_to_mongo()
        print("✅ Database connected successfully!")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        raise e

if __name__ == "__main__":

    print(f"🚀 API running on http://127.0.0.1:8000")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False
    )
