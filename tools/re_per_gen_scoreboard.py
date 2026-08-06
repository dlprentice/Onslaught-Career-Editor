#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""File known Grok grades + rebuild per-gen SCOREBOARD from LANE/receipts."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "local-lab" / "per-gen-review-20260805-v1"

# Seed grades from completed Grok police (integration owner harvest)
GROK_SEED: dict[int, dict] = {
    9: {
        "grok-normal": "SURVIVES",
        "grok-adversarial": "SURVIVES",
        "notes": {
            "normal": "5 metadata promotions; contracts OPEN/C0; no REBUILD_READY",
            "adversarial": "hygiene PE re-hash gap; U2 elevation over-read; stale falsifiers",
        },
    },
    10: {
        "grok-normal": "SURVIVES",
        "grok-adversarial": "NEEDS_WORK",
        "notes": {
            "normal": "3 C2 TTD promotions; StartDie zero-control; dual authority base",
            "adversarial": "IDENTITY soft-close; unreproduced semantic-verification.json",
        },
    },
    11: {
        "grok-normal": "SURVIVES",
        "grok-adversarial": "NEEDS_WORK",
        "notes": {
            "normal": "4986 TERMINAL_PADDING xrefclean; 26 abs-hit open",
            "adversarial": "verify no PE rebind; defaults still 5012 pre-xrefclean",
        },
    },
    12: {
        "grok-normal": "SURVIVES",
        "grok-adversarial": "NEEDS_WORK",
        "notes": {
            "normal": "356 mixed-shape; pad 4986; dark 667; exec 108",
            "adversarial": "PE-less verify; envelope rubber-stamp; invented refuter SURVIVED",
        },
    },
    13: {
        "grok-normal": "SURVIVES",
        "grok-adversarial": "NEEDS_WORK",
        "notes": {
            "normal": "12 pad/data terminals; parent Gen12 unmutated",
            "adversarial": "PE-less gen verify; self-stamped SURVIVED; hard EXPECTED 12",
        },
    },
    14: {
        "grok-normal": "SURVIVES",
        "grok-adversarial": "SURVIVES",
        "notes": {
            "normal": "242 code envelopes TBA; multi 8 excluded",
            "adversarial": "hard claims hold; process PE-less verify noted non-killing",
        },
    },
    15: {
        "grok-normal": "SURVIVES",
        "grok-adversarial": "NEEDS_WORK",
        "notes": {
            "normal": "32 multi-subspan full-cover AMBIG",
            "adversarial": "soft MULTI kind; frac>=0.90 full cover; PE-less verify",
        },
    },
    16: {
        "grok-normal": "SURVIVES",
        "grok-adversarial": "REFUTED",
        "notes": {
            "normal": "46 code-like mass (16 pad+30 ambig)",
            "adversarial": (
                "OFFSET_ENVELOPE launders deeper STILL_OPEN/partial "
                "(0x005344fc, 0x0042d06a) vs pack non_claim partial tails stay OPEN"
            ),
        },
    },
    17: {
        "grok-normal": "SURVIVES",
        "grok-adversarial": "NEEDS_WORK",
        "notes": {
            "normal": "50 MSVC align-NOP NO_INBOUND pads; pad 5062",
            "adversarial": "gen verify count-only; no PE rebind on apply",
        },
    },
    18: {
        "grok-normal": "SURVIVES",
        "grok-adversarial": "NEEDS_WORK",
        "notes": {
            "normal": "37 table+align + prologue CALL; dark 255 exec 101",
            "adversarial": "gen verify soft compose; no pack join/PE",
        },
    },
    19: {
        "grok-normal": "SURVIVES",
        "grok-adversarial": "NEEDS_WORK",
        "notes": {
            "normal": "112 code envelopes (20 dark+92 exec); remain 235/9",
            "adversarial": "gen verify count-lock only; no pack row replay/PE",
        },
    },
    20: {
        "grok-normal": "SURVIVES",
        "grok-adversarial": "NEEDS_WORK",
        "notes": {
            "normal": "68 multi-unit TBA (64 dark+4 exec); remain 171/5",
            "adversarial": "ownership Q CLOSED_SURVIVED without ownership; soft verify",
        },
    },
    21: {
        "grok-normal": "SURVIVES",
        "grok-adversarial": "NEEDS_WORK",
        "notes": {
            "normal": "6 code+pad TBA (5 dark+1 soft multi exec)",
            "adversarial": "ownership Q overclose; PE-less gen verify; hard EXPECTED",
        },
    },
    22: {
        "grok-normal": "SURVIVES",
        "grok-adversarial": "SURVIVES",
        "notes": {
            "normal": "31 data-shape (4 DATA+27 ambig); dark 135 exec 4",
            "adversarial": "hard claims hold; soft campaign verify/SSE noted non-killing",
        },
    },
    23: {
        "grok-normal": "SURVIVES",
        "grok-adversarial": "SURVIVES",
        "notes": {
            "normal": "10 partial-data AMBIG; dark 125 exec 4",
            "adversarial": "content holds; gen verify PE gap hygiene only",
        },
    },
    24: {
        "grok-normal": "SURVIVES",
        "grok-adversarial": "NEEDS_WORK",
        "notes": {
            "normal": "47 small-table; pad5062+data29+ambig944+dark78+exec4=6117",
            "adversarial": "INDEX bulk-close 0x004f5ac5 (171B); hard EXPECTED; shallow gen verify",
        },
    },
}


