"""speech

Revision ID: 9345b6e245a3
Revises: b9b9d86c59ad
Create Date: 2025-03-13 11:38:30.975231

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "9345b6e245a3"
down_revision = "b9b9d86c59ad"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("CREATE SCHEMA IF NOT EXISTS speech")
    op.create_table(
        "speech_profile",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("last_seen", sa.DateTime(), nullable=True),
        sa.Column("role", sa.String(length=50), nullable=True),
        sa.Column("speaking_level", sa.String(length=50), nullable=True),
        sa.Column("total_recordings", sa.Integer(), nullable=True),
        sa.Column("total_practice_time", sa.Integer(), nullable=True),
        sa.Column("last_practice", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="speech",
    )
    op.create_table(
        "recording",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("profile_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("duration", sa.Integer(), nullable=True),
        sa.Column("file_path", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["profile_id"],
            ["speech.speech_profile.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="speech",
    )
    op.create_table(
        "analysis",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("recording_id", sa.Integer(), nullable=False),
        sa.Column("transcript", sa.Text(), nullable=True),
        sa.Column("clarity_score", sa.Float(), nullable=True),
        sa.Column("pace_score", sa.Float(), nullable=True),
        sa.Column("filler_word_count", sa.Integer(), nullable=True),
        sa.Column("tone_analysis", sa.JSON(), nullable=True),
        sa.Column("content_structure", sa.JSON(), nullable=True),
        sa.Column("feedback", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["recording_id"],
            ["speech.recording.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="speech",
    )
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("google_id", sa.String(length=255), nullable=True)
        )
        batch_op.add_column(sa.Column("apple_id", sa.String(length=255), nullable=True))
        batch_op.drop_column("social_id")

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "social_id",
                sa.VARCHAR(length=255),
                autoincrement=False,
                nullable=False,
                server_default="1",
            )
        )
        batch_op.drop_column("apple_id")
        batch_op.drop_column("google_id")

    op.drop_table("analysis", schema="speech")
    op.drop_table("recording", schema="speech")
    op.drop_table("speech_profile", schema="speech")
    op.execute("DROP SCHEMA IF EXISTS speech")
    # ### end Alembic commands ###
