"""Add foreign key marking to cluster_id

Revision ID: be78a520d420
Revises: 3afbcc77e96b
Create Date: 2021-12-18 10:05:18.738711

"""
from alembic import op, context
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'be78a520d420'
down_revision = '3afbcc77e96b'
branch_labels = None
depends_on = None


def upgrade():
    if context.get_x_argument(as_dictionary=True).get('data', None):
        data_upgrade()
    try:
        # ### commands auto generated by Alembic - please adjust! ###
        op.drop_index('ix_opinion_cluster_id', table_name='opinion')
        op.create_foreign_key(None, 'opinion', 'cluster', ['cluster_id'], ['resource_id'])
    # ### end Alembic commands ###
    except BaseException as e:
        print("Revision be78a520 failed to apply. Try rerunning the upgrade with data set to true:"
              " alembic upgrade -x data=true [revision]"
              " NOTE: This will drop opinions with missing clusters to allow the foreign key constraint to take effect.")
        raise e


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('opinion_cluster_id_fkey', 'opinion', type_='foreignkey')
    op.create_index('ix_opinion_cluster_id', 'opinion', ['cluster_id'], unique=False)
    # ### end Alembic commands ###
    if context.get_x_argument(as_dictionary=True).get('data', None):
        data_downgrade()


def data_upgrade():
    op.execute("DELETE FROM opinion WHERE cluster_id NOT IN (SELECT resource_id FROM cluster);")
    op.execute("DELETE FROM citation WHERE citing_opinion_id NOT IN (SELECT resource_id FROM opinion);")
    op.execute("DELETE FROM citation WHERE cited_opinion_id NOT IN (SELECT resource_id FROM opinion);")


def data_downgrade():
    pass