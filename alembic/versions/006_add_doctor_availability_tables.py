"""Add doctor availability tables

Revision ID: 006
Revises: 005
Create Date: 2024-01-01 00:06:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create doctor_availability table
    op.create_table('doctor_availability',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('doctor_document_type_id', sa.Integer(), nullable=False),
        sa.Column('doctor_document_number', sa.String(length=50), nullable=False),
        sa.Column('day_of_week', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('appointment_duration_minutes', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('custom_fields', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create doctor_blocked_time table
    op.create_table('doctor_blocked_time',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('doctor_document_type_id', sa.Integer(), nullable=False),
        sa.Column('doctor_document_number', sa.String(length=50), nullable=False),
        sa.Column('start_datetime', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_datetime', sa.DateTime(timezone=True), nullable=False),
        sa.Column('reason', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('custom_fields', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_doctor_availability_tenant_id'), 'doctor_availability', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_doctor_availability_doctor_doc'), 'doctor_availability', ['doctor_document_type_id', 'doctor_document_number'], unique=False)
    op.create_index(op.f('ix_doctor_availability_day_of_week'), 'doctor_availability', ['day_of_week'], unique=False)
    op.create_index('ix_doctor_availability_custom_fields', 'doctor_availability', ['custom_fields'], unique=False, postgresql_using='gin')
    
    op.create_index(op.f('ix_doctor_blocked_time_tenant_id'), 'doctor_blocked_time', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_doctor_blocked_time_doctor_doc'), 'doctor_blocked_time', ['doctor_document_type_id', 'doctor_document_number'], unique=False)
    op.create_index(op.f('ix_doctor_blocked_time_start_datetime'), 'doctor_blocked_time', ['start_datetime'], unique=False)
    op.create_index('ix_doctor_blocked_time_custom_fields', 'doctor_blocked_time', ['custom_fields'], unique=False, postgresql_using='gin')
    
    # Enable RLS on new tables
    op.execute('ALTER TABLE doctor_availability ENABLE ROW LEVEL SECURITY;')
    op.execute('ALTER TABLE doctor_blocked_time ENABLE ROW LEVEL SECURITY;')
    
    # Create RLS policies for doctor_availability table
    op.execute('''
        CREATE POLICY doctor_availability_tenant_isolation
        ON doctor_availability
        USING (tenant_id::text = current_setting('app.tenant_id', true));
    ''')
    
    op.execute('''
        CREATE POLICY doctor_availability_tenant_isolation_insert
        ON doctor_availability
        WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true));
    ''')
    
    op.execute('''
        CREATE POLICY doctor_availability_tenant_isolation_update
        ON doctor_availability
        USING (tenant_id::text = current_setting('app.tenant_id', true))
        WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true));
    ''')
    
    # Create RLS policies for doctor_blocked_time table
    op.execute('''
        CREATE POLICY doctor_blocked_time_tenant_isolation
        ON doctor_blocked_time
        USING (tenant_id::text = current_setting('app.tenant_id', true));
    ''')
    
    op.execute('''
        CREATE POLICY doctor_blocked_time_tenant_isolation_insert
        ON doctor_blocked_time
        WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true));
    ''')
    
    op.execute('''
        CREATE POLICY doctor_blocked_time_tenant_isolation_update
        ON doctor_blocked_time
        USING (tenant_id::text = current_setting('app.tenant_id', true))
        WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true));
    ''')


def downgrade() -> None:
    # Drop RLS policies
    op.execute('DROP POLICY IF EXISTS doctor_blocked_time_tenant_isolation_update ON doctor_blocked_time;')
    op.execute('DROP POLICY IF EXISTS doctor_blocked_time_tenant_isolation_insert ON doctor_blocked_time;')
    op.execute('DROP POLICY IF EXISTS doctor_blocked_time_tenant_isolation ON doctor_blocked_time;')
    
    op.execute('DROP POLICY IF EXISTS doctor_availability_tenant_isolation_update ON doctor_availability;')
    op.execute('DROP POLICY IF EXISTS doctor_availability_tenant_isolation_insert ON doctor_availability;')
    op.execute('DROP POLICY IF EXISTS doctor_availability_tenant_isolation ON doctor_availability;')
    
    # Drop tables
    op.drop_table('doctor_blocked_time')
    op.drop_table('doctor_availability')
