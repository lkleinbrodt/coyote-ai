"""more artist info

Revision ID: 594b150befb3
Revises: a7fe9939873e
Create Date: 2024-05-05 14:45:54.314206

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '594b150befb3'
down_revision = 'a7fe9939873e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('artists', schema=None) as batch_op:
        batch_op.add_column(sa.Column('url', sa.String(length=128), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('artists', schema=None) as batch_op:
        batch_op.drop_column('url')

    # ### end Alembic commands ###