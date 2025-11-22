from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """
    Root endpoint - health check
    """
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """
    Run on application startup
    """
    print(f"🚀 {settings.PROJECT_NAME} v{settings.VERSION} starting up...")
    print(f"📊 Environment: {settings.ENVIRONMENT}")
    print(f"🌐 API Docs: http://localhost:8000{settings.API_V1_STR}/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Run on application shutdown
    """
    print(f"👋 {settings.PROJECT_NAME} shutting down...")


# Include API routers
from app.api import devices, metrics, websockets

app.include_router(devices.router)
app.include_router(metrics.router)
app.include_router(websockets.router)

# TODO: Add remaining routers as they're implemented
# from app.api import organizations, clients, sites, ai
# app.include_router(organizations.router)
# app.include_router(clients.router)
# app.include_router(sites.router)
# app.include_router(ai.router)
