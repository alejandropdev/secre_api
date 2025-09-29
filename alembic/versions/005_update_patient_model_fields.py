"""Update patient model fields - remove cell_phone and update required fields

Revision ID: 005
Revises: 004
Create Date: 2024-01-01 00:04:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Remove cell_phone column
    op.drop_column('patient', 'cell_phone')
    
    # Update nullable constraints
    # Make birth_date nullable
    op.alter_column('patient', 'birth_date', nullable=True)
    
    # Make gender_id nullable
    op.alter_column('patient', 'gender_id', nullable=True)
    
    # Make phone required (nullable=False)
    op.alter_column('patient', 'phone', nullable=False)
    
    # Make email required (nullable=False)
    op.alter_column('patient', 'email', nullable=False)


def downgrade() -> None:
    # Add cell_phone column back
    op.add_column('patient', sa.Column('cell_phone', sa.String(length=20), nullable=True))
    
    # Revert nullable constraints
    # Make birth_date required again
    op.alter_column('patient', 'birth_date', nullable=False)
    
    # Make gender_id required again
    op.alter_column('patient', 'gender_id', nullable=False)
    
    # Make phone optional again
    op.alter_column('patient', 'phone', nullable=True)
    
    # Make email optional again
    op.alter_column('patient', 'email', nullable=True)
