"""add_api_key_usage_metrics_table

Revision ID: 009_add_api_key_usage_metrics
Revises: 3eb45c4c46ff_update_doctor_blocked_time_timezone
Create Date: 2024-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '009_add_api_key_usage_metrics'
down_revision = '3eb45c4c46ff_update_doctor_blocked_time_timezone'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create api_key_usage table
    op.create_table('api_key_usage',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('api_key_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('endpoint', sa.String(length=255), nullable=False),
        sa.Column('method', sa.String(length=10), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=False),
        sa.Column('request_count', sa.Integer(), nullable=False),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('usage_date', sa.Date(), nullable=False),
        sa.Column('usage_hour', sa.Integer(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for efficient querying
    op.create_index('idx_api_key_usage_date', 'api_key_usage', ['api_key_id', 'usage_date'])
    op.create_index('idx_api_key_usage_endpoint', 'api_key_usage', ['api_key_id', 'endpoint'])
    op.create_index('idx_tenant_usage_date', 'api_key_usage', ['tenant_id', 'usage_date'])
    op.create_index('idx_usage_date_hour', 'api_key_usage', ['usage_date', 'usage_hour'])
    op.create_index(op.f('ix_api_key_usage_api_key_id'), 'api_key_usage', ['api_key_id'])
    op.create_index(op.f('ix_api_key_usage_tenant_id'), 'api_key_usage', ['tenant_id'])
    op.create_index(op.f('ix_api_key_usage_usage_date'), 'api_key_usage', ['usage_date'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_api_key_usage_usage_date'), table_name='api_key_usage')
    op.drop_index(op.f('ix_api_key_usage_tenant_id'), table_name='api_key_usage')
    op.drop_index(op.f('ix_api_key_usage_api_key_id'), table_name='api_key_usage')
    op.drop_index('idx_usage_date_hour', table_name='api_key_usage')
    op.drop_index('idx_tenant_usage_date', table_name='api_key_usage')
    op.drop_index('idx_api_key_usage_endpoint', table_name='api_key_usage')
    op.drop_index('idx_api_key_usage_date', table_name='api_key_usage')
    
    # Drop table
    op.drop_table('api_key_usage')
