"""Initial migration with RLS setup

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_migration'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable required extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')
    
    # Create app schema for RLS
    op.execute('CREATE SCHEMA IF NOT EXISTS app;')
    
    # Create tenant table
    op.create_table('tenant',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create api_key table
    op.create_table('api_key',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('key_hash', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenant.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key_hash')
    )
    
    # Create indexes
    op.create_index(op.f('ix_api_key_tenant_id'), 'api_key', ['tenant_id'], unique=False)
    
    # Enable RLS on tenant table
    op.execute('ALTER TABLE tenant ENABLE ROW LEVEL SECURITY;')
    
    # Enable RLS on api_key table
    op.execute('ALTER TABLE api_key ENABLE ROW LEVEL SECURITY;')
    
    # Create RLS policies for tenant table
    op.execute('''
        CREATE POLICY tenant_tenant_isolation
        ON tenant
        USING (id::text = current_setting('app.tenant_id', true));
    ''')
    
    op.execute('''
        CREATE POLICY tenant_tenant_isolation_insert
        ON tenant
        WITH CHECK (id::text = current_setting('app.tenant_id', true));
    ''')
    
    op.execute('''
        CREATE POLICY tenant_tenant_isolation_update
        ON tenant
        USING (id::text = current_setting('app.tenant_id', true))
        WITH CHECK (id::text = current_setting('app.tenant_id', true));
    ''')
    
    # Create RLS policies for api_key table
    op.execute('''
        CREATE POLICY api_key_tenant_isolation
        ON api_key
        USING (tenant_id::text = current_setting('app.tenant_id', true));
    ''')
    
    op.execute('''
        CREATE POLICY api_key_tenant_isolation_insert
        ON api_key
        WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true));
    ''')
    
    op.execute('''
        CREATE POLICY api_key_tenant_isolation_update
        ON api_key
        USING (tenant_id::text = current_setting('app.tenant_id', true))
        WITH CHECK (tenant_id::text = current_setting('app.tenant_id', true));
    ''')


def downgrade() -> None:
    # Drop RLS policies
    op.execute('DROP POLICY IF EXISTS api_key_tenant_isolation_update ON api_key;')
    op.execute('DROP POLICY IF EXISTS api_key_tenant_isolation_insert ON api_key;')
    op.execute('DROP POLICY IF EXISTS api_key_tenant_isolation ON api_key;')
    op.execute('DROP POLICY IF EXISTS tenant_tenant_isolation_update ON tenant;')
    op.execute('DROP POLICY IF EXISTS tenant_tenant_isolation_insert ON tenant;')
    op.execute('DROP POLICY IF EXISTS tenant_tenant_isolation ON tenant;')
    
    # Drop tables
    op.drop_table('api_key')
    op.drop_table('tenant')
    
    # Drop schema
    op.execute('DROP SCHEMA IF EXISTS app;')
