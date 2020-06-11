"""empty message

Revision ID: f21b83b954bc
Revises: 9e73140fbdd6
Create Date: 2020-06-10 17:41:56.786976

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f21b83b954bc'
down_revision = '9e73140fbdd6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('role', sa.Column('id', sa.Integer(), nullable=False))
    op.alter_column('role', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.create_unique_constraint(None, 'role', ['rolename'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'role', type_='unique')
    op.alter_column('role', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_column('role', 'id')
    # ### end Alembic commands ###