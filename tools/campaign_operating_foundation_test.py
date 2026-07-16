#!/usr/bin/env python3
"""Regression tests for the durable single-writer campaign foundation."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CANONICAL_GOAL = """
Continuously reconstruct and enhance Battle Engine Aquila through an
evidence-backed, product-coupled campaign. Operate one portfolio with three
shipping outcomes: the community WinUI Toolkit, a playable RE-informed
original-code reconstruction, and meaningful tools, patches, mods, and
multiplayer progress for copied retail installations. Treat static analysis,
pinned source, copied-runtime observation, lore, asset research,
documentation, and harnesses as inputs rather than ends. Every slice must
name its primary product outcome, user value, exact consumer, acceptance
evidence, and non-claims. Do not run consecutive research-only slices unless
a concrete dependency requires it; absent such a dependency, deliver a
user-observable capability within every two accepted slices. Translate
retail-derived behavior through bounded evidence contracts before consumer
implementation, then close the product increment rather than the proof
artifact. Keep the installed game and original BEA.exe immutable, proprietary
payloads local, Host/Join evidence-gated, and spending or genuinely
destructive operations separately authorized. Operate unattended with
conservative reversible assumptions, automated behavioral/visual verification,
prompt integration, and resume-ready state. If one slice blocks, record the
exact reason and continue another safe shipping outcome. Stop only at an
accepted phase boundary, a human pause, or when no meaningful authorized
product work remains; one advancement is progress, not campaign completion.
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

    def test_goal_policy_uses_single_writer_default(self) -> None:
        policy = read_repo_text("goal.policy.md")

        self.assert_contains_all(
            policy,
            (
                "## Single-Writer Default",
                "optional coordination overlay",
                "implementation, integration, validation, state",
                "sole sequential implementation worker",
                "supervises, steers, and reports",
                "supervising task does not edit, validate, commit, push, launch, mutate, publish",
                "execution-safety mechanism, not a permission gate",
                "Exactly one task is the active implementation owner",
                "If two tasks could plausibly claim implementation ownership",
                "Only the active implementation owner exercises standing campaign authority",
                "Resource claims do not expire merely because time passes",
                "a successor implementation owner re-reads the repository baton",
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

    def test_external_authority_is_owner_only_and_closed_to_project_surfaces(
        self,
    ) -> None:
        policy = read_repo_text("goal.policy.md")
        standing = markdown_h2_section(policy, "Standing Campaign Authority")

        self.assert_contains_all(
            policy,
            (
                "Only the active implementation owner exercises standing campaign authority",
                "A supervising task or bounded adviser does not share that authority",
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

    def test_supervised_worker_requires_a_verified_two_way_control_channel(self) -> None:
        policy = read_repo_text("goal.policy.md")
        coordination = read_repo_text("coordination/README.md")
        contributing = read_repo_text("CONTRIBUTING.md")
        combined = normalized_words(
            "\n".join((policy, coordination, contributing))
        ).casefold()

        for phrase in (
            "two normal top-level tasks",
            "list_threads",
            "read_thread",
            "send_message_to_thread",
            "harmless round-trip message",
            "directly spawned subordinate agent task",
            "remains a valid alternative",
            "older resumed or cli-origin tasks",
            "fresh desktop-created supervisor task",
            "codex exec resume <task-id>",
            "overlapping turns",
            "mailbox may carry a checkpoint handoff only",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(normalized_words(phrase).casefold(), combined)

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
                "Single-writer work does not require",
                "sole implementation worker is single-writer work",
                "explicitly activates this overlay",
                "ignored/local activation record before an additional writer edits",
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
                "active implementation owner normally owns source integration and canonical state",
                "optional coordination overlay",
                "only for concurrent writers",
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
            "the active implementation owner writes and accepts the final commit",
            normalized_words(coordination).casefold(),
        )
        self.assertIn(
            "the active implementation owner writes and accepts the final state",
            normalized_words(contributing).casefold(),
        )
        self.assertIn(
            "the active campaign owner or maintainer accepts the phase boundary",
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

    def test_paused_product_baton_closes_shield_and_queues_consumer(
        self,
    ) -> None:
        baton = read_repo_text("goal.md")
        campaign = read_repo_text("goal.campaign.md")

        self.assertIn("M2.3-target-acquisition-static-contract", baton)
        self.assertIn("Status: **PAUSED**", baton)
        self.assertIn("no implementation worker assigned", baton)
        self.assertIn("fresh Codex Desktop supervisor task", baton)
        self.assertIn("send_message_to_thread", baton)
        self.assertIn("019f5e71-2038-7bf2-aab8-e75f9747fa3a", baton)
        self.assertIn("019f67ff-3b76-75b2-915e-5aec4abedecb", baton)
        self.assertIn("openai/codex#25990", baton)
        self.assertIn("standing-authorized", baton)
        self.assertIn("The shield attempt cap is exhausted", baton)
        self.assertIn("zero active shield edges", baton)
        self.assertIn("not an accepted canonical pair", baton)
        self.assertIn(
            "no shield retail behavior contract",
            normalized_words(baton).casefold(),
        )
        self.assertIn(
            "not a completed playable-targeting milestone",
            normalized_words(baton),
        )
        self.assertNotIn("MISSING_COMPLETE_LIVE_RUNTIME_LEASE", baton)
        self.assertNotIn("BLOCKED_SHIELD_LIVE_AUTHORITY", baton)
        self.assertNotIn("## Active skipped blocker", baton)
        self.assertIn("single-writer", campaign.casefold())
        normalized_campaign = normalized_words(campaign).casefold()
        self.assertIn(
            "exactly two separately closed copied-runtime observations",
            normalized_campaign,
        )
        self.assertIn("no third runtime attempt is authorized", normalized_campaign)
        self.assertIn("winui reconstruction", normalized_campaign)
        self.assertIn(
            "one advancement is progress, not campaign completion",
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

        self.assertIn("m0.6-single-writer-operating-foundation", normalized_baton)
        self.assertIn("| p0.1 |", campaign.casefold())
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

        self.assertIn("Single-writer default", developer["routingPolicy"])
        self.assertTrue(developer["verifiedTruth"]["release"]["newReleaseAuthorized"])
        self.assertIn("single-writer default", documentation["routingPolicy"].casefold())
        self.assertIn("product-coupled", developer["currentFocus"].casefold())
        self.assertIn("paused", developer["currentFocus"].casefold())
        self.assertIn("product-coupled", documentation["currentFocus"].casefold())
        self.assertIn("paused", documentation["currentFocus"].casefold())
        for label, state in (
            ("developer", developer),
            ("documentation", documentation),
            ("orchestrator", orchestrator),
        ):
            with self.subTest(state=label):
                self.assertEqual("2026-07-15", state["lastUpdated"])
                self.assertIn("winui reconstruction", state["currentFocus"].casefold())
                self.assertIn("paused", state["currentFocus"].casefold())
                self.assertIn(
                    "no implementation worker", state["currentFocus"].casefold()
                )
        self.assertIn(
            "standing-authorized",
            " ".join(orchestrator["currentTruth"]).casefold(),
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
            blockers = normalized_words(" ".join(state["activeBlockers"])).casefold()
            next_steps = normalized_words(" ".join(state["nextSteps"])).casefold()
            with self.subTest(state=label, closed_live_path="shield"):
                self.assertIn("shield", blockers)
                self.assertIn("exactly two", blockers)
                self.assertIn("cap is exhausted", blockers)
                self.assertIn("zero active shield edges", blockers)
                self.assertIn("no accepted pair", blockers)
                self.assertIn("no shield behavior contract", blockers)
                self.assertNotIn("run exactly two", next_steps)

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
