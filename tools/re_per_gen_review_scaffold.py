#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Scaffold Gen9–Gen24 per-generation 6-way review matrix.

Each generation is its own police lane (not a single mega-sweep).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "local-lab" / "per-gen-review-20260805-v1"

LANES: list[dict] = [
    {
        "gen": 9,
        "kind": "GHIDRA_TARGET_LOCK_SEMANTIC",
        "campaign": (
            "local-lab/ghidra-target-lock-semantic-generation9-20260804-v1/"
            "generation-9-live-semantic-promoted"
        ),
        "tools": [
            "tools/ghidra_target_lock_semantic_live_promotion.py",
            "tools/ghidra_target_lock_semantic_proof.py",
        ],
        "note": "Semantic promotion gen; dual authority precursor",
    },
    {
        "gen": 10,
        "kind": "TTD_CALL_CONTEXT",
        "campaign": (
            "local-lab/ttd-call-context-level521-impact-generation10-20260804-v1/"
            "generation-10-ttd-call-context-observation-v2"
        ),
        "tools": ["tools/Invoke-TtdCallContext.ps1"],
        "note": "Standing function/runtime TTD authority",
    },
    {
        "gen": 11,
        "kind": "RESIDUAL_TERMINAL_PADDING_BULK",
        "campaign": (
            "local-lab/residual-terminal-generation11-padding-xrefclean-20260805-v1/"
            "generation-11-residual-terminal-padding"
        ),
        "tools": [
            "tools/re_residual_terminal_generation.py",
            "tools/re_residual_terminal_formal_pack.py",
        ],
    },
    {
        "gen": 12,
        "kind": "RESIDUAL_TERMINAL_MIXED_SHAPE_BULK",
        "campaign": (
            "local-lab/residual-terminal-generation12-mixed-shape-20260805-v1/"
            "generation-12-residual-terminal-mixed-shape"
        ),
        "tools": [
            "tools/re_residual_mixed_shape_generation.py",
            "tools/re_residual_mixed_shape_formal_pack.py",
        ],
    },
    {
        "gen": 13,
        "kind": "RESIDUAL_TERMINAL_OPEN_DARK_PAD_DATA",
        "campaign": (
            "local-lab/residual-terminal-generation13-open-dark-pad-data-20260805-v1/"
            "generation-13-residual-terminal-open-dark-pad-data"
        ),
        "tools": [
            "tools/re_open_dark_pad_data_generation.py",
            "tools/re_open_dark_pad_data_formal_pack.py",
        ],
    },
    {
        "gen": 14,
        "kind": "RESIDUAL_TERMINAL_CODE_ENVELOPE_BOUNDED",
        "campaign": (
            "local-lab/residual-terminal-generation14-code-envelope-20260805-v1/"
            "generation-14-residual-terminal-code-envelope"
        ),
        "tools": ["tools/re_code_envelope_generation.py"],
    },
    {
        "gen": 15,
        "kind": "RESIDUAL_TERMINAL_OPEN_DARK_REMAINING",
        "campaign": (
            "local-lab/residual-terminal-generation15-open-dark-remaining-20260805-v1/"
            "generation-15-residual-terminal-open-dark-remaining"
        ),
        "tools": ["tools/re_open_dark_remaining_generation.py"],
    },
    {
        "gen": 16,
        "kind": "RESIDUAL_TERMINAL_OPEN_DARK_CODE_LIKE_MASS",
        "campaign": (
            "local-lab/residual-terminal-generation16-code-like-mass-20260805-v1/"
            "generation-16-residual-terminal-code-like-mass"
        ),
        "tools": [
            "tools/re_open_dark_code_like_mass_generation.py",
            "tools/re_open_dark_code_like_mass.py",
        ],
    },
    {
        "gen": 17,
        "kind": "RESIDUAL_TERMINAL_OPEN_DARK_STILL_OPEN_INBOUND",
        "campaign": (
            "local-lab/residual-terminal-generation17-still-open-inbound-20260805-v1/"
            "generation-17-residual-terminal-still-open-inbound"
        ),
        "tools": [
            "tools/re_open_dark_still_open_inbound_generation.py",
            "tools/re_open_dark_still_open_inbound.py",
        ],
    },
    {
        "gen": 18,
        "kind": "RESIDUAL_TERMINAL_OPEN_TABLE_ALIGN_EXECUTED",
        "campaign": (
            "local-lab/residual-terminal-generation18-table-align-executed-20260805-v1/"
            "generation-18-residual-terminal-table-align-executed"
        ),
        "tools": [
            "tools/re_open_residual_gen17_table_align_generation.py",
            "tools/re_open_residual_gen17_table_align.py",
        ],
    },
    {
        "gen": 19,
        "kind": "RESIDUAL_TERMINAL_OPEN_CODE_ENVELOPE",
        "campaign": (
            "local-lab/residual-terminal-generation19-code-envelope-20260805-v1/"
            "generation-19-residual-terminal-code-envelope"
        ),
        "tools": [
            "tools/re_open_residual_gen18_code_envelope_generation.py",
            "tools/re_open_residual_gen18_code_envelope.py",
        ],
    },
    {
        "gen": 20,
        "kind": "RESIDUAL_TERMINAL_OPEN_MULTI_UNIT",
        "campaign": (
            "local-lab/residual-terminal-generation20-multi-unit-20260805-v1/"
            "generation-20-residual-terminal-multi-unit"
        ),
        "tools": [
            "tools/re_open_residual_gen19_multi_unit_generation.py",
            "tools/re_open_residual_gen19_multi_unit.py",
        ],
    },
    {
        "gen": 21,
        "kind": "RESIDUAL_TERMINAL_OPEN_CODE_PAD",
        "campaign": (
            "local-lab/residual-terminal-generation21-code-pad-20260805-v1/"
            "generation-21-residual-terminal-code-pad"
        ),
        "tools": [
            "tools/re_open_residual_gen20_code_pad_generation.py",
            "tools/re_open_residual_gen20_code_pad.py",
        ],
    },
    {
        "gen": 22,
        "kind": "RESIDUAL_TERMINAL_OPEN_DATA_SHAPE",
        "campaign": (
            "local-lab/residual-terminal-generation22-data-shape-20260805-v1/"
            "generation-22-residual-terminal-data-shape"
        ),
        "tools": [
            "tools/re_open_residual_gen21_data_shape_generation.py",
            "tools/re_open_residual_gen21_data_shape.py",
        ],
    },
    {
        "gen": 23,
        "kind": "RESIDUAL_TERMINAL_OPEN_PARTIAL_DATA",
        "campaign": (
            "local-lab/residual-terminal-generation23-partial-data-20260805-v1/"
            "generation-23-residual-terminal-partial-data"
        ),
        "tools": [
            "tools/re_open_residual_gen22_partial_data_generation.py",
            "tools/re_open_residual_gen22_partial_data.py",
        ],
    },
    {
        "gen": 24,
        "kind": "RESIDUAL_TERMINAL_OPEN_SMALL_TABLE",
        "campaign": (
            "local-lab/residual-terminal-generation24-small-table-20260805-v1/"
            "generation-24-residual-terminal-small-table"
        ),
        "tools": [
            "tools/re_open_residual_gen23_small_table_generation.py",
            "tools/re_open_residual_gen23_small_table.py",
        ],
    },
]

