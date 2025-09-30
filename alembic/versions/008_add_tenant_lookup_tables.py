"""Add tenant-specific lookup tables for appointment types and clinics

Revision ID: 008_add_tenant_lookup_tables
Revises: 007_update_appointment_modality_state_to_ids
Create Date: 2024-01-15 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '008_add_tenant_lookup_tables'
down_revision = '007_update_appointment_modality_state_to_ids'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create tenant appointment type table
    op.create_table('tenant_appointment_type',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.String(length=10), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'code', name='uq_tenant_appointment_type_code')
    )
    
    # Create tenant clinic table
    op.create_table('tenant_clinic',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.String(length=10), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'code', name='uq_tenant_clinic_code')
    )
    
    # Add foreign key columns to appointment table
    op.add_column('appointment', sa.Column('appointment_type_id', sa.Integer(), nullable=True))
    op.add_column('appointment', sa.Column('clinic_id', sa.Integer(), nullable=True))
    
    # Create foreign key constraints
    op.create_foreign_key('fk_appointment_appointment_type', 'appointment', 'tenant_appointment_type', ['appointment_type_id'], ['id'])
    op.create_foreign_key('fk_appointment_clinic', 'appointment', 'tenant_clinic', ['clinic_id'], ['id'])
    
    # Create indexes for better performance
    op.create_index('idx_tenant_appointment_type_tenant_id', 'tenant_appointment_type', ['tenant_id'])
    op.create_index('idx_tenant_appointment_type_code', 'tenant_appointment_type', ['code'])
    op.create_index('idx_tenant_appointment_type_active', 'tenant_appointment_type', ['is_active'])
    
    op.create_index('idx_tenant_clinic_tenant_id', 'tenant_clinic', ['tenant_id'])
    op.create_index('idx_tenant_clinic_code', 'tenant_clinic', ['code'])
    op.create_index('idx_tenant_clinic_active', 'tenant_clinic', ['is_active'])


def downgrade() -> None:
    # Drop foreign key constraints
    op.drop_constraint('fk_appointment_clinic', 'appointment', type_='foreignkey')
    op.drop_constraint('fk_appointment_appointment_type', 'appointment', type_='foreignkey')
    
    # Drop foreign key columns
    op.drop_column('appointment', 'clinic_id')
    op.drop_column('appointment', 'appointment_type_id')
    
    # Drop indexes
    op.drop_index('idx_tenant_clinic_active', 'tenant_clinic')
    op.drop_index('idx_tenant_clinic_code', 'tenant_clinic')
    op.drop_index('idx_tenant_clinic_tenant_id', 'tenant_clinic')
    
    op.drop_index('idx_tenant_appointment_type_active', 'tenant_appointment_type')
    op.drop_index('idx_tenant_appointment_type_code', 'tenant_appointment_type')
    op.drop_index('idx_tenant_appointment_type_tenant_id', 'tenant_appointment_type')
    
    # Drop tables
    op.drop_table('tenant_clinic')
    op.drop_table('tenant_appointment_type')
