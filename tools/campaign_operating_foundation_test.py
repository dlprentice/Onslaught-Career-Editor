#!/usr/bin/env python3
"""Regression tests for the durable single-root campaign foundation."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CANONICAL_GOAL = """
Continuously reverse engineer and reconstruct Battle Engine Aquila through an
evidence-backed, multi-slice campaign. Resume from the repository’s current
baton, autonomously pursue the highest-value actionable work across retail RE,
deterministic Core/Godot reconstruction, WinUI tooling, assets, documentation,
and regression harnesses. Translate static analysis and explicitly authorized
copied-runtime observations into bounded behavior contracts before implementing
retail-derived behavior. Preserve provenance, honest non-claims, tests, and
resume-ready state after every slice. Keep the installed game and original
BEA.exe immutable, proprietary evidence local, and release/online/destructive
actions separately authorized. Continue until campaign exit criteria, a human
pause, or a genuine authority blocker; one advancement is progress, not goal
completion. Operate unattended: make conservative, reversible assumptions and
build automated visual, behavioral, capture/replay, and regression harnesses
wherever they can replace subjective human verification. Do not pause for
ordinary clarification. If one slice genuinely needs unavailable authority or
human interaction, record the exact blocker and continue with the next safe,
independent campaign slice. Stop only when no meaningful authorized work
remains.
"""


def read_repo_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def normalized_words(value: str) -> str:
    return " ".join(value.split())


def markdown_h2_section(value: str, title: str) -> str:
    marker = f"## {title}"
    start = value.find(marker)
    if start < 0:
        raise AssertionError(f"missing Markdown section: {marker}")
    body_start = start + len(marker)
    next_section = value.find("\n## ", body_start)
    return value[body_start:] if next_section < 0 else value[body_start:next_section]


class CampaignOperatingFoundationTests(unittest.TestCase):
    def assert_contains_all(self, text: str, phrases: tuple[str, ...]) -> None:
        normalized_text = normalized_words(text).casefold()
        for phrase in phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(normalized_words(phrase).casefold(), normalized_text)

    def test_goal_policy_uses_single_root_default(self) -> None:
        policy = read_repo_text("goal.policy.md")

        self.assert_contains_all(
            policy,
            (
                "## Single-Root Default",
                "optional coordination overlay",
                "implementation, integration, validation, state",
                "Subagents and external consults are bounded advisers by default",
                "execution-safety mechanism, not a permission gate",
                "Exactly one task is the current root",
                "If two tasks could plausibly claim root ownership",
                "Only the currently active root task exercises standing campaign authority",
                "Resource claims do not expire merely because time passes",
                "a successor root re-reads the repository baton",
                "Before a successor pushes or publishes",
                "exact remote branch, tag, release, artifact, and publication identity",
            ),
        )
        self.assertNotIn("Absence of any field means no authority", policy)

    def test_policy_records_standing_and_fresh_authority(self) -> None:
        policy = read_repo_text("goal.policy.md")
        standing = markdown_h2_section(policy, "Standing Campaign Authority")
        fresh = markdown_h2_section(policy, "Fresh Authorization Required")

        self.assert_contains_all(
            standing,
            (
                "copied-runtime launches",
                "controlled input",
                "read-process memory",
                "process-memory mutation",
                "copied executables",
                "live Ghidra",
                "commits and pushes",
                "tags, releases, publication",
                "project-scoped external actions",
                "normal cleanup",
                "standing-authorized actions for this campaign",
                "unused exact identity",
                "moving an existing tag",
                "overwriting/replacing an existing release artifact",
            ),
        )
        self.assert_contains_all(
            fresh,
            (
                "spending",
                "genuinely destructive or irreversible operations",
                "force-push or history rewriting",
            ),
        )
        for standing_family in (
            "copied-runtime",
            "live Ghidra",
            "commits and pushes",
            "tags, releases",
            "project-scoped external actions",
        ):
            with self.subTest(standing_family=standing_family):
                self.assertNotIn(standing_family.casefold(), fresh.casefold())
        self.assertNotIn("\n- spending", standing.casefold())
        self.assertNotIn("\n- genuinely destructive", standing.casefold())
        self.assert_contains_all(
            policy,
            (
                "installed Steam game and original `BEA.exe` remain immutable",
                "proprietary evidence remains local",
                "Host/Join remains disabled",
                "proves the target is the intended copy rather than the installed game or original executable",
                "Live Ghidra mutation hard-stops before the first write",
            ),
        )

    def test_external_authority_is_root_only_and_closed_to_project_surfaces(
        self,
    ) -> None:
        policy = read_repo_text("goal.policy.md")
        standing = markdown_h2_section(policy, "Standing Campaign Authority")

        self.assert_contains_all(
            policy,
            (
                "Only the currently active root task exercises standing campaign authority",
                "A root-created writer receives only its explicit bounded write scope",
            ),
        )
        self.assert_contains_all(
            standing,
            (
                "Standing project-scoped external actions are limited to the configured source repository and its established project surfaces",
                "non-force Git writes",
                "issue/PR/project metadata actions",
                "creation of unused tag/release/publication identities",
                "additive publication of the exact verified project artifact",
                "an already identified project channel/audience",
                "not an open alias for billing, spend, credential changes, account/provider administration, unrelated deployment, or a novel audience",
            ),
        )

    def test_normal_cleanup_requires_all_item_ownership_or_disposability(self) -> None:
        policy = read_repo_text("goal.policy.md")
        resources = read_repo_text("coordination/RESOURCE_LEASES.md")
        design = read_repo_text(
            "docs/superpowers/specs/2026-07-15-single-root-campaign-operating-foundation-design.md"
        )
        required_boundary = (
            "created and owned by the current action or separately verified as "
            "disposable"
        )

        for relative_path, text in (
            ("goal.policy.md", policy),
            ("coordination/RESOURCE_LEASES.md", resources),
            ("foundation design", design),
        ):
            with self.subTest(path=relative_path):
                self.assertIn(required_boundary, normalized_words(text).casefold())
        self.assert_contains_all(
            policy,
            (
                "immutable:",
                "retained/shared:",
                "action-owned disposable:",
                "never deletes an unknown, pre-existing, retained, shared, or immutable item",
                "action receipt/provenance identifier and exact allowed path class",
                "Crash debris without a valid action receipt/provenance record is retained",
            ),
        )
        self.assert_contains_all(
            resources,
            (
                "A claim has no automatic time-based expiry",
                "exact remote branch/tag/release/artifact read-back",
                "A successor does not inherit a prior action's disposable set",
            ),
        )

    def test_coordination_is_an_optional_concurrency_overlay(self) -> None:
        coordination = read_repo_text("coordination/README.md")
        workstreams = read_repo_text("coordination/WORKSTREAM_CONTRACT.md")
        resources = read_repo_text("coordination/RESOURCE_LEASES.md")
        reports = read_repo_text("coordination/REPORT_CONTRACT.md")
        contributing = read_repo_text("CONTRIBUTING.md")
        automation = read_repo_text(
            "coordination/AUTOMATION_STORAGE_GHIDRA_POSTURE.md"
        )

        self.assert_contains_all(
            coordination,
            (
                "optional concurrency overlay",
                "Single-root work does not require",
                "explicitly activates this overlay",
                "ignored/local activation record before a non-root writer edits",
            ),
        )
        self.assertIn("## Applicability", workstreams)
        self.assertIn("does not apply to ordinary single-root work", workstreams)
        self.assertIn("resource claim", resources)
        self.assertIn(
            "does not grant or withhold action authority",
            normalized_words(resources).casefold(),
        )
        self.assertIn(
            "does not require a worker report", normalized_words(reports).casefold()
        )
        normalized_automation = normalized_words(automation).casefold()
        self.assertIn("root-led slice at a time", normalized_automation)
        self.assertIn("standing campaign authority", normalized_automation)
        self.assert_contains_all(
            contributing,
            (
                "active root task normally owns source integration and canonical state",
                "optional coordination overlay",
                "only when root explicitly activates concurrent writers",
            ),
        )

    def test_current_root_alone_commits_and_accepts_across_overlay(self) -> None:
        workstreams = read_repo_text("coordination/WORKSTREAM_CONTRACT.md")
        reports = read_repo_text("coordination/REPORT_CONTRACT.md")
        automation = read_repo_text(
            "coordination/AUTOMATION_STORAGE_GHIDRA_POSTURE.md"
        )
        coordination = read_repo_text("coordination/README.md")
        contributing = read_repo_text("CONTRIBUTING.md")
        campaign = read_repo_text("goal.campaign.md")

        self.assert_contains_all(
            workstreams,
            (
                "a non-root writer does not commit under ambient campaign authority",
                "the current root alone owns final judgment, commits/pushes",
                "explicit root handoff",
            ),
        )
        self.assert_contains_all(
            reports,
            (
                "The current root reviews that proposal, writes the final integration/state commit",
                "The current root alone owns final acceptance",
            ),
        )
        self.assert_contains_all(
            automation,
            (
                "The current root remains the final acceptance and integration owner",
                "explicit baton succession",
            ),
        )
        self.assertIn(
            "the current root writes and accepts the final commit",
            normalized_words(coordination).casefold(),
        )
        self.assertIn(
            "the current root writes and accepts the final state",
            normalized_words(contributing).casefold(),
        )
        self.assertIn(
            "human or the current root accepts campaign pause/phase-complete",
            normalized_words(campaign).casefold(),
        )
        for stale_phrase in (
            "whether the worker may commit",
            "root or the named integration owner owns final judgment",
            "root or the designated integration owner owns final acceptance",
            "unless it explicitly delegates those roles",
        ):
            for relative_path, text in (
                ("workstreams", workstreams),
                ("reports", reports),
                ("automation", automation),
            ):
                with self.subTest(path=relative_path, phrase=stale_phrase):
                    self.assertNotIn(stale_phrase, text.casefold())

    def test_canonical_slash_goal_is_durable_and_unchanged(self) -> None:
        slash_goal = read_repo_text(
            "roadmap/goals/full-rebuild-campaign-slash-goal.md"
        )

        self.assertIn(
            normalized_words(CANONICAL_GOAL), normalized_words(slash_goal)
        )
        self.assertNotIn("STOP_LOCAL", slash_goal)
        self.assertNotIn("TIME-BOXED MARATHON", slash_goal)

    def test_campaign_baton_clears_only_the_obsolete_shield_authority_blocker(
        self,
    ) -> None:
        baton = read_repo_text("goal.md")
        campaign = read_repo_text("goal.campaign.md")

        self.assertIn("M2.3-target-acquisition-static-contract", baton)
        self.assertIn("Resolved skipped blocker", baton)
        self.assertIn("standing campaign authority", baton)
        self.assertIn("The shield measurement itself remains pending", baton)
        self.assertIn("No shield attempt", baton)
        self.assertIn("publish no behavior contract", baton)
        self.assertNotIn("MISSING_COMPLETE_LIVE_RUNTIME_LEASE", baton)
        self.assertNotIn("BLOCKED_SHIELD_LIVE_AUTHORITY", baton)
        self.assertNotIn("## Active skipped blocker", baton)
        self.assertIn("single-root default", campaign.casefold())
        normalized_campaign = normalized_words(campaign).casefold()
        self.assertIn(
            "live pair pending and covered by standing campaign authority",
            normalized_campaign,
        )
        self.assertIn(
            "campaign continues until accepted exit criteria, a human pause, or no meaningful authorized work remains",
            normalized_campaign,
        )
        self.assertNotIn(
            "until exit or a well-formed `blocked_*` record", normalized_campaign
        )
        self.assertNotIn(
            "shield be+0x100 neutral-control/input-free runner and symmetric correlation gate landed, live pair authority-blocked",
            normalized_campaign,
        )

    def test_landed_foundation_baton_has_no_pending_acceptance_placeholders(
        self,
    ) -> None:
        baton = read_repo_text("goal.md")
        campaign = read_repo_text("goal.campaign.md")
        normalized_baton = normalized_words(baton).casefold()

        self.assertIn("m0.6-single-root-operating-foundation", normalized_baton)
        self.assertIn("| m0.6 |", campaign.casefold())
        for placeholder in (
            "pending foundation implementation commit",
            "pending final foundation verification",
            "pending bounded normal/adversarial foundation review",
        ):
            with self.subTest(placeholder=placeholder):
                self.assertNotIn(placeholder, normalized_baton)

    def test_canonical_state_batons_reflect_single_root_authority(self) -> None:
        developer = json.loads(read_repo_text("developer_agent_state.json"))
        documentation = json.loads(read_repo_text("documentation_agent_state.json"))
        orchestrator = json.loads(read_repo_text("re_orchestrator_state.json"))

        self.assertIn("Single-root default", developer["routingPolicy"])
        self.assertTrue(developer["verifiedTruth"]["release"]["newReleaseAuthorized"])
        self.assertIn("single-root default", documentation["routingPolicy"].casefold())
        self.assertIn("standing-authorized", developer["currentFocus"])
        self.assertIn("standing-authorized", documentation["currentFocus"])
        for label, state in (
            ("developer", developer),
            ("documentation", documentation),
            ("orchestrator", orchestrator),
        ):
            with self.subTest(state=label):
                self.assertEqual("2026-07-15", state["lastUpdated"])
                self.assertIn("m2.3", state["currentFocus"].casefold())
        self.assertIn(
            "standing-authorized", orchestrator["currentTruth"][-1].casefold()
        )
        combined = normalized_words(
            json.dumps(
                (developer, documentation, orchestrator),
                ensure_ascii=False,
                sort_keys=True,
            )
        ).casefold()
        for stale_phrase in (
            "blocked_shield_live_authority",
            "missing_complete_live_runtime_lease",
            "shield live pair remains authority-blocked",
            "requires a separate structured baton",
            "no measured walker scalar-response contract exists",
            "exactly-two-attempt copied-runtime walker measurement",
            "no accepted live measurement exists",
            "the future measurement is scalar motion response",
            "fresh exactly-two-attempt run is authorized",
            "core translation blocked until measured contract",
            "no live measurement or behavior contract exists yet",
            "walker slice still lacks two accepted copied-runtime measurements",
        ):
            with self.subTest(stale_phrase=stale_phrase):
                self.assertNotIn(stale_phrase, combined)

        for label, state in (
            ("developer", developer),
            ("documentation", documentation),
            ("orchestrator", orchestrator),
        ):
            shield_steps = normalized_words(
                " ".join(
                    step for step in state["nextSteps"] if "shield" in step.casefold()
                )
            ).casefold()
            with self.subTest(state=label, pending_live_path="shield"):
                self.assertIn("shield", shield_steps)
                self.assertIn("exactly two", shield_steps)
                self.assertIn("if either attempt fails", shield_steps)
                self.assertIn("publish no behavior contract", shield_steps)

    def test_active_foundation_has_no_mandatory_structured_runtime_baton(self) -> None:
        active_paths = (
            "goal.policy.md",
            "coordination/README.md",
            "coordination/WORKSTREAM_CONTRACT.md",
            "coordination/RESOURCE_LEASES.md",
            "coordination/REPORT_CONTRACT.md",
            "coordination/AUTOMATION_STORAGE_GHIDRA_POSTURE.md",
            "CONTRIBUTING.md",
        )
        forbidden_phrases = (
            "Absence of any field means no authority",
            "Structured Authority Baton",
            "requires a structured baton authority",
            "require a structured baton authority",
        )

        for relative_path in active_paths:
            text = read_repo_text(relative_path)
            for phrase in forbidden_phrases:
                with self.subTest(path=relative_path, phrase=phrase):
                    self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