ROLES = [
    ("grok-normal", "grok", "normal"),
    ("grok-adversarial", "grok", "adversarial"),
    ("flash-normal", "deepseek/deepseek-v4-flash", "normal"),
    ("flash-adversarial", "deepseek/deepseek-v4-flash", "adversarial"),
    ("pro-normal", "deepseek/deepseek-v4-pro", "normal"),
    ("pro-adversarial", "deepseek/deepseek-v4-pro", "adversarial"),
]

COUNT_KEYS = (
    "residualOpenDark",
    "residualOpenExecuted",
    "residualTerminalPadding",
    "residualTerminalData",
    "residualTerminalBoundedAmbiguity",
    "functions",
    "residuals",
)


def _normal_prompt(lane: dict) -> str:
    g = lane["gen"]
    tools_s = " ".join(lane["tools"])
    return (
        f"READ-ONLY per-generation NORMAL review (tools allowed; no writes; "
        f"no Ghidra mutation; no campaign apply). "
        f"Scope ONLY Gen{g} lane kind={lane['kind']}. "
        f"Campaign dir: {lane['campaign']}. "
        f"Read campaign.ready.json and generation-receipt.json if present; "
        f"parentCampaign links; counts. Tools: {tools_s}. "
        f"Review: (1) this gen claims only (2) instrument/script quality for "
        f"this gen (3) parent unmutated if applicable (4) non-claims "
        f"REBUILD_READY/names. Do not broaden to other gens except "
        f"parent/child continuity for THIS gen. Output markdown + final line "
        f"GRADE: SURVIVES|REFUTED|NEEDS_WORK."
    )


