"""add role to users

Revision ID: 07a999e9d606
Revises: 1be834d42a8c
Create Date: 2026-10-07 18:17:33.385885
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "07a999e9d606"
down_revision: Union[str, Sequence[str], None] = "1be834d42a8c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.String(length=20),
            nullable=False,
            server_default="user",
        ),
    )

    op.alter_column(
        "users",
        "role",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_column("users", "role")