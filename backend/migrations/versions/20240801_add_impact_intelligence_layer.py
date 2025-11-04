"""Add Impact Intelligence Layer models and tables."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import expression

# revision identifiers, used by Alembic.
revision = "20240801_add_impact_intelligence_layer"
down_revision = "20240709_add_mvp_tables"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("metrics", "outcome_id", existing_type=sa.String(), nullable=True)

    op.add_column("metrics", sa.Column("workspace_id", sa.Integer(), nullable=True))
    op.add_column("metrics", sa.Column("code", sa.String(), nullable=True))
    op.add_column("metrics", sa.Column("description", sa.Text(), nullable=True))
    op.add_column("metrics", sa.Column("unit", sa.String(), nullable=True))
    op.add_column("metrics", sa.Column("category", sa.String(), nullable=True))
    op.add_column("metrics", sa.Column("aggregation_method", sa.String(), nullable=True))
    op.add_column("metrics", sa.Column("source", sa.String(), nullable=True))
    op.add_column("metrics", sa.Column("is_active", sa.Boolean(), server_default=expression.true(), nullable=False))
    op.add_column("metrics", sa.Column("is_library", sa.Boolean(), server_default=expression.false(), nullable=False))
    op.add_column("metrics", sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True))
    op.add_column("metrics", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True))

    op.create_index("ix_metrics_code", "metrics", ["code"], unique=True)
    op.create_foreign_key(
        "fk_metrics_workspace",
        "metrics",
        "workspaces",
        ["workspace_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "metric_mappings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("metric_id", sa.Integer(), sa.ForeignKey("metrics.id", ondelete="CASCADE"), nullable=False),
        sa.Column("column_name", sa.String(), nullable=False),
        sa.Column("column_sample", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("suggested_by_ai", sa.Boolean(), server_default=expression.false(), nullable=False),
        sa.Column("confirmed", sa.Boolean(), server_default=expression.false(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_metric_mappings_dataset", "metric_mappings", ["dataset_id"])
    op.create_index("ix_metric_mappings_metric", "metric_mappings", ["metric_id"])
    op.create_index("ix_metric_mappings_column", "metric_mappings", ["column_name"])

    op.create_table(
        "sdg_goals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("short_title", sa.String(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("color", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("number", name="uq_sdg_goals_number"),
    )

    op.create_table(
        "sdg_targets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("goal_id", sa.Integer(), sa.ForeignKey("sdg_goals.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("code", name="uq_sdg_targets_code"),
    )
    op.create_index("ix_sdg_targets_goal", "sdg_targets", ["goal_id"])

    op.create_table(
        "sdg_indicators",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("target_id", sa.Integer(), sa.ForeignKey("sdg_targets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("guidance", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("code", name="uq_sdg_indicators_code"),
    )
    op.create_index("ix_sdg_indicators_target", "sdg_indicators", ["target_id"])

    op.create_table(
        "metric_sdg_mapping",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("metric_id", sa.Integer(), sa.ForeignKey("metrics.id", ondelete="CASCADE"), nullable=False),
        sa.Column("indicator_id", sa.Integer(), sa.ForeignKey("sdg_indicators.id", ondelete="CASCADE"), nullable=False),
        sa.Column("relevance_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("rationale", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("metric_id", "indicator_id", name="uq_metric_indicator"),
    )
    op.create_index("ix_metric_sdg_mapping_metric", "metric_sdg_mapping", ["metric_id"])
    op.create_index("ix_metric_sdg_mapping_indicator", "metric_sdg_mapping", ["indicator_id"])

    op.create_table(
        "benchmark_projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sector", sa.String(), nullable=False),
        sa.Column("metric_id", sa.Integer(), sa.ForeignKey("metrics.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mean_value", sa.Float(), nullable=False),
        sa.Column("std_dev", sa.Float(), nullable=True),
        sa.Column("sample_size", sa.Integer(), nullable=True),
        sa.Column("source", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_benchmark_projects_sector", "benchmark_projects", ["sector"])
    op.create_index("ix_benchmark_projects_metric", "benchmark_projects", ["metric_id"])

    op.create_table(
        "impact_balance_sheet",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("metric_id", sa.Integer(), sa.ForeignKey("metrics.id", ondelete="SET NULL"), nullable=True),
        sa.Column("framework", sa.String(), nullable=False),
        sa.Column("pillar", sa.String(), nullable=True),
        sa.Column("narrative", sa.Text(), nullable=True),
        sa.Column("value", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_impact_balance_sheet_dataset", "impact_balance_sheet", ["dataset_id"])

    op.create_table(
        "correlations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("metric_id", sa.Integer(), sa.ForeignKey("metrics.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sdg_indicator_id", sa.Integer(), sa.ForeignKey("sdg_indicators.id", ondelete="SET NULL"), nullable=True),
        sa.Column("independent_variable", sa.String(), nullable=False),
        sa.Column("r_value", sa.Float(), nullable=False),
        sa.Column("p_value", sa.Float(), nullable=True),
        sa.Column("direction", sa.String(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("computed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_correlations_dataset", "correlations", ["dataset_id"])
    op.create_index("ix_correlations_metric", "correlations", ["metric_id"])


def downgrade():
    op.drop_index("ix_correlations_metric", table_name="correlations")
    op.drop_index("ix_correlations_dataset", table_name="correlations")
    op.drop_table("correlations")

    op.drop_index("ix_impact_balance_sheet_dataset", table_name="impact_balance_sheet")
    op.drop_table("impact_balance_sheet")

    op.drop_index("ix_benchmark_projects_metric", table_name="benchmark_projects")
    op.drop_index("ix_benchmark_projects_sector", table_name="benchmark_projects")
    op.drop_table("benchmark_projects")

    op.drop_index("ix_metric_sdg_mapping_indicator", table_name="metric_sdg_mapping")
    op.drop_index("ix_metric_sdg_mapping_metric", table_name="metric_sdg_mapping")
    op.drop_table("metric_sdg_mapping")

    op.drop_index("ix_sdg_indicators_target", table_name="sdg_indicators")
    op.drop_table("sdg_indicators")

    op.drop_index("ix_sdg_targets_goal", table_name="sdg_targets")
    op.drop_table("sdg_targets")

    op.drop_table("sdg_goals")

    op.drop_index("ix_metric_mappings_column", table_name="metric_mappings")
    op.drop_index("ix_metric_mappings_metric", table_name="metric_mappings")
    op.drop_index("ix_metric_mappings_dataset", table_name="metric_mappings")
    op.drop_table("metric_mappings")

    op.drop_constraint("fk_metrics_workspace", "metrics", type_="foreignkey")
    op.drop_index("ix_metrics_code", table_name="metrics")
    op.drop_column("metrics", "updated_at")
    op.drop_column("metrics", "created_at")
    op.drop_column("metrics", "is_library")
    op.drop_column("metrics", "is_active")
    op.drop_column("metrics", "source")
    op.drop_column("metrics", "aggregation_method")
    op.drop_column("metrics", "category")
    op.drop_column("metrics", "unit")
    op.drop_column("metrics", "description")
    op.drop_column("metrics", "code")
    op.drop_column("metrics", "workspace_id")

    op.alter_column("metrics", "outcome_id", existing_type=sa.String(), nullable=False)
