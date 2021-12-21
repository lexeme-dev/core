"""add md5 checksum for opinion and cluster json

Revision ID: f532a873941c
Revises: be78a520d420
Create Date: 2021-12-20 12:22:59.330975

"""
from alembic import op, context
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f532a873941c'
down_revision = 'be78a520d420'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('cluster', sa.Column('courtlistener_json_checksum', sa.String(length=32), nullable=True))
    op.add_column('opinion', sa.Column('courtlistener_json_checksum', sa.String(length=32), nullable=True))
    # ### end Alembic commands ###
    if context.get_x_argument(as_dictionary=True).get('data', None):
        data_upgrade()


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('opinion', 'courtlistener_json_checksum')
    op.drop_column('cluster', 'courtlistener_json_checksum')
    # ### end Alembic commands ###
    if context.get_x_argument(as_dictionary=True).get('data', None):
        data_downgrade()


def data_upgrade():
    pass


def data_downgrade():
    pass