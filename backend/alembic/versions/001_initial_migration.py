"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-02-14 12:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create institutions table
    op.create_table('institutions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('sector', sa.Enum('GOVERNMENT', 'HEALTHCARE', 'EDUCATION', 'FINANCE', 'RETAIL', 'OTHER', name='institutionsector'), nullable=True),
        sa.Column('contact_email', sa.String(length=255), nullable=True),
        sa.Column('contact_phone', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_institutions_id'), 'institutions', ['id'], unique=False)
    op.create_index(op.f('ix_institutions_name'), 'institutions', ['name'], unique=True)
    
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('institution_id', sa.Integer(), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('SUPERADMIN', 'ADMIN', 'OPERATOR', name='userrole'), nullable=True),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Integer(), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # Create sessions table
    op.create_table('sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('institution_id', sa.Integer(), nullable=False),
        sa.Column('operator_id', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('turns_count', sa.Integer(), nullable=True),
        sa.Column('stt_attempts', sa.Integer(), nullable=True),
        sa.Column('lsp_attempts', sa.Integer(), nullable=True),
        sa.Column('lsp_failed_attempts', sa.Integer(), nullable=True),
        sa.Column('text_fallback_count', sa.Integer(), nullable=True),
        sa.Column('avg_confidence', sa.Float(), nullable=True),
        sa.Column('total_duration_seconds', sa.Integer(), nullable=True),
        sa.Column('operator_notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['operator_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sessions_id'), 'sessions', ['id'], unique=False)
    
    # Create metrics_daily table
    op.create_table('metrics_daily',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('institution_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('sessions_count', sa.Integer(), nullable=True),
        sa.Column('avg_duration_minutes', sa.Float(), nullable=True),
        sa.Column('total_turns', sa.Integer(), nullable=True),
        sa.Column('lsp_total_attempts', sa.Integer(), nullable=True),
        sa.Column('lsp_successful_attempts', sa.Integer(), nullable=True),
        sa.Column('lsp_avg_confidence', sa.Float(), nullable=True),
        sa.Column('text_fallback_count', sa.Integer(), nullable=True),
        sa.Column('avg_turns_per_session', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_metrics_daily_date'), 'metrics_daily', ['date'], unique=False)
    op.create_index(op.f('ix_metrics_daily_id'), 'metrics_daily', ['id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_metrics_daily_id'), table_name='metrics_daily')
    op.drop_index(op.f('ix_metrics_daily_date'), table_name='metrics_daily')
    op.drop_table('metrics_daily')
    op.drop_index(op.f('ix_sessions_id'), table_name='sessions')
    op.drop_table('sessions')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_institutions_name'), table_name='institutions')
    op.drop_index(op.f('ix_institutions_id'), table_name='institutions')
    op.drop_table('institutions')