def grade_cell(raw: str | None, status: str) -> str:
    if status == "DONE" and raw:
        u = raw.upper()
        if "NEEDS_WORK" in u:
            return "NEEDS_WORK"
        if "REFUTED" in u and "GRADE" in u:
            return "REFUTED"
        if "SURVIVES" in u:
            return "SURVIVES"
        return raw[:24]
    return (status or "PENDING")[:10]


def main() -> int:
    now = datetime.now(timezone.utc).isoformat()
    for g in range(9, 25):
        gdir = BASE / f"gen{g:02d}"
        lane_path = gdir / "LANE.json"
        if not lane_path.is_file():
            continue
        lane = json.loads(lane_path.read_text(encoding="utf-8"))
        revs = lane.setdefault("reviewers", {})

        if g in GROK_SEED:
            seed = GROK_SEED[g]
            for rid in ("grok-normal", "grok-adversarial"):
                revs.setdefault(rid, {})
                revs[rid]["status"] = "DONE"
                revs[rid]["grade"] = seed[rid]
                revs[rid]["provider"] = "grok"
                revs[rid]["finishedAtUtc"] = now
            lane["grok_notes"] = seed["notes"]
            for role in ("normal", "adversarial"):
                rid = f"grok-{role}"
                (gdir / f"{rid}-GRADE.md").write_text(
                    f"# Gen{g} {rid}\n\n**GRADE: {seed[rid]}**\n\n"
                    f"{seed['notes'][role]}\n\n"
                    f"(Full subagent text in session; filed {now})\n",
                    encoding="utf-8",
                )

        for rid in (
            "flash-normal",
            "flash-adversarial",
            "pro-normal",
            "pro-adversarial",
        ):
            rec_path = gdir / f"{rid}-receipt.json"
            if not rec_path.is_file():
                continue
            rec = json.loads(rec_path.read_text(encoding="utf-8"))
            revs.setdefault(rid, {})
            revs[rid]["status"] = "DONE" if rec.get("exitCode") == 0 else "FAIL"
            revs[rid]["grade"] = rec.get("gradeLine")
            revs[rid]["exitCode"] = rec.get("exitCode")
            revs[rid]["note"] = rec.get("note")
            revs[rid]["provider"] = rec.get("model")
            if rec.get("gradeLine"):
                (gdir / f"{rid}-GRADE.md").write_text(
                    f"# Gen{g} {rid}\n\n**{rec.get('gradeLine')}**\n\n"
                    f"exit={rec.get('exitCode')} note={rec.get('note')}\n"
                    f"See {rid}-stdout.txt\n",
                    encoding="utf-8",
                )

        lane_path.write_text(json.dumps(lane, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# SCOREBOARD (live)",
        "",
        f"Updated: {now}",
        "",
        "| Gen | grok-N | grok-A | flash-N | flash-A | pro-N | pro-A |",
        "|----:|:------:|:------:|:-------:|:-------:|:-----:|:-----:|",
    ]
    for g in range(9, 25):
        lane = json.loads((BASE / f"gen{g:02d}" / "LANE.json").read_text(encoding="utf-8"))
        revs = lane.get("reviewers") or {}

        def cell(rid: str) -> str:
            r = revs.get(rid) or {}
            return grade_cell(r.get("grade"), r.get("status", "PENDING"))

        lines.append(
            f"| {g} | {cell('grok-normal')} | {cell('grok-adversarial')} | "
            f"{cell('flash-normal')} | {cell('flash-adversarial')} | "
            f"{cell('pro-normal')} | {cell('pro-adversarial')} |"
        )

    lines.extend(
        [
            "",
            "## Theme from Gen9–24 Grok police (filed)",
            "",
            "- **Normal:** 16/16 SURVIVES (claim surfaces + partition math).",
            "- **Adversarial SURVIVES:** Gen 9, 14, 22, 23.",
            "- **Adversarial NEEDS_WORK:** Gen 10–13, 15, 17–21, 24.",
            "- **Adversarial REFUTED:** **Gen 16** (OFFSET_ENVELOPE launders deeper",
            "  STILL_OPEN/partial vs pack non-claim; e.g. 0x005344fc, 0x0042d06a).",
            "- Recurring process debt: generation verify PE-less / count-oracle;",
            "  hardcoded EXPECTED_*; self-stamped refuterVerdict=SURVIVED;",
            "  ownership Q closed without ownership (Gen20/21).",
            "- DeepSeek serial queue: flash/pro max still PENDING after Gen9 flash-N.",
            "- Gauntlet: adjudicate Gen16 REFUTED before trusting that ladder tip;",
            "  harden verify gates before Gen25 residual mass.",
            "",
        ]
    )
    (BASE / "SCOREBOARD.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print((BASE / "SCOREBOARD.md").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
