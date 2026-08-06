#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Scaffold Gen26–Gen33 per-generation multi-agent review matrix.

Standing mandatory set (FRAGO 2026-08-05 six-way pin; incomplete is NOT
finished):
  - Grok 4.5 High normal + adversarial
  - DeepSeek flash-max normal + adversarial (OpenCode direct)
  - Claude Opus 5 medium normal + adversarial (headless claude -p)

pro-max and Opus max are RETIRED for standing RE; direct DeepSeek sessions use
native subagent N+A per the AGENTS.md carve-out (see AGENTS.md).

Self-authored GROK-ADVERSARIAL.json stubs are NOT a substitute for these lanes.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "local-lab" / "per-gen-review-gen26-33-20260805-v1"

LANES: list[dict] = [
    {
        "gen": 26,
        "kind": "RESIDUAL_TERMINAL_UNIT_SPLIT",
        "campaign": (
            "local-lab/residual-terminal-generation26-unit-split-20260805-v1/"
            "generation-26-residual-terminal-unit-split"
        ),
        "tools": [
            "tools/re_open_residual_gen26_unit_split_generation.py",
            "tools/re_open_residual_gen25_ttd_unit_split.py",
        ],
        "prior_stub": "local-lab/gen26-preapply-review-20260805-v1/GROK-ADVERSARIAL.json",
        "note": "Closed OPEN_EXECUTED via unit-split; police not re-closed",
    },
    {
        "gen": 27,
        "kind": "RESIDUAL_TERMINAL_TINY_FRAGMENT",
        "campaign": (
            "local-lab/residual-terminal-generation27-tiny-fragment-20260805-v1/"
            "generation-27-residual-terminal-tiny-fragment"
        ),
        "tools": [
            "tools/re_open_residual_gen27_tiny_fragment_generation.py",
            "tools/re_open_residual_gen26_tiny_fragment.py",
        ],
        "prior_stub": "local-lab/gen27-preapply-review-20260805-v1/GROK-ADVERSARIAL.json",
    },
    {
        "gen": 28,
        "kind": "RESIDUAL_TERMINAL_OPEN_DARK_UNIT_SPLIT",
        "campaign": (
            "local-lab/residual-terminal-generation28-open-dark-unit-split-20260805-v1/"
            "generation-28-residual-terminal-open-dark-unit-split"
        ),
        "tools": [
            "tools/re_open_residual_gen28_open_dark_unit_split_generation.py",
            "tools/re_open_residual_gen27_open_dark_unit_split.py",
        ],
        "prior_stub": "local-lab/gen28-preapply-review-20260805-v1/GROK-ADVERSARIAL.json",
    },
    {
        "gen": 29,
        "kind": "RESIDUAL_TERMINAL_PAD_PEEL_SANDWICH",
        "campaign": (
            "local-lab/residual-terminal-generation29-pad-peel-sandwich-20260805-v1/"
            "generation-29-residual-terminal-pad-peel-sandwich"
        ),
        "tools": [
            "tools/re_open_residual_gen29_pad_peel_sandwich_generation.py",
            "tools/re_open_residual_gen28_pad_peel_sandwich.py",
        ],
        "prior_stub": "local-lab/gen29-preapply-review-20260805-v1/GROK-ADVERSARIAL.json",
    },
    {
        "gen": 30,
        "kind": "RESIDUAL_TERMINAL_MSVC_TABLE_MIX",
        "campaign": (
            "local-lab/residual-terminal-generation30-msvc-table-mix-20260805-v1/"
            "generation-30-residual-terminal-msvc-table-mix"
        ),
        "tools": [
            "tools/re_open_residual_gen30_msvc_table_mix_generation.py",
            "tools/re_open_residual_gen29_msvc_table_mix.py",
        ],
        "prior_stub": "local-lab/gen30-preapply-review-20260805-v1/GROK-ADVERSARIAL.json",
    },
    {
        "gen": 31,
        "kind": "RESIDUAL_TERMINAL_SEH_SEGMENT_RESOLVE",
        "campaign": (
            "local-lab/residual-terminal-generation31-seh-segment-resolve-20260805-v1/"
            "generation-31-residual-terminal-seh-segment-resolve"
        ),
        "tools": [
            "tools/re_open_residual_gen31_seh_segment_resolve_generation.py",
            "tools/re_open_residual_gen30_seh_segment_resolve.py",
        ],
        "prior_stub": "local-lab/gen31-preapply-review-20260805-v1/GROK-ADVERSARIAL.json",
    },
    {
        "gen": 32,
        "kind": "RESIDUAL_TERMINAL_DEEP_SEGMENT_RESOLVE",
        "campaign": (
            "local-lab/residual-terminal-generation32-deep-segment-resolve-20260805-v1/"
            "generation-32-residual-terminal-deep-segment-resolve"
        ),
        "tools": [
            "tools/re_open_residual_gen32_deep_segment_resolve_generation.py",
            "tools/re_open_residual_gen31_deep_segment_resolve.py",
        ],
        "prior_stub": "local-lab/gen32-preapply-review-20260805-v1/GROK-ADVERSARIAL.json",
    },
    {
        "gen": 33,
        "kind": "RESIDUAL_TERMINAL_LARGE_ISLAND_RESOLVE",
        "campaign": (
            "local-lab/residual-terminal-generation33-large-island-resolve-20260805-v1/"
            "generation-33-residual-terminal-large-island-resolve"
        ),
        "tools": [
            "tools/re_open_residual_gen33_large_island_resolve_generation.py",
            "tools/re_open_residual_gen32_large_island_resolve.py",
        ],
        "prior_stub": "local-lab/gen33-preapply-review-20260805-v1/GROK-ADVERSARIAL.json",
        "note": "Tip; remaining OPEN_DARK are police OFFSET_ENVELOPE only",
    },
]

