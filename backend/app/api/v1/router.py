"""Main API v1 router."""

from fastapi import APIRouter

from app.api.v1 import admin, auth, health, lookup

router = APIRouter()

# Include all sub-routers
router.include_router(admin.router)
router.include_router(auth.router)
router.include_router(health.router)
router.include_router(lookup.router)
