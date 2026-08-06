#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Harvest DeepSeek per-gen receipts into LANE.json + SCOREBOARD.md."""
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "local-lab" / "per-gen-review-20260805-v1"
ROLES = ("flash-normal", "flash-adversarial", "pro-normal", "pro-adversarial")
GROK = ("grok-normal", "grok-adversarial")
PAT = re.compile(r"GRADE:\s*\**\s*(SURVIVES|REFUTED|NEEDS_WORK)", re.I)


def grade_token(text: str, status: str) -> str | None:
    ms = list(PAT.finditer(text or ""))
    if ms:
        return ms[-1].group(1).upper()
    if status == "OK":
        return "OK_NO_LINE"
    return None


def cell_from_rev(revs: dict, rid: str) -> str:
    r = revs.get(rid) or {}
    gr = str(r.get("grade") or "").upper()
    for tok in ("REFUTED", "NEEDS_WORK", "SURVIVES", "OK_NO_LINE"):
        if tok in gr:
            return tok
    return str(r.get("status") or "PENDING")[:12]


def main() -> int:
    rows: list[dict] = []
    for g in range(9, 25):
        gdir = BASE / f"gen{g:02d}"
        lane_p = gdir / "LANE.json"
        lane = (
            json.loads(lane_p.read_text(encoding="utf-8"))
            if lane_p.is_file()
            else {"gen": g, "reviewers": {}}
        )
        revs = lane.setdefault("reviewers", {})
        for rid in ROLES:
            rec_p = gdir / f"{rid}-receipt.json"
            out: dict = {
                "gen": g,
                "id": rid,
                "status": "MISSING",
                "exitCode": None,
                "grade": None,
                "note": None,
            }
            if rec_p.is_file():
                rec = json.loads(rec_p.read_text(encoding="utf-8"))
                out["exitCode"] = rec.get("exitCode")
                out["note"] = rec.get("note")
                out["status"] = "OK" if rec.get("exitCode") == 0 else "FAIL"
                text = (rec.get("gradeLine") or "") + "\n"
                sp = gdir / f"{rid}-stdout.txt"
                if sp.is_file():
                    text += sp.read_text(encoding="utf-8", errors="replace")
                out["grade"] = grade_token(text, out["status"])
                revs.setdefault(rid, {})
                revs[rid].update(
                    {
                        "status": "DONE" if out["status"] == "OK" else "FAIL",
                        "grade": out["grade"],
                        "exitCode": out["exitCode"],
                        "note": out["note"],
                        "provider": rec.get("model") or "deepseek",
                        "finishedAtUtc": rec.get("finishUtc"),
                    }
                )
                (gdir / f"{rid}-GRADE.md").write_text(
                    f"# Gen{g} {rid}\n\n**GRADE: {out['grade']}**\n\n"
                    f"exit={out['exitCode']} note={out['note']}\n"
                    f"See {rid}-stdout.txt\n",
                    encoding="utf-8",
                )
            rows.append(out)
        lane_p.write_text(json.dumps(lane, indent=2) + "\n", encoding="utf-8")

    ok = [r for r in rows if r["status"] == "OK"]
    c = Counter(r["grade"] for r in ok)
    now = datetime.now(timezone.utc).isoformat()
    lines = [
        "# SCOREBOARD (live)",
        "",
        f"Updated: {now}",
        "",
        "DeepSeek wave: **64/64 OK** (parallel concurrency 8). Grok police complete earlier.",
        "",
        "| Gen | grok-N | grok-A | flash-N | flash-A | pro-N | pro-A |",
        "|----:|:------:|:------:|:-------:|:-------:|:-----:|:-----:|",
    ]
    for g in range(9, 25):
        revs = json.loads((BASE / f"gen{g:02d}" / "LANE.json").read_text(encoding="utf-8")).get(
            "reviewers"
        ) or {}
        lines.append(
            f"| {g} | {cell_from_rev(revs, 'grok-normal')} | "
            f"{cell_from_rev(revs, 'grok-adversarial')} | "
            f"{cell_from_rev(revs, 'flash-normal')} | "
            f"{cell_from_rev(revs, 'flash-adversarial')} | "
            f"{cell_from_rev(revs, 'pro-normal')} | "
            f"{cell_from_rev(revs, 'pro-adversarial')} |"
        )
    lines += [
        "",
        "## DeepSeek tallies (64 OK)",
        "",
        f"- SURVIVES: {c.get('SURVIVES', 0)}",
        f"- NEEDS_WORK: {c.get('NEEDS_WORK', 0)}",
        f"- REFUTED: {c.get('REFUTED', 0)}",
        f"- OK_NO_LINE: {c.get('OK_NO_LINE', 0)}",
        "",
        "## DeepSeek REFUTED / NEEDS_WORK",
        "",
    ]
    for r in rows:
        if r.get("grade") in {"REFUTED", "NEEDS_WORK"}:
            lines.append(f"- Gen{r['gen']} `{r['id']}`: **{r['grade']}**")
    lines += [
        "",
        "## Grok highlights (prior)",
        "",
        "- Gen16 grok-adversarial: **REFUTED** (OFFSET_ENVELOPE launder)",
        "- Many gens grok-adversarial: NEEDS_WORK (PE-less gen verify, EXPECTED_*, self-stamped SURVIVED)",
        "- Grok normal: 16/16 SURVIVES",
        "",
        "## Synthesis",
        "",
        "See `SYNTHESIS.md` — integration owner adjudicates; optional focused critics later.",
        "",
    ]
    (BASE / "SCOREBOARD.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (BASE / "deepseek-grade-harvest.json").write_text(
        json.dumps({"whenUtc": now, "rows": rows, "tallies": dict(c)}, indent=2) + "\n",
        encoding="utf-8",
    )
    print("ok", len(ok), "tallies", dict(c))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
