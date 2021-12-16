"""Initial migration

Revision ID: bc224e115ea0
Revises: 
Create Date: 2021-12-16 15:56:44.059300

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'bc224e115ea0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('citation',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('citing_opinion_id', sa.BigInteger(), nullable=True),
    sa.Column('cited_opinion_id', sa.BigInteger(), nullable=True),
    sa.Column('depth', sa.BigInteger(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_40711_citation_cited_opinion_id', 'citation', ['cited_opinion_id'], unique=False)
    op.create_index('idx_40711_citation_citing_opinion_id', 'citation', ['citing_opinion_id'], unique=False)
    op.create_table('cluster',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('resource_id', sa.BigInteger(), nullable=True),
    sa.Column('case_name', sa.Text(), nullable=True),
    sa.Column('reporter', sa.Text(), nullable=True),
    sa.Column('citation_count', sa.BigInteger(), nullable=True),
    sa.Column('cluster_uri', sa.Text(), nullable=True),
    sa.Column('docket_uri', sa.Text(), nullable=True),
    sa.Column('year', sa.BigInteger(), nullable=True),
    sa.Column('time', sa.BigInteger(), nullable=True),
    sa.Column('searchable_case_name', postgresql.TSVECTOR(), nullable=True),
    sa.Column('court', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('searchable_case_name_idx', 'cluster', ['searchable_case_name'], unique=False)
    op.create_table('clustercitation',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('citing_cluster_id', sa.BigInteger(), nullable=True),
    sa.Column('cited_cluster_id', sa.BigInteger(), nullable=True),
    sa.Column('depth', sa.BigInteger(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_40753_clustercitation_cited_cluster_id', 'clustercitation', ['cited_cluster_id'], unique=False)
    op.create_index('idx_40753_clustercitation_citing_cluster_id', 'clustercitation', ['citing_cluster_id'], unique=False)
    op.create_table('opinion',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('resource_id', sa.BigInteger(), nullable=True),
    sa.Column('opinion_uri', sa.Text(), nullable=True),
    sa.Column('cluster_uri', sa.Text(), nullable=True),
    sa.Column('cluster_id', sa.BigInteger(), nullable=True),
    sa.Column('html_text', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_40705_opinion_cluster_id', 'opinion', ['cluster_id'], unique=False)
    op.create_table('opinionparenthetical',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('citing_opinion_id', sa.Integer(), nullable=False),
    sa.Column('cited_opinion_id', sa.Integer(), nullable=False),
    sa.Column('text', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('opinionparenthetical_cited_opinion_id', 'opinionparenthetical', ['cited_opinion_id'], unique=False)
    op.create_index('opinionparenthetical_citing_opinion_id', 'opinionparenthetical', ['citing_opinion_id'], unique=False)
    op.create_table('similarity',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('opinion_a_id', sa.BigInteger(), nullable=True),
    sa.Column('opinion_b_id', sa.BigInteger(), nullable=True),
    sa.Column('similarity_index', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_40750_similarity_opinion_a_id', 'similarity', ['opinion_a_id'], unique=False)
    op.create_index('idx_40750_similarity_opinion_b_id', 'similarity', ['opinion_b_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('idx_40750_similarity_opinion_b_id', table_name='similarity')
    op.drop_index('idx_40750_similarity_opinion_a_id', table_name='similarity')
    op.drop_table('similarity')
    op.drop_index('opinionparenthetical_citing_opinion_id', table_name='opinionparenthetical')
    op.drop_index('opinionparenthetical_cited_opinion_id', table_name='opinionparenthetical')
    op.drop_table('opinionparenthetical')
    op.drop_index('idx_40705_opinion_cluster_id', table_name='opinion')
    op.drop_table('opinion')
    op.drop_index('idx_40753_clustercitation_citing_cluster_id', table_name='clustercitation')
    op.drop_index('idx_40753_clustercitation_cited_cluster_id', table_name='clustercitation')
    op.drop_table('clustercitation')
    op.drop_index('searchable_case_name_idx', table_name='cluster')
    op.drop_table('cluster')
    op.drop_index('idx_40711_citation_citing_opinion_id', table_name='citation')
    op.drop_index('idx_40711_citation_cited_opinion_id', table_name='citation')
    op.drop_table('citation')
    # ### end Alembic commands ###
