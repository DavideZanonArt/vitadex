from __future__ import annotations

from typing import Any

from vitadex.models.plan import PlanRecord, PlanStep
from vitadex.models.skill import SkillManifest
from vitadex.models.task import TaskRecord
from vitadex.skills.base import Skill, SkillContext


class AssetReconciliationSkill(Skill):
    manifest = SkillManifest(
        id="asset_reconciliation",
        name="Asset reconciliation",
        description=(
            "Reconcile local asset inventories across domains, repositories, deployment projects, "
            "builder projects, subscriptions, licenses, contracts, and warranties."
        ),
        area="private_projects",
        trigger_examples=[
            "asset",
            "assets",
            "portfolio",
            "inventory",
            "reconcile",
            "matching",
            "match",
            "domain",
            "repository",
            "github",
            "vercel",
            "lovable",
        ],
        required_inputs=["asset inventories", "asset kinds", "matching goal"],
        optional_inputs=[
            "provider names",
            "known relationships",
            "expiry dates",
            "confidence rules",
            "output path",
        ],
        outputs=[
            "normalized asset list",
            "candidate links",
            "confirmed links",
            "missing-link queue",
            "reconciliation summary",
            "follow-up actions",
        ],
        max_autonomy_level="A3",
        required_tools=["FileSystemTool"],
        approval_requirements=[
            "Writing local inventory files",
            "Connecting live provider accounts",
            "Sharing asset inventory outside the local runtime",
        ],
        risk_level="medium",
        runbook=[
            "Identify the source inventories and expected asset kinds.",
            "Normalize each item into generic asset fields.",
            "Separate confirmed relationships from candidate relationships.",
            "Keep weak matches in a missing-link queue instead of forcing links.",
            "Summarize coverage, risks, and next inventories to collect.",
        ],
        test_examples=[
            {
                "input": "Reconcile GitHub repositories with domains and Vercel projects",
                "matches": True,
            }
        ],
    )

    def plan(self, task: TaskRecord, context: SkillContext) -> PlanRecord:
        memories = [m.id for m in context.get("memories", [])]
        return PlanRecord(
            task_id=task.id,
            objective=task.goal,
            known_context=[task.title, task.description, *task.constraints],
            relevant_memories=memories,
            assumptions=[
                "Real inventories live in the local runtime and are not copied into public examples.",
                "Only exact or externally verified relationships are treated as confirmed.",
                "Name similarity alone produces a candidate link at most.",
            ],
            missing_info=[
                "source inventory files or provider exports",
                "asset kinds to reconcile",
                "known naming conventions",
                "desired output location in the local runtime",
            ],
            risks=[
                "Accidentally publishing private asset names or provider metadata.",
                "Creating false dependencies from weak name similarity.",
                "Missing private repositories or projects when using public-only provider data.",
            ],
            recommended_strategy=(
                "Use a conservative pass that normalizes assets, records only strong links, "
                "and leaves unresolved items in a missing-link queue for the next provider inventory."
            ),
            steps=[
                PlanStep(
                    title="Inventory sources",
                    description="List the local source files or provider exports and the asset kinds they contain.",
                    tool="FileSystemTool",
                    output="source map",
                ),
                PlanStep(
                    title="Normalize assets",
                    description="Convert each item to generic asset fields without exposing private values in public files.",
                    output="normalized assets",
                ),
                PlanStep(
                    title="Propose links",
                    description="Create confirmed links only for exact or verified relationships; mark name-only matches as candidates.",
                    output="asset links",
                ),
                PlanStep(
                    title="Queue unresolved assets",
                    description="Keep unlinked records in a missing-link queue with the next source needed for validation.",
                    output="missing-link queue",
                ),
                PlanStep(
                    title="Summarize reconciliation",
                    description="Report coverage, unresolved counts, risk notes, and follow-up inventories to collect.",
                    output="summary",
                ),
            ],
            required_skills=["asset_reconciliation", "decision_matrix"],
            required_tools=["FileSystemTool"],
            approval_points=[
                {
                    "action_type": "write_file",
                    "title": "Write local asset reconciliation output",
                    "description": "Write normalized inventory or link results to the configured local runtime.",
                    "risk_level": "medium",
                    "sensitivity_level": "personal",
                }
            ],
            expected_outputs=[
                "Normalized assets",
                "Confirmed links",
                "Candidate links",
                "Missing-link queue",
                "Reconciliation summary",
            ],
            followups=[
                {
                    "title": "Collect the next provider inventory",
                    "trigger_condition": "Assets remain in the missing-link queue",
                    "action": "Export or fetch the next provider inventory before forcing matches",
                    "approval_required": False,
                }
            ],
            final_recommendation_placeholder=(
                "Recommend only confirmed asset relationships and identify the next inventory needed "
                "for unresolved candidate links."
            ),
        )

    def execute(
        self, task: TaskRecord, plan: PlanRecord, context: SkillContext, dry_run: bool = True
    ) -> dict[str, Any]:
        return {
            "dry_run": dry_run,
            "asset_kinds": [
                "domain",
                "github_repository",
                "vercel_project",
                "lovable_project",
                "subscription",
                "license",
                "contract",
                "warranty",
            ],
            "link_confidence_rules": {
                "confirmed": "exact provider relationship or explicit source metadata",
                "candidate": "strong name similarity that still needs provider validation",
                "unknown": "weak or contextual relationship that should stay unresolved",
            },
            "output_sections": [
                "normalized_assets",
                "confirmed_links",
                "candidate_links",
                "missing_links",
                "followups",
            ],
            "recommendation_next": "Collect missing provider inventories before promoting candidate links to confirmed links.",
        }
