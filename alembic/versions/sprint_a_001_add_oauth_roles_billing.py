"""Add Google OAuth, roles, security, and billing tables

Revision ID: sprint_a_001
Revises: 
Create Date: 2026-07-29

"""
from alembic import op
import sqlalchemy as sa

revision = "sprint_a_001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to users table
    op.add_column("users", sa.Column("google_id", sa.String(), nullable=True, unique=True))
    op.add_column("users", sa.Column("email", sa.String(), nullable=True, unique=True))
    op.add_column("users", sa.Column("name", sa.String(), server_default=""))
    op.add_column("users", sa.Column("avatar_url", sa.String(), server_default=""))
    op.add_column("users", sa.Column("role", sa.String(), server_default="user"))
    op.add_column("users", sa.Column("is_banned", sa.Boolean(), server_default=sa.text("false")))
    op.add_column("users", sa.Column("ban_reason", sa.String(), nullable=True))
    op.add_column("users", sa.Column("banned_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("banned_by", sa.String(), nullable=True))
    op.add_column("users", sa.Column("email_verified", sa.Boolean(), server_default=sa.text("true")))
    op.add_column("users", sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("last_login_ip", sa.String(), nullable=True))
    op.add_column("users", sa.Column("login_count", sa.Integer(), server_default=sa.text("0")))
    op.add_column("users", sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()))
    op.add_column("users", sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()))

    # Create purchases table
    op.create_table(
        "purchases",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.String(), nullable=False, index=True),
        sa.Column("order_id", sa.String(), unique=True, nullable=False),
        sa.Column("plan", sa.String(), nullable=False),
        sa.Column("price_usd", sa.Float(), nullable=False),
        sa.Column("currency_paid", sa.String(), server_default=""),
        sa.Column("amount_paid", sa.Float(), server_default=sa.text("0")),
        sa.Column("status", sa.String(), server_default="pending"),
        sa.Column("np_invoice_id", sa.String(), nullable=True),
        sa.Column("license_key", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("purchases")
    op.drop_column("users", "updated_at")
    op.drop_column("users", "created_at")
    op.drop_column("users", "login_count")
    op.drop_column("users", "last_login_ip")
    op.drop_column("users", "last_login_at")
    op.drop_column("users", "email_verified")
    op.drop_column("users", "banned_by")
    op.drop_column("users", "banned_at")
    op.drop_column("users", "ban_reason")
    op.drop_column("users", "is_banned")
    op.drop_column("users", "role")
    op.drop_column("users", "avatar_url")
    op.drop_column("users", "name")
    op.drop_column("users", "email")
    op.drop_column("users", "google_id")