REQUIRED_LANES = [
    "grok-normal",
    "grok-adversarial",
    "flash-normal",
    "flash-adversarial",
    "opus5-medium-normal",
    "opus5-medium-adversarial",
]


def prompt_normal(lane: dict) -> str:
    tools = " ".join(lane["tools"])
    return (
        "READ-ONLY per-generation NORMAL review (tools allowed; no writes; no "
        "Ghidra mutation; no campaign apply). Scope ONLY Gen{gen} lane "
        "kind={kind}. Campaign dir: {campaign}. Read campaign.ready.json and "
        "generation-receipt.json if present; parentCampaign links; counts. "
        "Tools/instruments: {tools}. Prior thin pre-apply stub (NOT authority): "
        "{stub}. Review: (1) this gen claims only (2) instrument/script quality "
        "for this gen compose/verify/tests (3) parent unmutated if applicable "
        "(4) police OFFSET_ENVELOPE not re-closed (5) non-claims: no REBUILD_READY "
        "or invented names. Do not broaden to other gens except parent/child "
        "continuity for THIS gen. Output markdown + final line "
        "GRADE: SURVIVES|REFUTED|NEEDS_WORK."
    ).format(
        gen=lane["gen"],
        kind=lane["kind"],
        campaign=lane["campaign"],
        tools=tools,
        stub=lane.get("prior_stub") or "NONE",
    )


def prompt_adversarial(lane: dict) -> str:
    tools = " ".join(lane["tools"])
    return (
        "READ-ONLY per-generation ADVERSARIAL review (tools allowed; no writes; "
        "no Ghidra mutation; no campaign apply). Scope ONLY Gen{gen} kind={kind}. "
        "Campaign: {campaign}. Instruments: {tools}. Attack this generation: "
        "A_parent_mutation, B_police_envelope_reclose, C_rebuild_ready_launder, "
        "D_false_terminal_shape, E_pack_row_join_miss, F_self_grade_stub_as_review "
        "(prior stub {stub} is NOT external review), G_script_gate_bypass, "
        "H_specimen_sha_drift. Require real artifact inspection (ready json, "
        "residuals sha, formal pack if any, PE peBytes when claimed). "
        "Output attack table + final line GRADE: SURVIVES|REFUTED|NEEDS_WORK."
    ).format(
        gen=lane["gen"],
        kind=lane["kind"],
        campaign=lane["campaign"],
        tools=tools,
        stub=lane.get("prior_stub") or "NONE",
    )


