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


# TODO: Add API routers
# from app.api import organizations, clients, sites, devices, metrics, ai
# app.include_router(organizations.router, prefix=f"{settings.API_V1_STR}/organizations", tags=["organizations"])
# app.include_router(clients.router, prefix=f"{settings.API_V1_STR}/clients", tags=["clients"])
# app.include_router(sites.router, prefix=f"{settings.API_V1_STR}/sites", tags=["sites"])
# app.include_router(devices.router, prefix=f"{settings.API_V1_STR}/devices", tags=["devices"])
# app.include_router(metrics.router, prefix=f"{settings.API_V1_STR}/metrics", tags=["metrics"])
# app.include_router(ai.router, prefix=f"{settings.API_V1_STR}/ai", tags=["ai"])
