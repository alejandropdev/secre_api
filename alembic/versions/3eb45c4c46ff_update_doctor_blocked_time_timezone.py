"""update_doctor_blocked_time_timezone

Revision ID: 3eb45c4c46ff
Revises: 008
Create Date: 2025-10-04 18:57:10.094133

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3eb45c4c46ff'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Update doctor_blocked_time table to use timezone-aware datetime columns
    # First, convert existing data to UTC if needed
    op.execute("""
        UPDATE doctor_blocked_time 
        SET start_datetime = start_datetime AT TIME ZONE 'UTC',
            end_datetime = end_datetime AT TIME ZONE 'UTC'
        WHERE start_datetime IS NOT NULL AND end_datetime IS NOT NULL;
    """)
    
    # Alter the columns to be timezone-aware
    op.alter_column('doctor_blocked_time', 'start_datetime',
                    type_=sa.DateTime(timezone=True),
                    existing_type=sa.DateTime)
    op.alter_column('doctor_blocked_time', 'end_datetime',
                    type_=sa.DateTime(timezone=True),
                    existing_type=sa.DateTime)


def downgrade() -> None:
    # Convert back to naive datetime (not recommended for production)
    op.alter_column('doctor_blocked_time', 'start_datetime',
                    type_=sa.DateTime,
                    existing_type=sa.DateTime(timezone=True))
    op.alter_column('doctor_blocked_time', 'end_datetime',
                    type_=sa.DateTime,
                    existing_type=sa.DateTime(timezone=True))
