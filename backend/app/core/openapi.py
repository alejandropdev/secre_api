"""OpenAPI configuration and components."""

from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI

from app.core.config import settings


def get_openapi_schema(app: FastAPI) -> dict:
    """Generate comprehensive OpenAPI schema."""
    
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-Api-Key",
            "description": "API Key para autenticación. Debe incluirse en el header X-Api-Key para todas las operaciones.",
            "example": "sk-1234567890abcdef1234567890abcdef"
        }
    }
    
    # Add common responses
    openapi_schema["components"]["responses"] = {
        "UnauthorizedError": {
            "description": "No autorizado - API Key requerida o inválida",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorResponseSchema"
                    },
                    "examples": {
                        "missing_api_key": {
                            "summary": "API Key faltante",
                            "value": {
                                "error": "API key required. Provide X-Api-Key header.",
                                "trace_id": "550e8400-e29b-41d4-a716-446655440001",
                                "timestamp": "2024-01-15T10:30:00Z"
                            }
                        },
                        "invalid_api_key": {
                            "summary": "API Key inválida",
                            "value": {
                                "error": "Invalid API key",
                                "trace_id": "550e8400-e29b-41d4-a716-446655440002",
                                "timestamp": "2024-01-15T10:30:00Z"
                            }
                        }
                    }
                }
            }
        },
        "ValidationError": {
            "description": "Error de validación de datos",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorResponseSchema"
                    },
                    "examples": {
                        "validation_error": {
                            "summary": "Error de validación",
                            "value": {
                                "error": "Validation error",
                                "detail": "Patient with document 12345678 already exists",
                                "trace_id": "550e8400-e29b-41d4-a716-446655440003",
                                "timestamp": "2024-01-15T10:30:00Z",
                                "field": "document_number"
                            }
                        },
                        "required_field": {
                            "summary": "Campo requerido faltante",
                            "value": {
                                "error": "Validation error",
                                "detail": "Field 'firstName' is required",
                                "trace_id": "550e8400-e29b-41d4-a716-446655440004",
                                "timestamp": "2024-01-15T10:30:00Z",
                                "field": "firstName"
                            }
                        }
                    }
                }
            }
        },
        "NotFoundError": {
            "description": "Recurso no encontrado",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorResponseSchema"
                    },
                    "examples": {
                        "patient_not_found": {
                            "summary": "Paciente no encontrado",
                            "value": {
                                "error": "Patient 550e8400-e29b-41d4-a716-446655440000 not found",
                                "trace_id": "550e8400-e29b-41d4-a716-446655440005",
                                "timestamp": "2024-01-15T10:30:00Z"
                            }
                        },
                        "appointment_not_found": {
                            "summary": "Cita no encontrada",
                            "value": {
                                "error": "Appointment 550e8400-e29b-41d4-a716-446655440000 not found",
                                "trace_id": "550e8400-e29b-41d4-a716-446655440006",
                                "timestamp": "2024-01-15T10:30:00Z"
                            }
                        }
                    }
                }
            }
        },
        "InternalServerError": {
            "description": "Error interno del servidor",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorResponseSchema"
                    },
                    "examples": {
                        "internal_error": {
                            "summary": "Error interno",
                            "value": {
                                "error": "Internal server error",
                                "detail": "An unexpected error occurred",
                                "trace_id": "550e8400-e29b-41d4-a716-446655440007",
                                "timestamp": "2024-01-15T10:30:00Z"
                            }
                        }
                    }
                }
            }
        }
    }
    
    # Add common parameters
    openapi_schema["components"]["parameters"] = {
        "PatientId": {
            "name": "patient_id",
            "in": "path",
            "required": True,
            "description": "ID único del paciente",
            "schema": {
                "type": "string",
                "format": "uuid"
            },
            "example": "550e8400-e29b-41d4-a716-446655440000"
        },
        "AppointmentId": {
            "name": "appointment_id",
            "in": "path",
            "required": True,
            "description": "ID único de la cita",
            "schema": {
                "type": "string",
                "format": "uuid"
            },
            "example": "550e8400-e29b-41d4-a716-446655440000"
        },
        "PageParam": {
            "name": "page",
            "in": "query",
            "required": False,
            "description": "Número de página para paginación (comienza en 1)",
            "schema": {
                "type": "integer",
                "minimum": 1,
                "default": 1
            },
            "example": 1
        },
        "SizeParam": {
            "name": "size",
            "in": "query",
            "required": False,
            "description": "Tamaño de página para paginación (máximo 100)",
            "schema": {
                "type": "integer",
                "minimum": 1,
                "maximum": 100,
                "default": 50
            },
            "example": 50
        }
    }
    
    # Add common headers
    openapi_schema["components"]["headers"] = {
        "X-Request-ID": {
            "description": "ID único de la solicitud para trazabilidad",
            "schema": {
                "type": "string",
                "format": "uuid"
            },
            "example": "550e8400-e29b-41d4-a716-446655440000"
        },
        "X-Response-Time": {
            "description": "Tiempo de respuesta en segundos",
            "schema": {
                "type": "string"
            },
            "example": "0.1234s"
        }
    }
    
    # Add security requirements to all endpoints
    openapi_schema["security"] = [{"ApiKeyAuth": []}]
    
    # Add common tags
    openapi_schema["tags"] = [
        {
            "name": "Pacientes",
            "description": "Operaciones CRUD para gestión de pacientes. Incluye validación de documentos, normalización de datos y campos personalizados por inquilino.",
            "externalDocs": {
                "description": "Guía de integración de pacientes",
                "url": "https://docs.secre-api.com/patients"
            }
        },
        {
            "name": "Citas",
            "description": "Operaciones CRUD para gestión de citas médicas. Incluye validación de horarios, conversión UTC y campos personalizados.",
            "externalDocs": {
                "description": "Guía de integración de citas",
                "url": "https://docs.secre-api.com/appointments"
            }
        },
        {
            "name": "Autenticación",
            "description": "Gestión de API Keys y autenticación. Solo para administradores internos.",
            "externalDocs": {
                "description": "Guía de autenticación",
                "url": "https://docs.secre-api.com/auth"
            }
        },
        {
            "name": "Lookups",
            "description": "Datos de referencia como tipos de documento, géneros, modalidades de cita, etc.",
            "externalDocs": {
                "description": "Guía de datos de referencia",
                "url": "https://docs.secre-api.com/lookups"
            }
        },
        {
            "name": "Auditoría",
            "description": "Registro de auditoría para seguimiento de cambios y operaciones.",
            "externalDocs": {
                "description": "Guía de auditoría",
                "url": "https://docs.secre-api.com/audit"
            }
        },
        {
            "name": "Salud",
            "description": "Endpoints de monitoreo y salud del sistema.",
            "externalDocs": {
                "description": "Guía de monitoreo",
                "url": "https://docs.secre-api.com/health"
            }
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema
