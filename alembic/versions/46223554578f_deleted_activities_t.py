"""deleted activities table

Revision ID: 46223554578f
Revises: f155ce1c832
Create Date: 2013-06-06 14:49:47.685250

"""

# revision identifiers, used by Alembic.
revision = '46223554578f'
down_revision = 'f155ce1c832'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('deleted_activity',
    sa.Column('iati_identifier', sa.Unicode(), nullable=False),
    sa.Column('deletion_date', sa.Date(), nullable=True),
    sa.PrimaryKeyConstraint('iati_identifier')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('deleted_activity')
    ### end Alembic commands ###
