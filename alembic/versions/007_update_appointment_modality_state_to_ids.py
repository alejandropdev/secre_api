"""Update appointment modality and state to use IDs

Revision ID: 007_update_appointment_modality_state_to_ids
Revises: 006_add_doctor_availability_tables
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new foreign key columns
    op.add_column('appointment', sa.Column('modality_id', sa.Integer(), nullable=True))
    op.add_column('appointment', sa.Column('state_id', sa.Integer(), nullable=True))
    
    # Create foreign key constraints
    op.create_foreign_key('fk_appointment_modality', 'appointment', 'appointment_modality', ['modality_id'], ['id'])
    op.create_foreign_key('fk_appointment_state', 'appointment', 'appointment_state', ['state_id'], ['id'])
    
    # Update existing data - map string values to IDs
    # First, let's assume we have some default data in the lookup tables
    # We'll map common values to IDs 1 and 2 as defaults
    
    # Update modality mappings
    op.execute("""
        UPDATE appointment 
        SET modality_id = 1 
        WHERE modality = 'presencial' OR modality = 'in-person' OR modality = 'in_person'
    """)
    
    op.execute("""
        UPDATE appointment 
        SET modality_id = 2 
        WHERE modality = 'virtual' OR modality = 'telemedicina' OR modality = 'telemedicine'
    """)
    
    op.execute("""
        UPDATE appointment 
        SET modality_id = 3 
        WHERE modality = 'domicilio' OR modality = 'home' OR modality = 'house_call'
    """)
    
    # Update state mappings
    op.execute("""
        UPDATE appointment 
        SET state_id = 1 
        WHERE state = 'scheduled' OR state = 'agendada' OR state = 'programada'
    """)
    
    op.execute("""
        UPDATE appointment 
        SET state_id = 2 
        WHERE state = 'confirmed' OR state = 'confirmada'
    """)
    
    op.execute("""
        UPDATE appointment 
        SET state_id = 3 
        WHERE state = 'cancelled' OR state = 'cancelada'
    """)
    
    op.execute("""
        UPDATE appointment 
        SET state_id = 4 
        WHERE state = 'completed' OR state = 'completada' OR state = 'finalizada'
    """)
    
    # Set default values for any remaining null values
    op.execute("UPDATE appointment SET modality_id = 1 WHERE modality_id IS NULL")
    op.execute("UPDATE appointment SET state_id = 1 WHERE state_id IS NULL")
    
    # Make the columns non-nullable
    op.alter_column('appointment', 'modality_id', nullable=False)
    op.alter_column('appointment', 'state_id', nullable=False)
    
    # Drop the old string columns
    op.drop_column('appointment', 'modality')
    op.drop_column('appointment', 'state')


def downgrade() -> None:
    # Add back the string columns
    op.add_column('appointment', sa.Column('modality', sa.String(length=50), nullable=True))
    op.add_column('appointment', sa.Column('state', sa.String(length=50), nullable=True))
    
    # Map IDs back to string values
    op.execute("""
        UPDATE appointment 
        SET modality = 'presencial' 
        WHERE modality_id = 1
    """)
    
    op.execute("""
        UPDATE appointment 
        SET modality = 'virtual' 
        WHERE modality_id = 2
    """)
    
    op.execute("""
        UPDATE appointment 
        SET modality = 'domicilio' 
        WHERE modality_id = 3
    """)
    
    op.execute("""
        UPDATE appointment 
        SET state = 'scheduled' 
        WHERE state_id = 1
    """)
    
    op.execute("""
        UPDATE appointment 
        SET state = 'confirmed' 
        WHERE state_id = 2
    """)
    
    op.execute("""
        UPDATE appointment 
        SET state = 'cancelled' 
        WHERE state_id = 3
    """)
    
    op.execute("""
        UPDATE appointment 
        SET state = 'completed' 
        WHERE state_id = 4
    """)
    
    # Make the string columns non-nullable
    op.alter_column('appointment', 'modality', nullable=False)
    op.alter_column('appointment', 'state', nullable=False)
    
    # Drop foreign key constraints
    op.drop_constraint('fk_appointment_state', 'appointment', type_='foreignkey')
    op.drop_constraint('fk_appointment_modality', 'appointment', type_='foreignkey')
    
    # Drop the ID columns
    op.drop_column('appointment', 'state_id')
    op.drop_column('appointment', 'modality_id')
