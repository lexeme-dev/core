"""add score column to parenthetical

Revision ID: 3796f484796a
Revises: d635179c9bf2
Create Date: 2022-02-26 16:17:06.483952

"""
from alembic import op, context
import sqlalchemy as sa
from db.sqlalchemy import *
from db.sqlalchemy.models import OpinionParenthetical
from algorithms.description_score import description_score


# revision identifiers, used by Alembic.
from db.sqlalchemy import get_session

revision = "3796f484796a"
down_revision = "d635179c9bf2"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("opinionparenthetical", sa.Column("score", sa.Float(), nullable=True))
    # ### end Alembic commands ###
    if context.get_x_argument(as_dictionary=True).get("data", None):
        data_upgrade()


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("opinionparenthetical", "score")
    # ### end Alembic commands ###
    if context.get_x_argument(as_dictionary=True).get("data", None):
        data_downgrade()


def data_upgrade():
    with get_session() as s:
        for parenthetical in (
            s.execute(
                select(OpinionParenthetical)
            )
            .scalars()
            .all()
        ):
            parenthetical.score = description_score(
                parenthetical.text
            )
        s.commit()


def data_downgrade():
    pass