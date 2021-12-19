"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op, context
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade():
    ${upgrades if upgrades else "pass"}
    if context.get_x_argument(as_dictionary=True).get('data', None):
        data_upgrade()


def downgrade():
    ${downgrades if downgrades else "pass"}
    if context.get_x_argument(as_dictionary=True).get('data', None):
        data_downgrade()


def data_upgrade():
    pass


def data_downgrade():
    pass
