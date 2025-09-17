"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.middleware.rls import RLSMiddleware

# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description="Multi-tenant Medical Integration API",
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add middleware
app.add_middleware(RLSMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.version}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Secre API - Multi-tenant Medical Integration",
        "version": settings.version,
        "docs": "/docs",
    }