def _adv_prompt(lane: dict) -> str:
    g = lane["gen"]
    tools_s = " ".join(lane["tools"])
    return (
        f"READ-ONLY per-generation ADVERSARIAL review (tools allowed; no writes; "
        f"no Ghidra mutation; no apply). Scope ONLY Gen{g} lane kind="
        f"{lane['kind']}. Campaign: {lane['campaign']}. Tools: {tools_s}. "
        f"Attack THIS gen: parent mutation, soft compose launder, hardcoded "
        f"EXPECTED counts, missing PE re-verify, EXECUTED overclaim, "
        f"REBUILD_READY, wrong specimen 74154bfa, dual-authority bleed. "
        f"Read instrument source + generation reducer + tests if present. "
        f"For each attack REFUTED or ATTACK_SURVIVES with paths/hashes. "
        f"Do not police other gens except as parent/child of THIS gen. "
        f"Final line GRADE: SURVIVES|REFUTED|NEEDS_WORK."
    )


def main() -> int:
    BASE.mkdir(parents=True, exist_ok=True)
    status: dict = {
        "schema": "bea.re.per-gen-review-matrix.v1",
        "createdAtUtc": datetime.now(timezone.utc).isoformat(),
        "policy": {
            "per_generation": True,
            "reviewers_required": [r[0] for r in ROLES],
            "deepseek_variant": "max",
            "serial_opencode": True,
            "broad_sweep_optional_not_substitute": True,
        },
        "lanes": [],
    }

    for lane in LANES:
        g = lane["gen"]
        gdir = BASE / f"gen{g:02d}"
        gdir.mkdir(parents=True, exist_ok=True)
        camp = ROOT / lane["campaign"]
        ready = camp / "campaign.ready.json"
        ready_exists = ready.is_file()
        counts = None
        advance = None
        generation = None
        if ready_exists:
            r = json.loads(ready.read_text(encoding="utf-8"))
            counts = r.get("counts")
            advance = (r.get("advance") or {}).get("kind")
            generation = r.get("generation")

        tools_exist = {t: (ROOT / t).is_file() for t in lane["tools"]}
        (gdir / "PROMPT-NORMAL.txt").write_text(
            _normal_prompt(lane) + "\n", encoding="utf-8"
        )
        (gdir / "PROMPT-ADVERSARIAL.txt").write_text(
            _adv_prompt(lane) + "\n", encoding="utf-8"
        )
        meta = {
            **lane,
            "ready_exists": ready_exists,
            "ready_generation": generation,
            "ready_advance": advance,
            "counts_subset": (
                {k: (counts or {}).get(k) for k in COUNT_KEYS} if counts else None
            ),
            "tools_exist": tools_exist,
            "reviewers": {
                rid: {"status": "PENDING", "provider": prov, "role": role}
                for rid, prov, role in ROLES
            },
        }
        (gdir / "LANE.json").write_text(
            json.dumps(meta, indent=2) + "\n", encoding="utf-8"
        )
        status["lanes"].append(
            {
                "gen": g,
                "kind": lane["kind"],
                "dir": str(gdir.relative_to(ROOT)).replace("\\", "/"),
                "ready_exists": ready_exists,
                "reviewers_pending": [r[0] for r in ROLES],
            }
        )
        print(
            f"gen{g:02d} ready={ready_exists} "
            f"tools={all(tools_exist.values())} advance={advance}"
        )

    (BASE / "MATRIX.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8"
    )
    (BASE / "README.md").write_text(
        """# Per-generation review matrix (Gen9–Gen24)

Policy (maintainer 2026-08-05): **each generation is its own police lane**.

For **every** gen N in 9..24, require all six:

| id | provider | role |
|----|----------|------|
| grok-normal | Grok subagent | normal |
| grok-adversarial | Grok subagent | adversarial |
| flash-normal | deepseek/deepseek-v4-flash max | normal |
| flash-adversarial | deepseek/deepseek-v4-flash max | adversarial |
| pro-normal | deepseek/deepseek-v4-pro max | normal |
| pro-adversarial | deepseek/deepseek-v4-pro max | adversarial |

Optional broad sweep is **supplement**, not substitute.

DeepSeek OpenCode runs are **serial** (DB lock). Grok subagents batch parallel.

See `MATRIX.json` and each `genNN/LANE.json`.
""",
        encoding="utf-8",
    )
    print("BASE", BASE)
    print("lanes", len(status["lanes"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
