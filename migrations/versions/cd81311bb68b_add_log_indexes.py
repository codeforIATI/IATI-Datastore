"""Add log indexes

Revision ID: cd81311bb68b
Revises: 864375812164
Create Date: 2024-04-12 13:51:24.890197

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cd81311bb68b'
down_revision = '864375812164'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_log_logger'), 'log', ['logger'], unique=False)
    op.create_index(op.f('ix_log_resource'), 'log', ['resource'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_log_resource'), table_name='log')
    op.drop_index(op.f('ix_log_logger'), table_name='log')
    # ### end Alembic commands ###
