"""Main API v1 router."""

from fastapi import APIRouter

from app.api.v1 import admin, appointments, auth, doctor_availability, health, lookup, patients, tenant_lookups

router = APIRouter()

# Include all sub-routers
router.include_router(admin.router)
router.include_router(auth.router)
router.include_router(doctor_availability.router)
router.include_router(health.router)
router.include_router(lookup.router)
router.include_router(patients.router)
router.include_router(appointments.router)
router.include_router(tenant_lookups.router)
