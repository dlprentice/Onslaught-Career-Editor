#!/usr/bin/env python3
"""Validate bounded operand-token triage for weapon-fired stealth reset.

This probe consumes an ignored Ghidra instruction export created by
ExportInstructionsByOperandToken.java. It deliberately does not promote the
source anchor to a retail candidate; it records that a field-focused scan found
stealth-adjacent object-offset references but no weapon/fire/projectile function
hit for those offsets.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TSV = (
    ROOT
    / "subagents"
    / "battleengine-weapon-fired-stealth-candidate"
    / "current"
    / "operand-search"
    / "stealth-field-instructions.tsv"
)
DEFAULT_OUT = (
    ROOT
    / "subagents"
    / "battleengine-weapon-fired-stealth-candidate"
    / "current"
    / "operand-search"
    / "weapon-stealth-operand-search.json"
)

SOURCE = ROOT / "references" / "Onslaught" / "BattleEngine.cpp"
SOURCE_TOKENS = (
    "BOOL CBattleEngine::WeaponFired(",
    "if (mJetPart->WeaponFired(inWeapon))",
    "if (mWalkerPart->WeaponFired(inWeapon))",
    "mStealth=0.0f;",
)

EXPECTED_TOKENS = ("0x4ac", "0x5d4", "0x5d8", "0x5dc")
EXPECTED_RELEVANT_FUNCTIONS = {
    "CBattleEngine__Init",
    "CMonitor__Process",
    "CGeneralVolume__Update4ACLatchFromHeightAndA0",
}
WEAPON_LIKE_RE = re.compile(r"(Weapon|Projectile|Fire)", re.IGNORECASE)
OBJECT_OFFSET_RE = re.compile(r"\+ 0x(4ac|5d4|5d8|5dc)\]")


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def source_hits() -> dict[str, list[int]]:
    lines = read_text(SOURCE).splitlines()
    return {
        token: [index + 1 for index, line in enumerate(lines) if token in line]
        for token in SOURCE_TOKENS
    }


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def build_report(tsv_path: Path) -> dict[str, object]:
    failures: list[str] = []
    source_token_hits = source_hits()
    missing_source = [token for token, hits in source_token_hits.items() if not hits]
    failures.extend(f"missing source token: {token}" for token in missing_source)

    rows: list[dict[str, str]] = []
    if not tsv_path.is_file():
        failures.append(f"missing operand export: {relative(tsv_path)}")
    else:
        rows = read_rows(tsv_path)

    token_counts = Counter(row.get("token", "") for row in rows)
    missing_tokens = [token for token in EXPECTED_TOKENS if token_counts[token] == 0]
    failures.extend(f"missing operand token rows: {token}" for token in missing_tokens)

    object_offset_rows = [
        row
        for row in rows
        if OBJECT_OFFSET_RE.search(row.get("operands", ""))
    ]
    weapon_like_offset_rows = [
        row
        for row in object_offset_rows
        if WEAPON_LIKE_RE.search(row.get("function_name", ""))
    ]
    if weapon_like_offset_rows:
        failures.append("weapon/fire/projectile object-offset rows exist; update public evidence before keeping this negative triage claim")

    functions_with_object_offsets = sorted(
        {
            row.get("function_name", "")
            for row in object_offset_rows
            if row.get("function_name", "") and row.get("function_name", "") != "<no_function>"
        }
    )
    missing_relevant_functions = sorted(EXPECTED_RELEVANT_FUNCTIONS - set(functions_with_object_offsets))
    failures.extend(
        f"missing expected relevant object-offset function: {name}"
        for name in missing_relevant_functions
    )

    grouped_counts = Counter(
        (
            row.get("token", ""),
            row.get("function_entry", ""),
            row.get("function_name", ""),
        )
        for row in object_offset_rows
    )
    top_groups = [
        {
            "token": token,
            "functionEntry": entry,
            "functionName": name,
            "count": count,
        }
        for (token, entry, name), count in grouped_counts.most_common(30)
    ]

    return {
        "schema": "battleengine-weapon-stealth-operand-search.v1",
        "status": "pass" if not failures else "blocked",
        "operandExport": relative(tsv_path),
        "sourceTokenLineHits": source_token_hits,
        "rowsTotal": len(rows),
        "objectOffsetRows": len(object_offset_rows),
        "tokenCounts": dict(sorted(token_counts.items())),
        "topObjectOffsetGroups": top_groups,
        "weaponLikeObjectOffsetRows": [
            {
                "token": row.get("token", ""),
                "instructionAddress": row.get("instruction_addr", ""),
                "functionEntry": row.get("function_entry", ""),
                "functionName": row.get("function_name", ""),
                "mnemonic": row.get("mnemonic", ""),
                "operands": row.get("operands", ""),
            }
            for row in weapon_like_offset_rows
        ],
        "failures": failures,
        "whatIsProven": [
            "The source WeaponFired anchor still clears stealth for both jet and walker fired-weapon paths.",
            "The current ignored Ghidra operand-token export contains stealth-adjacent object-offset references.",
            "The expected relevant object-offset references are currently in init/process/latch context, not weapon/fire/projectile functions.",
            "The current object-offset scan found zero weapon/fire/projectile function rows for the stealth-adjacent offsets.",
        ],
        "notProven": [
            "Absence of a retail weapon-fired stealth reset implementation.",
            "Exact Steam retail function body for weapon-fired stealth reset.",
            "Whether Steam retail removed, inlined, reorganized, or changed this source behavior.",
            "Runtime stealth behavior after firing a weapon.",
            "Ghidra rename-map mutation or read-back.",
            "Rebuildable open-source gameplay implementation.",
        ],
        "privacy": "Report stores repo-relative filenames, public token names, function names, public addresses, instruction operands, and counts from an ignored Ghidra export; no binaries, private paths, source excerpts, runtime captures, screenshots, or mutation logs.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check bounded weapon-fired stealth operand-token triage.")
    parser.add_argument("--check", action="store_true", help="run the operand search probe")
    parser.add_argument("--json", action="store_true", help="print the full JSON report")
    parser.add_argument("--tsv", type=Path, default=DEFAULT_TSV, help="ignored Ghidra operand-token TSV")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="ignored JSON report path")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    tsv = args.tsv if args.tsv.is_absolute() else ROOT / args.tsv
    out = args.out if args.out.is_absolute() else ROOT / args.out
    try:
        out.resolve().relative_to((ROOT / "subagents").resolve())
    except ValueError:
        print(f"Refusing to write report outside subagents/: {out}")
        return 1

    report = build_report(tsv)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("BattleEngine weapon-fired stealth operand search")
        print(f"Status: {report['status']}")
        print(f"Rows total: {report['rowsTotal']}")
        print(f"Object-offset rows: {report['objectOffsetRows']}")
        print(f"Weapon-like object-offset rows: {len(report['weaponLikeObjectOffsetRows'])}")

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
