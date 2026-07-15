#!/usr/bin/env python3
"""Regression tests for the product-coupled reconstruction campaign strategy."""

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

CURRENT_ONSLAUGHT_PIN = "5352a81cdb838b145a57f7febc5d9fc4b0129ebb"
CURRENT_AYA_PIN = "53b10b083b59cfd7e72849c15bec8b608eaf8a23"
STALE_ONSLAUGHT_PIN = "792545b996365f383781c666d145ea6cbda83f3a"
STALE_AYA_PIN = "6f3df296201ecc62bc09c39f7a93d8a4fb2f1638"


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def normalize(value: str) -> str:
    return " ".join(value.split())


def fenced_goal(value: str) -> str:
    marker = "## Verbatim `/goal` Objective"
    start = value.index(marker)
    fence_start = value.index("```text", start) + len("```text")
    fence_end = value.index("```", fence_start)
    return value[fence_start:fence_end].strip()


class ProductCoupledCampaignStrategyTests(unittest.TestCase):
    def test_canonical_goal_matches_approved_product_coupled_text(self) -> None:
        slash_goal = read_text(
            "roadmap/goals/full-rebuild-campaign-slash-goal.md"
        )
        self.assertEqual(normalize(CANONICAL_GOAL), normalize(fenced_goal(slash_goal)))
        self.assertIn("product-coupled", slash_goal)
        self.assertIn("three shipping outcomes", slash_goal)
        self.assertNotIn(
            "Continuously reverse engineer and reconstruct Battle Engine Aquila",
            slash_goal,
        )

    def test_policy_owns_three_outcomes_and_consumer_debt(self) -> None:
        policy = read_text("goal.policy.md")
        required = (
            "WinUI Community",
            "Playable Reconstruction",
            "Retail Enhancement",
            "supporting inputs",
            "primary outcome",
            "user outcome",
            "evidence question",
            "exact consumer",
            "acceptance",
            "non-claims",
            "next link",
            "No second consecutive research-only slice",
            "every two accepted slices",
            "user-observable result",
            "A behavior contract does not by itself land a product milestone",
            "Original-game multiplayer",
            "community release",
            "evidence-debt, contract-only, checker-only, documentation-only",
            "operator-only proof UI",
            "every tier of the consumer-first picker",
            "reopen condition",
            "GPL reconstruction code/artifacts retain their GPL obligations",
            "no proprietary retail bytes enter the GPL source tree",
            "does not manufacture authority merely by being read",
            "materially improve the named user task",
            "Navigation-only shells, no-op commands, inert scaffolds",
        )
        normalized_policy = normalize(policy).casefold()
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(normalize(phrase).casefold(), normalized_policy)

        for preserved_boundary in (
            "Single-Writer Default",
            "Standing Campaign Authority",
            "Fresh Authorization Required",
            "installed Steam game and original `BEA.exe` remain immutable",
            "Host/Join remains disabled",
            "Live Ghidra mutation hard-stops",
        ):
            with self.subTest(boundary=preserved_boundary):
                self.assertIn(preserved_boundary, policy)

    def test_campaign_prioritizes_consumers_not_research_counts(self) -> None:
        campaign = read_text("goal.campaign.md")
        for heading in (
            "P0 — Product integration foundation",
            "P1 — Playable reconstruction verticals",
            "P2 — Community WinUI integration and releases",
            "P3 — Retail enhancements and mods",
            "P4 — Original-game multiplayer epic",
            "P5 — Retail asset and mission import",
            "P6 — Community knowledge supporting outcomes",
        ):
            with self.subTest(heading=heading):
                self.assertIn(heading, campaign)

        self.assertIn("Consumer-first next-slice picker", campaign)
        self.assertIn("actionable evidence debt", campaign)
        self.assertIn("user-observable result", campaign)
        self.assertIn("behavior contract does not land", campaign.casefold())
        self.assertIn("no third runtime attempt is authorized", campaign.casefold())
        self.assertIn("operator-only proof UI", campaign)
        self.assertIn("Closed measurement ledger", campaign)
        self.assertNotIn("| **RE** |", campaign)

    def test_active_baton_preserves_m23_and_names_consumers(self) -> None:
        baton = read_text("goal.md")
        required = (
            "Status: **ACTIVE**",
            "sole sequential implementation worker",
            "M2.3-target-acquisition-static-contract",
            "Primary outcome: **Playable Reconstruction**",
            "OnslaughtRebuild.Core",
            "dangerous-misinterpretation exception",
            "shield",
            "Core and Godot",
            "WinUI Reconstruction",
            "No P1/P2 runtime retest occurred",
        )
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.casefold(), baton.casefold())
        self.assertNotIn("Status: **PAUSED**", baton)

    def test_public_front_doors_connect_all_three_products(self) -> None:
        readme = read_text("README.MD")
        capabilities = read_text("CURRENT_CAPABILITIES.md")
        rebuild = read_text("rebuild/README.md")

        self.assertIn("community front door", readme.casefold())
        self.assertIn("playable reconstruction", readme.casefold())
        self.assertIn("retail enhancements", readme.casefold())
        self.assertIn("three shipping outcomes", capabilities.casefold())
        self.assertIn("community winui toolkit", capabilities.casefold())
        self.assertIn("original-game multiplayer", capabilities.casefold())
        self.assertIn("shared product strategy", rebuild.casefold())
        self.assertIn("future winui", rebuild.casefold())
        self.assertIn("user-owned retail assets", rebuild.casefold())

    def test_state_batons_use_current_pins_and_product_focus(self) -> None:
        states = {
            name: json.loads(read_text(name))
            for name in (
                "developer_agent_state.json",
                "documentation_agent_state.json",
                "re_orchestrator_state.json",
            )
        }
        combined = normalize(json.dumps(states, sort_keys=True)).casefold()
        for name, state in states.items():
            with self.subTest(state=name):
                self.assertIn("product-coupled", state["currentFocus"].casefold())
                self.assertIn("active", state["currentFocus"].casefold())
                next_steps = normalize(" ".join(state["nextSteps"])).casefold()
                self.assertIn("m2.3", next_steps)
                self.assertIn("shield", next_steps)
                self.assertIn("winui reconstruction", next_steps)

        self.assertIn(CURRENT_ONSLAUGHT_PIN, combined)
        self.assertIn(CURRENT_AYA_PIN, combined)
        self.assertNotIn(STALE_ONSLAUGHT_PIN, combined)
        self.assertNotIn(STALE_AYA_PIN, combined)

    def test_strategy_keeps_reconstruction_label_and_local_asset_boundary(self) -> None:
        policy = read_text("goal.policy.md")
        design = read_text(
            "docs/superpowers/specs/2026-07-15-product-coupled-reconstruction-campaign-design.md"
        )
        rebuild = read_text("rebuild/README.md")
        combined = "\n".join((policy, design, rebuild)).casefold()

        self.assertIn(
            "evidence-backed, re-informed original-code reconstruction", combined
        )
        self.assertIn("not a strict clean-room implementation", combined)
        self.assertIn("user-owned retail assets", combined)
        self.assertIn("proprietary", combined)
        self.assertIn("status: accepted and implemented", design.casefold())


if __name__ == "__main__":
    unittest.main(verbosity=2)
