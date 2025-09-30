"""Add canonical data models with JSONB fields

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 00:01:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_canonical_models'
down_revision = '001_initial_migration'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create lookup tables
    op.create_table('document_type',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    
    op.create_table('gender',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    
    op.create_table('appointment_modality',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    
    op.create_table('appointment_state',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    
    # Create patient table
    op.create_table('patient',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('first_name', sa.String(length=255), nullable=False),
        sa.Column('second_name', sa.String(length=255), nullable=True),
        sa.Column('first_last_name', sa.String(length=255), nullable=False),
        sa.Column('second_last_name', sa.String(length=255), nullable=True),
        sa.Column('birth_date', sa.Date(), nullable=False),
        sa.Column('gender_id', sa.Integer(), nullable=False),
        sa.Column('document_type_id', sa.Integer(), nullable=False),
        sa.Column('document_number', sa.String(length=50), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('cell_phone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('eps_id', sa.String(length=100), nullable=True),
        sa.Column('habeas_data', sa.Boolean(), nullable=False),
        sa.Column('custom_fields', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create appointment table
    op.create_table('appointment',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('start_utc', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_utc', sa.DateTime(timezone=True), nullable=False),
        sa.Column('patient_document_type_id', sa.Integer(), nullable=False),
        sa.Column('patient_document_number', sa.String(length=50), nullable=False),
        sa.Column('doctor_document_type_id', sa.Integer(), nullable=False),
        sa.Column('doctor_document_number', sa.String(length=50), nullable=False),
        sa.Column('modality', sa.String(length=50), nullable=False),
        sa.Column('state', sa.String(length=50), nullable=False),
        sa.Column('notification_state', sa.String(length=50), nullable=True),
        sa.Column('appointment_type', sa.String(length=100), nullable=True),
        sa.Column('clinic_id', sa.String(length=100), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('custom_fields', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create audit_log table
    op.create_table('audit_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('api_key_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('resource_type', sa.String(length=100), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('before_snapshot', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('after_snapshot', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('request_id', sa.String(length=100), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for performance
    op.create_index(op.f('ix_patient_tenant_id'), 'patient', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_patient_document_number'), 'patient', ['document_number'], unique=False)
    op.create_index(op.f('ix_patient_email'), 'patient', ['email'], unique=False)
    op.create_index(op.f('ix_patient_phone'), 'patient', ['phone'], unique=False)
    op.create_index(op.f('ix_patient_cell_phone'), 'patient', ['cell_phone'], unique=False)
    op.create_index('ix_patient_custom_fields', 'patient', ['custom_fields'], unique=False, postgresql_using='gin')
    
    op.create_index(op.f('ix_appointment_tenant_id'), 'appointment', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_appointment_start_utc'), 'appointment', ['start_utc'], unique=False)
    op.create_index(op.f('ix_appointment_patient_doc'), 'appointment', ['patient_document_number'], unique=False)
    op.create_index(op.f('ix_appointment_doctor_doc'), 'appointment', ['doctor_document_number'], unique=False)
    op.create_index(op.f('ix_appointment_state'), 'appointment', ['state'], unique=False)
    op.create_index(op.f('ix_appointment_modality'), 'appointment', ['modality'], unique=False)
    op.create_index('ix_appointment_custom_fields', 'appointment', ['custom_fields'], unique=False, postgresql_using='gin')
    
    op.create_index(op.f('ix_audit_log_tenant_id'), 'audit_log', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_audit_log_resource_type'), 'audit_log', ['resource_type'], unique=False)
    op.create_index(op.f('ix_audit_log_resource_id'), 'audit_log', ['resource_id'], unique=False)
    op.create_index(op.f('ix_audit_log_action'), 'audit_log', ['action'], unique=False)
    
    # Enable RLS on new tables
    op.execute('ALTER TABLE patient ENABLE ROW LEVEL SECURITY;')
    op.execute('ALTER TABLE appointment ENABLE ROW LEVEL SECURITY;')
    op.execute('ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;')
    
    # Create RLS policies for patient table
    op.execute('''
        CREATE POLICY patient_tenant_isolation
        ON patient
        USING (tenant_id::text = current_setting('app.tenant_id', true));
    ''')
    
    op.execute('''
        CREATE POLICY patient_tenant_isolation_insert
        ON patient
        WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true));
    ''')
    
    op.execute('''
        CREATE POLICY patient_tenant_isolation_update
        ON patient
        USING (tenant_id::text = current_setting('app.tenant_id', true))
        WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true));
    ''')
    
    # Create RLS policies for appointment table
    op.execute('''
        CREATE POLICY appointment_tenant_isolation
        ON appointment
        USING (tenant_id::text = current_setting('app.tenant_id', true));
    ''')
    
    op.execute('''
        CREATE POLICY appointment_tenant_isolation_insert
        ON appointment
        WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true));
    ''')
    
    op.execute('''
        CREATE POLICY appointment_tenant_isolation_update
        ON appointment
        USING (tenant_id::text = current_setting('app.tenant_id', true))
        WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true));
    ''')
    
    # Create RLS policies for audit_log table
    op.execute('''
        CREATE POLICY audit_log_tenant_isolation
        ON audit_log
        USING (tenant_id::text = current_setting('app.tenant_id', true));
    ''')
    
    op.execute('''
        CREATE POLICY audit_log_tenant_isolation_insert
        ON audit_log
        WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true));
    ''')


def downgrade() -> None:
    # Drop RLS policies
    op.execute('DROP POLICY IF EXISTS audit_log_tenant_isolation_insert ON audit_log;')
    op.execute('DROP POLICY IF EXISTS audit_log_tenant_isolation ON audit_log;')
    op.execute('DROP POLICY IF EXISTS appointment_tenant_isolation_update ON appointment;')
    op.execute('DROP POLICY IF EXISTS appointment_tenant_isolation_insert ON appointment;')
    op.execute('DROP POLICY IF EXISTS appointment_tenant_isolation ON appointment;')
    op.execute('DROP POLICY IF EXISTS patient_tenant_isolation_update ON patient;')
    op.execute('DROP POLICY IF EXISTS patient_tenant_isolation_insert ON patient;')
    op.execute('DROP POLICY IF EXISTS patient_tenant_isolation ON patient;')
    
    # Drop tables
    op.drop_table('audit_log')
    op.drop_table('appointment')
    op.drop_table('patient')
    op.drop_table('appointment_state')
    op.drop_table('appointment_modality')
    op.drop_table('gender')
    op.drop_table('document_type')