def main() -> int:
    BASE.mkdir(parents=True, exist_ok=True)
    when = datetime.now(timezone.utc).isoformat()
    index = {
        "schema": "bea.re.per-gen-review-gen26-33.v1",
        "whenUtc": when,
        "status": "SCAFFOLDED_INCOMPLETE",
        "requiredLanesPerGen": REQUIRED_LANES,
        "n_gens": len(LANES),
        "n_cells": len(LANES) * len(REQUIRED_LANES),
        "note": (
            "Gen26-33 applied with thin/self GROK-ADVERSARIAL stubs only. "
            "This matrix backfills mandatory multi-agent police. "
            "Incomplete dual-role is not finished review. "
            "Six-way per FRAGO 2026-08-05; pro-max and Opus max retired."
        ),
        "lanes": LANES,
    }
    (BASE / "INDEX.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    (BASE / "GAUNTLET.md").write_text(
        """# Gauntlet — Gen26–33 residual tip backfill

Standing bar from AGENTS.md + complete-RE goal.

## Mandatory critics (every gen)

| Lane | How |
|------|-----|
| Grok normal + adversarial | Grok 4.5 High subagents |
| DeepSeek flash-max N+A | OpenCode direct `deepseek/deepseek-v4-flash` variant max |
| Claude Opus 5 medium N+A | `claude -p --model claude-opus-5 --effort medium` |

**6 cells/gen × 8 gens = 48 cells.** Builder never grades itself.
Self-authored `genNN-preapply-review-*/GROK-ADVERSARIAL.json` is evidence of
integration-owner hygiene only — not a finished police wave.

## Hard bar

1. Specimen `74154bfa…`
2. Honest terminal / OPEN+falsifier
3. No police OFFSET_ENVELOPE re-close without new instrument evidence
4. No REBUILD_READY / invented names
5. Parent generation residuals unmutated
6. Script/instrument gates reviewed, not only campaign JSON

## Stop

Do not mark Gen26–33 REVIEW_COMPLETE until SCOREBOARD shows all 48 cells
with real receipts (exit 0 + grade line). No fixed round count on gaps.
""",
        encoding="utf-8",
    )
    score_rows = [
        "# SCOREBOARD Gen26–33 (live)",
        "",
        f"Scaffolded: {when}",
        "",
        "Status: **INCOMPLETE** until all cells have real external receipts.",
        "",
        "| Gen | grok-N | grok-A | flash-N | flash-A | opus-med-N | opus-med-A |",
        "|----:|:------:|:------:|:-------:|:-------:|:----------:|:----------:|",
    ]
    for lane in LANES:
        g = lane["gen"]
        gdir = BASE / f"gen{g:02d}"
        gdir.mkdir(parents=True, exist_ok=True)
        (gdir / "PROMPT-NORMAL.txt").write_text(prompt_normal(lane) + "\n", encoding="utf-8")
        (gdir / "PROMPT-ADVERSARIAL.txt").write_text(
            prompt_adversarial(lane) + "\n", encoding="utf-8"
        )
        meta = {
            "gen": g,
            "kind": lane["kind"],
            "campaign": lane["campaign"],
            "tools": lane["tools"],
            "prior_stub": lane.get("prior_stub"),
            "requiredLanes": REQUIRED_LANES,
            "status": "PENDING_EXTERNAL_REVIEW",
        }
        (gdir / "LANE.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
        score_rows.append(
            f"| {g} | - | - | - | - | - | - |"
        )
    (BASE / "SCOREBOARD.md").write_text("\n".join(score_rows) + "\n", encoding="utf-8")
    print(json.dumps({"status": "SCAFFOLDED", "base": str(BASE), "cells": index["n_cells"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
