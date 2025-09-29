"""Utilities for converting between database models and Pydantic schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.models.api_key import ApiKey
from app.models.appointment import Appointment
from app.models.audit_log import AuditLog
from app.models.lookup import (
    AppointmentModality,
    AppointmentState,
    DocumentType,
    Gender,
)
from app.models.patient import Patient
from app.models.tenant import Tenant
from app.schemas.appointment import AppointmentResponseSchema
from app.schemas.audit import AuditLogResponseSchema
from app.schemas.auth import ApiKeyResponseSchema, TenantResponseSchema
from app.schemas.lookup import (
    AppointmentModalitySchema,
    AppointmentStateSchema,
    DocumentTypeSchema,
    GenderSchema,
)
from app.schemas.patient import PatientResponseSchema


def convert_patient_to_response(patient: Patient) -> PatientResponseSchema:
    """Convert Patient model to PatientResponseSchema."""
    return PatientResponseSchema(
        id=patient.id,
        tenant_id=patient.tenant_id,
        first_name=patient.first_name,
        second_name=patient.second_name,
        first_last_name=patient.first_last_name,
        second_last_name=patient.second_last_name,
        birth_date=patient.birth_date,
        gender_id=patient.gender_id,
        document_type_id=patient.document_type_id,
        document_number=patient.document_number,
        phone=patient.phone,
        email=patient.email,
        eps_id=patient.eps_id,
        habeas_data=patient.habeas_data,
        custom_fields=patient.custom_fields,
        created_at=patient.created_at.isoformat(),
        updated_at=patient.updated_at.isoformat(),
    )


def convert_appointment_to_response(appointment: Appointment) -> AppointmentResponseSchema:
    """Convert Appointment model to AppointmentResponseSchema."""
    return AppointmentResponseSchema(
        id=appointment.id,
        tenant_id=appointment.tenant_id,
        start_utc=appointment.start_utc,
        end_utc=appointment.end_utc,
        patient_document_type_id=appointment.patient_document_type_id,
        patient_document_number=appointment.patient_document_number,
        doctor_document_type_id=appointment.doctor_document_type_id,
        doctor_document_number=appointment.doctor_document_number,
        modality=appointment.modality,
        state=appointment.state,
        notification_state=appointment.notification_state,
        appointment_type=appointment.appointment_type,
        clinic_id=appointment.clinic_id,
        comment=appointment.comment,
        custom_fields=appointment.custom_fields,
        created_at=appointment.created_at.isoformat(),
        updated_at=appointment.updated_at.isoformat(),
    )


def convert_tenant_to_response(tenant: Tenant) -> TenantResponseSchema:
    """Convert Tenant model to TenantResponseSchema."""
    return TenantResponseSchema(
        id=tenant.id,
        name=tenant.name,
        is_active=tenant.is_active,
        created_at=tenant.created_at,
        updated_at=tenant.updated_at,
    )


def convert_api_key_to_response(api_key: ApiKey) -> ApiKeyResponseSchema:
    """Convert ApiKey model to ApiKeyResponseSchema."""
    return ApiKeyResponseSchema(
        id=api_key.id,
        tenant_id=api_key.tenant_id,
        name=api_key.name,
        last_used_at=api_key.last_used_at,
        created_at=api_key.created_at,
        revoked_at=api_key.revoked_at,
    )


def convert_document_type_to_schema(doc_type: DocumentType) -> DocumentTypeSchema:
    """Convert DocumentType model to DocumentTypeSchema."""
    return DocumentTypeSchema(
        id=doc_type.id,
        code=doc_type.code,
        name=doc_type.name,
        description=doc_type.description,
        created_at=doc_type.created_at.isoformat(),
        updated_at=doc_type.updated_at.isoformat(),
    )


def convert_gender_to_schema(gender: Gender) -> GenderSchema:
    """Convert Gender model to GenderSchema."""
    return GenderSchema(
        id=gender.id,
        code=gender.code,
        name=gender.name,
        description=gender.description,
        created_at=gender.created_at.isoformat(),
        updated_at=gender.updated_at.isoformat(),
    )


def convert_appointment_modality_to_schema(modality: AppointmentModality) -> AppointmentModalitySchema:
    """Convert AppointmentModality model to AppointmentModalitySchema."""
    return AppointmentModalitySchema(
        id=modality.id,
        code=modality.code,
        name=modality.name,
        description=modality.description,
        created_at=modality.created_at.isoformat(),
        updated_at=modality.updated_at.isoformat(),
    )


def convert_appointment_state_to_schema(state: AppointmentState) -> AppointmentStateSchema:
    """Convert AppointmentState model to AppointmentStateSchema."""
    return AppointmentStateSchema(
        id=state.id,
        code=state.code,
        name=state.name,
        description=state.description,
        created_at=state.created_at.isoformat(),
        updated_at=state.updated_at.isoformat(),
    )


def convert_audit_log_to_response(audit_log: AuditLog) -> AuditLogResponseSchema:
    """Convert AuditLog model to AuditLogResponseSchema."""
    return AuditLogResponseSchema(
        id=audit_log.id,
        tenant_id=audit_log.tenant_id,
        resource_type=audit_log.resource_type,
        resource_id=audit_log.resource_id,
        action=audit_log.action,
        api_key_id=audit_log.api_key_id,
        before_snapshot=audit_log.before_snapshot,
        after_snapshot=audit_log.after_snapshot,
        request_id=audit_log.request_id,
        ip_address=audit_log.ip_address,
        user_agent=audit_log.user_agent,
        created_at=audit_log.created_at,
    )


def convert_patients_to_response_list(patients: List[Patient]) -> List[PatientResponseSchema]:
    """Convert list of Patient models to list of PatientResponseSchema."""
    return [convert_patient_to_response(patient) for patient in patients]


def convert_appointments_to_response_list(appointments: List[Appointment]) -> List[AppointmentResponseSchema]:
    """Convert list of Appointment models to list of AppointmentResponseSchema."""
    return [convert_appointment_to_response(appointment) for appointment in appointments]


def convert_tenants_to_response_list(tenants: List[Tenant]) -> List[TenantResponseSchema]:
    """Convert list of Tenant models to list of TenantResponseSchema."""
    return [convert_tenant_to_response(tenant) for tenant in tenants]


def convert_api_keys_to_response_list(api_keys: List[ApiKey]) -> List[ApiKeyResponseSchema]:
    """Convert list of ApiKey models to list of ApiKeyResponseSchema."""
    return [convert_api_key_to_response(api_key) for api_key in api_keys]


def convert_audit_logs_to_response_list(audit_logs: List[AuditLog]) -> List[AuditLogResponseSchema]:
    """Convert list of AuditLog models to list of AuditLogResponseSchema."""
    return [convert_audit_log_to_response(audit_log) for audit_log in audit_logs]


def convert_document_types_to_schema_list(document_types: List[DocumentType]) -> List[DocumentTypeSchema]:
    """Convert list of DocumentType models to list of DocumentTypeSchema."""
    return [convert_document_type_to_schema(doc_type) for doc_type in document_types]


def convert_genders_to_schema_list(genders: List[Gender]) -> List[GenderSchema]:
    """Convert list of Gender models to list of GenderSchema."""
    return [convert_gender_to_schema(gender) for gender in genders]


def convert_appointment_modalities_to_schema_list(modalities: List[AppointmentModality]) -> List[AppointmentModalitySchema]:
    """Convert list of AppointmentModality models to list of AppointmentModalitySchema."""
    return [convert_appointment_modality_to_schema(modality) for modality in modalities]


def convert_appointment_states_to_schema_list(states: List[AppointmentState]) -> List[AppointmentStateSchema]:
    """Convert list of AppointmentState models to list of AppointmentStateSchema."""
    return [convert_appointment_state_to_schema(state) for state in states]
