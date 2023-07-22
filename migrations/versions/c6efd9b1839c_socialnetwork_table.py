"""socialnetwork table

Revision ID: c6efd9b1839c
Revises: 6ab37cb0fa4d
Create Date: 2018-07-23 17:05:57.111948

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'c6efd9b1839c'
down_revision = '6ab37cb0fa4d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('social_networks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('task_actions', sa.Column('social_network_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'task_actions', 'social_networks', ['social_network_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'task_actions', type_='foreignkey')
    op.drop_column('task_actions', 'social_network_id')
    op.drop_table('social_networks')
    # ### end Alembic commands ###
