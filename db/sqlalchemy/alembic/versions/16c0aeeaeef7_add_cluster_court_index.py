"""add cluster court index

Revision ID: 16c0aeeaeef7
Revises: e218cbe0b4bb
Create Date: 2021-12-20 21:58:51.215684

"""
from alembic import op, context
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "16c0aeeaeef7"
down_revision = "e218cbe0b4bb"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f("ix_cluster_court"), "cluster", ["court"], unique=False)
    # ### end Alembic commands ###
    if context.get_x_argument(as_dictionary=True).get("data", None):
        data_upgrade()


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_cluster_court"), table_name="cluster")
    # ### end Alembic commands ###
    if context.get_x_argument(as_dictionary=True).get("data", None):
        data_downgrade()


def data_upgrade():
    pass


def data_downgrade():
    pass
