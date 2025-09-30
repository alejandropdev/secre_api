"""Change lookup tables to integer IDs

Revision ID: 004
Revises: 003
Create Date: 2024-01-01 00:03:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003_seed_lookup_data'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop existing lookup tables (they will be recreated with integer IDs)
    op.drop_table('appointment_state')
    op.drop_table('appointment_modality')
    op.drop_table('gender')
    op.drop_table('document_type')
    
    # Recreate lookup tables with integer primary keys
    op.create_table('document_type',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    
    op.create_table('gender',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    
    op.create_table('appointment_modality',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    
    op.create_table('appointment_state',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    
    # Seed document types with integer IDs
    document_types = [
        {'id': 1, 'code': 'CC', 'name': 'Cédula de Ciudadanía', 'description': 'Colombian national ID'},
        {'id': 2, 'code': 'CE', 'name': 'Cédula de Extranjería', 'description': 'Foreigner ID'},
        {'id': 3, 'code': 'TI', 'name': 'Tarjeta de Identidad', 'description': 'Identity card for minors'},
        {'id': 4, 'code': 'RC', 'name': 'Registro Civil', 'description': 'Birth certificate'},
        {'id': 5, 'code': 'PA', 'name': 'Pasaporte', 'description': 'Passport'},
        {'id': 6, 'code': 'PEP', 'name': 'Permiso especial de Permanencia', 'description': 'Special permanence permit'},
        {'id': 7, 'code': 'PSI', 'name': 'Persona sin identificar', 'description': 'Unidentified person'},
    ]
    
    for doc_type in document_types:
        op.execute(f"""
            INSERT INTO document_type (id, code, name, description, created_at, updated_at)
            VALUES ({doc_type['id']}, '{doc_type['code']}', '{doc_type['name']}', '{doc_type['description']}', NOW(), NOW())
        """)
    
    # Seed genders with integer IDs
    genders = [
        {'id': 1, 'code': 'M', 'name': 'Masculino', 'description': 'Male'},
        {'id': 2, 'code': 'F', 'name': 'Femenino', 'description': 'Female'},
        {'id': 3, 'code': 'O', 'name': 'Otro', 'description': 'Other'},
        {'id': 4, 'code': 'N', 'name': 'No especifica', 'description': 'Not specified'},
    ]
    
    for gender in genders:
        op.execute(f"""
            INSERT INTO gender (id, code, name, description, created_at, updated_at)
            VALUES ({gender['id']}, '{gender['code']}', '{gender['name']}', '{gender['description']}', NOW(), NOW())
        """)
    
    # Seed appointment modalities with integer IDs
    modalities = [
        {'id': 1, 'code': 'IN_PERSON', 'name': 'Presencial', 'description': 'In-person appointment'},
        {'id': 2, 'code': 'VIRTUAL', 'name': 'Virtual', 'description': 'Video call appointment'},
        {'id': 3, 'code': 'PHONE', 'name': 'Telefónica', 'description': 'Phone call appointment'},
        {'id': 4, 'code': 'HOME', 'name': 'Domicilio', 'description': 'Home visit appointment'},
    ]
    
    for modality in modalities:
        op.execute(f"""
            INSERT INTO appointment_modality (id, code, name, description, created_at, updated_at)
            VALUES ({modality['id']}, '{modality['code']}', '{modality['name']}', '{modality['description']}', NOW(), NOW())
        """)
    
    # Seed appointment states with integer IDs
    states = [
        {'id': 1, 'code': 'SCHEDULED', 'name': 'Programada', 'description': 'Appointment scheduled'},
        {'id': 2, 'code': 'CONFIRMED', 'name': 'Confirmada', 'description': 'Appointment confirmed'},
        {'id': 3, 'code': 'IN_PROGRESS', 'name': 'En Progreso', 'description': 'Appointment in progress'},
        {'id': 4, 'code': 'COMPLETED', 'name': 'Completada', 'description': 'Appointment completed'},
        {'id': 5, 'code': 'CANCELLED', 'name': 'Cancelada', 'description': 'Appointment cancelled'},
        {'id': 6, 'code': 'NO_SHOW', 'name': 'No Asistió', 'description': 'Patient did not show up'},
        {'id': 7, 'code': 'RESCHEDULED', 'name': 'Reprogramada', 'description': 'Appointment rescheduled'},
    ]
    
    for state in states:
        op.execute(f"""
            INSERT INTO appointment_state (id, code, name, description, created_at, updated_at)
            VALUES ({state['id']}, '{state['code']}', '{state['name']}', '{state['description']}', NOW(), NOW())
        """)


def downgrade() -> None:
    # Drop tables with integer IDs
    op.drop_table('appointment_state')
    op.drop_table('appointment_modality')
    op.drop_table('gender')
    op.drop_table('document_type')
    
    # Recreate tables with UUID primary keys (reverting to previous state)
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
    
    # Re-seed with UUID data (reverting to previous state)
    document_types = [
        {'id': '11111111-1111-1111-1111-111111111111', 'code': 'CC', 'name': 'Cédula de Ciudadanía', 'description': 'Colombian national ID'},
        {'id': '22222222-2222-2222-2222-222222222222', 'code': 'CE', 'name': 'Cédula de Extranjería', 'description': 'Foreigner ID'},
        {'id': '33333333-3333-3333-3333-333333333333', 'code': 'TI', 'name': 'Tarjeta de Identidad', 'description': 'Identity card for minors'},
        {'id': '44444444-4444-4444-4444-444444444444', 'code': 'RC', 'name': 'Registro Civil', 'description': 'Birth certificate'},
        {'id': '55555555-5555-5555-5555-555555555555', 'code': 'PA', 'name': 'Pasaporte', 'description': 'Passport'},
        {'id': '66666666-6666-6666-6666-666666666666', 'code': 'PEP', 'name': 'Permiso especial de Permanencia', 'description': 'Special permanence permit'},
        {'id': '77777777-7777-7777-7777-777777777777', 'code': 'PSI', 'name': 'Persona sin identificar', 'description': 'Unidentified person'},
    ]
    
    for doc_type in document_types:
        op.execute(f"""
            INSERT INTO document_type (id, code, name, description, created_at, updated_at)
            VALUES ('{doc_type['id']}', '{doc_type['code']}', '{doc_type['name']}', '{doc_type['description']}', NOW(), NOW())
        """)
    
    genders = [
        {'id': '11111111-1111-1111-1111-111111111111', 'code': 'M', 'name': 'Masculino', 'description': 'Male'},
        {'id': '22222222-2222-2222-2222-222222222222', 'code': 'F', 'name': 'Femenino', 'description': 'Female'},
        {'id': '33333333-3333-3333-3333-333333333333', 'code': 'O', 'name': 'Otro', 'description': 'Other'},
        {'id': '44444444-4444-4444-4444-444444444444', 'code': 'N', 'name': 'No especifica', 'description': 'Not specified'},
    ]
    
    for gender in genders:
        op.execute(f"""
            INSERT INTO gender (id, code, name, description, created_at, updated_at)
            VALUES ('{gender['id']}', '{gender['code']}', '{gender['name']}', '{gender['description']}', NOW(), NOW())
        """)
    
    modalities = [
        {'id': '11111111-1111-1111-1111-111111111111', 'code': 'IN_PERSON', 'name': 'Presencial', 'description': 'In-person appointment'},
        {'id': '22222222-2222-2222-2222-222222222222', 'code': 'VIRTUAL', 'name': 'Virtual', 'description': 'Video call appointment'},
        {'id': '33333333-3333-3333-3333-333333333333', 'code': 'PHONE', 'name': 'Telefónica', 'description': 'Phone call appointment'},
        {'id': '44444444-4444-4444-4444-444444444444', 'code': 'HOME', 'name': 'Domicilio', 'description': 'Home visit appointment'},
    ]
    
    for modality in modalities:
        op.execute(f"""
            INSERT INTO appointment_modality (id, code, name, description, created_at, updated_at)
            VALUES ('{modality['id']}', '{modality['code']}', '{modality['name']}', '{modality['description']}', NOW(), NOW())
        """)
    
    states = [
        {'id': '11111111-1111-1111-1111-111111111111', 'code': 'SCHEDULED', 'name': 'Programada', 'description': 'Appointment scheduled'},
        {'id': '22222222-2222-2222-2222-222222222222', 'code': 'CONFIRMED', 'name': 'Confirmada', 'description': 'Appointment confirmed'},
        {'id': '33333333-3333-3333-3333-333333333333', 'code': 'IN_PROGRESS', 'name': 'En Progreso', 'description': 'Appointment in progress'},
        {'id': '44444444-4444-4444-4444-444444444444', 'code': 'COMPLETED', 'name': 'Completada', 'description': 'Appointment completed'},
        {'id': '55555555-5555-5555-5555-555555555555', 'code': 'CANCELLED', 'name': 'Cancelada', 'description': 'Appointment cancelled'},
        {'id': '66666666-6666-6666-6666-666666666666', 'code': 'NO_SHOW', 'name': 'No Asistió', 'description': 'Patient did not show up'},
        {'id': '77777777-7777-7777-7777-777777777777', 'code': 'RESCHEDULED', 'name': 'Reprogramada', 'description': 'Appointment rescheduled'},
    ]
    
    for state in states:
        op.execute(f"""
            INSERT INTO appointment_state (id, code, name, description, created_at, updated_at)
            VALUES ('{state['id']}', '{state['code']}', '{state['name']}', '{state['description']}', NOW(), NOW())
        """)
