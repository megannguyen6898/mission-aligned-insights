"""Add workspace, dataset, workflow, and AI event tables."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20240709_add_mvp_tables"
down_revision = "fcb3e9d30177"
branch_labels = None
depends_on = None


def upgrade():
    workspacerole = sa.Enum("admin", "member", "viewer", name="workspacerole")
    workflowstep = sa.Enum("upload", "validate", "ingest", name="workflowstep")
    workflowstate = sa.Enum("queued", "running", "succeeded", "failed", name="workflowstate")

    bind = op.get_bind()
    workspacerole.create(bind, checkfirst=True)
    workflowstep.create(bind, checkfirst=True)
    workflowstate.create(bind, checkfirst=True)

    op.create_table(
        "workspaces",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False, unique=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    op.create_table(
        "workspace_members",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("workspace_id", sa.Integer(), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("role", workspacerole, nullable=False, server_default="member"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    op.execute("ALTER TYPE uploadfilestatus ADD VALUE IF NOT EXISTS 'created'")
    op.execute("ALTER TYPE uploadfilestatus ADD VALUE IF NOT EXISTS 'uploaded'")

    op.add_column("uploads", sa.Column("workspace_id", sa.Integer(), nullable=True))
    op.add_column("uploads", sa.Column("checksum", sa.String(), nullable=True))
    op.add_column("uploads", sa.Column("error_message", sa.Text(), nullable=True))
    op.create_foreign_key(
        "fk_uploads_workspace",
        "uploads",
        "workspaces",
        ["workspace_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "datasets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", sa.Integer(), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("upload_id", sa.Integer(), sa.ForeignKey("uploads.id"), nullable=True),
        sa.Column("schema", sa.JSON(), nullable=True),
        sa.Column("preview", sa.JSON(), nullable=True),
        sa.Column("row_count", sa.Integer(), nullable=True),
        sa.Column("table_name", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    op.create_table(
        "workflows",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", sa.Integer(), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("upload_id", sa.Integer(), sa.ForeignKey("uploads.id"), nullable=True),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("datasets.id"), nullable=True),
        sa.Column("step", workflowstep, nullable=False),
        sa.Column("state", workflowstate, nullable=False, server_default="queued"),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("progress", sa.Integer(), nullable=True),
        sa.Column("meta", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    op.create_table(
        "ai_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", sa.Integer(), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("datasets.id"), nullable=True),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("ai_events")
    op.drop_table("workflows")
    op.drop_table("datasets")
    op.drop_constraint("fk_uploads_workspace", "uploads", type_="foreignkey")
    op.drop_column("uploads", "error_message")
    op.drop_column("uploads", "checksum")
    op.drop_column("uploads", "workspace_id")
    op.drop_table("workspace_members")
    op.drop_table("workspaces")

    bind = op.get_bind()
    sa.Enum(name="workflowstate").drop(bind, checkfirst=True)
    sa.Enum(name="workflowstep").drop(bind, checkfirst=True)
    sa.Enum(name="workspacerole").drop(bind, checkfirst=True)
