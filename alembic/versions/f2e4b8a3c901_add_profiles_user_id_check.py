"""add profiles user_id check

Revision ID: f2e4b8a3c901
Revises: 87c017a8f08b
Create Date: 2026-07-29 21:20:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f2e4b8a3c901"
down_revision: str | Sequence[str] | None = "87c017a8f08b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_check_constraint(
        "ck_profiles_user_id_positive",
        "profiles",
        "user_id > 0",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "ck_profiles_user_id_positive",
        "profiles",
        type_="check",
    )
