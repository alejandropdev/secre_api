"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_v1_router
from app.core.config import settings
from app.core.exceptions import (
    BaseAPIException,
    api_exception_handler,
    general_exception_handler,
    http_exception_handler,
)
from app.core.logging import setup_logging
from app.core.openapi import get_openapi_schema
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.rls import RLSMiddleware

# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title="Secre API - Multi-tenant Medical Integration",
    version=settings.version,
    description="""
    ## Secre API - API de Integración Médica Multi-tenant

    API interna para integración entre chatbots (agentes n8n) y sistemas médicos externos.
    Diseñada para ser multi-tenant, segura y rápida.

    ### Características Principales

    * **Multi-tenant**: Aislamiento completo de datos por inquilino
    * **Seguridad**: Autenticación por API Key con hash seguro
    * **Flexibilidad**: Campos personalizables por inquilino usando JSONB
    * **Auditoría**: Registro completo de cambios y operaciones
    * **Validación**: Validación robusta de datos médicos
    * **Observabilidad**: Logs estructurados y trazabilidad completa

    ### Autenticación

    Todas las operaciones requieren un API Key válido en el header `X-Api-Key`.
    Los API Keys son específicos por inquilino y proporcionan acceso solo a los datos de ese inquilino.

    ### Modelos de Datos

    * **Pacientes**: Información demográfica y médica básica
    * **Citas**: Programación y gestión de citas médicas
    * **Campos Personalizados**: Datos específicos por inquilino usando JSONB

    ### Formato de Fechas

    Todas las fechas deben estar en formato RFC3339 con zona horaria.
    Las fechas se almacenan automáticamente en UTC en la base de datos.
    """,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Secre API Support",
        "email": "support@secre-api.com",
    },
    license_info={
        "name": "Proprietary",
        "url": "https://secre-api.com/license",
    },
    servers=[
        {
            "url": "https://api.secre-api.com",
            "description": "Production server"
        },
        {
            "url": "https://staging-api.secre-api.com", 
            "description": "Staging server"
        },
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        }
    ],
    tags_metadata=[
        {
            "name": "Pacientes",
            "description": "Operaciones CRUD para gestión de pacientes. Incluye validación de documentos, normalización de datos y campos personalizados por inquilino.",
        },
        {
            "name": "Citas",
            "description": "Operaciones CRUD para gestión de citas médicas. Incluye validación de horarios, conversión UTC y campos personalizados.",
        },
        {
            "name": "Autenticación",
            "description": "Gestión de API Keys y autenticación. Solo para administradores internos.",
        },
        {
            "name": "Lookups",
            "description": "Datos de referencia como tipos de documento, géneros, modalidades de cita, etc.",
        },
        {
            "name": "Auditoría",
            "description": "Registro de auditoría para seguimiento de cambios y operaciones.",
        },
        {
            "name": "Salud",
            "description": "Endpoints de monitoreo y salud del sistema.",
        }
    ]
)

# Add middleware (order matters - first added is outermost)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(RLSMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
app.add_exception_handler(BaseAPIException, api_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include API routers
app.include_router(api_v1_router)

# Override OpenAPI schema
app.openapi = lambda: get_openapi_schema(app)


@app.get(
    "/health",
    summary="Verificar Estado del Sistema",
    description="""
    Endpoint de monitoreo para verificar el estado del sistema.
    
    **Uso:**
    - Monitoreo de salud del servicio
    - Verificación de disponibilidad
    - Validación de conectividad
    
    **Respuesta:**
    - `status`: Estado del sistema (healthy/unhealthy)
    - `version`: Versión actual de la API
    
    **Códigos de Estado:**
    - 200: Sistema funcionando correctamente
    - 503: Sistema no disponible (si hay problemas)
    """,
    responses={
        200: {
            "description": "Sistema funcionando correctamente",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "version": "1.0.0"
                    }
                }
            }
        },
        503: {
            "description": "Sistema no disponible",
            "content": {
                "application/json": {
                    "example": {
                        "status": "unhealthy",
                        "version": "1.0.0",
                        "error": "Database connection failed"
                    }
                }
            }
        }
    },
    tags=["Salud"]
)
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.version}


@app.get(
    "/",
    summary="Información de la API",
    description="""
    Endpoint raíz que proporciona información básica sobre la API.
    
    **Información Incluida:**
    - Mensaje de bienvenida
    - Versión actual de la API
    - Enlaces a la documentación
    
    **Uso:**
    - Verificación rápida de la API
    - Obtención de información básica
    - Redirección a la documentación
    """,
    responses={
        200: {
            "description": "Información de la API",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Secre API - Multi-tenant Medical Integration",
                        "version": "1.0.0",
                        "docs": "/docs"
                    }
                }
            }
        }
    },
    tags=["Salud"]
)
async def root():
    """Root endpoint."""
    return {
        "message": "Secre API - Multi-tenant Medical Integration",
        "version": settings.version,
        "docs": "/docs",
    }
