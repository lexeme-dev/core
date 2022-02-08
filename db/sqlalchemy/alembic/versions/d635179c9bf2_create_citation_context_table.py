"""create citation context table

Revision ID: d635179c9bf2
Revises: 16c0aeeaeef7
Create Date: 2022-01-21 21:26:04.782612

"""
from alembic import op, context
import sqlalchemy as sa
from sqlalchemy.schema import Sequence, CreateSequence


# revision identifiers, used by Alembic.
revision = "d635179c9bf2"
down_revision = "16c0aeeaeef7"
branch_labels = None
depends_on = None


def upgrade():
    if context.get_x_argument(as_dictionary=True).get("data", None):
        data_upgrade()
    op.execute(CreateSequence(Sequence("citationcontext_id_seq")))
    op.create_table(
        "citationcontext",
        sa.Column(
            "id",
            sa.Integer(),
            server_default=sa.text("nextval('citationcontext_id_seq')"),
            nullable=False,
        ),
        sa.Column("citing_opinion_id", sa.Integer(), nullable=False),
        sa.Column("cited_opinion_id", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ionparenthetical_cited_opinion_id",
        "citationcontext",
        ["cited_opinion_id"],
        unique=False,
    )
    op.create_index(
        "citationcontext_citing_opinion_id",
        "citationcontext",
        ["citing_opinion_id"],
        unique=False,
    )


def downgrade():
    if context.get_x_argument(as_dictionary=True).get("data", None):
        data_downgrade()
    op.drop_index("citationcontext_citing_opinion_id", table_name="citationcontext")
    op.drop_index("citationcontext_cited_opinion_id", table_name="citationcontext")
    op.drop_table("citationcontext")


def data_upgrade():
    pass


def data_downgrade():
    pass
