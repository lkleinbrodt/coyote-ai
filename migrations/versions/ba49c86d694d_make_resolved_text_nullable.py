"""make resolved_text nullable

Revision ID: ba49c86d694d
Revises: 65c654601a7f
Create Date: 2025-09-02 15:29:42.489764

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ba49c86d694d"
down_revision = "65c654601a7f"
branch_labels = None
depends_on = None


def upgrade():
    # Make resolved_text column nullable
    op.alter_column(
        "sidequest_user_quests",
        "resolved_text",
        existing_type=sa.Text(),
        nullable=True,
        schema="sidequest",
    )


def downgrade():
    # Make resolved_text column not nullable again
    op.alter_column(
        "sidequest_user_quests",
        "resolved_text",
        existing_type=sa.Text(),
        nullable=False,
        schema="sidequest",
    )
