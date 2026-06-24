#!/usr/bin/env python3
"""Verify the BattleEngine weapon/burst saved Ghidra comment pass.

The comment pass records the current evidence boundaries directly in Ghidra for
the recovered weapon event handler, adjacent destructor, inner projectile-burst
body, and shared preset fallback dispatcher. It intentionally does not rename
`0x005069f0` or `0x00506010`, harden signatures, or close the weapon-fired
stealth gap.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "weapon-burst-comment-pass" / "current"
DEFAULT_DRY_LOG = BASE / "comments_dry.log"
DEFAULT_APPLY_LOG = BASE / "comments_apply.log"
DEFAULT_METADATA = BASE / "metadata_after.tsv"
DEFAULT_OUT = BASE / "weapon-burst-comment-pass.json"

TARGETS = [
    {
        "address": "0x00506930",
        "name": "CWeapon__HandleFireBurstEvent",
        "tokens": ["event handler", "0x1389", "CWeapon::Fire", "runtime stealth proof"],
    },
    {
        "address": "0x00505f70",
        "name": "CWeapon__scalar_deleting_dtor",
        "tokens": ["Scalar deleting destructor", "detach", "conditional"],
    },
    {
        "address": "0x005069f0",
        "name": "CEngine__SpawnProjectileBurstFromCurrentPreset",
        "tokens": ["Inner projectile-burst body", "current preset", "source CWeapon::Fire", "runtime stealth behavior"],
    },
    {
        "address": "0x00506010",
        "name": "CGeneralVolume__SpawnBurstFromPresetWithFallback",
        "tokens": ["Shared preset fallback dispatcher", "UnitAI", "Sentinel", "provisional"],
    },
]


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def unescape_tsv(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_metadata(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        row["comment"] = unescape_tsv(row.get("comment", ""))
    return rows


def parse_summary(log_text: str) -> dict[str, int]:
    match = re.search(r"applied=(\d+)\s+skipped=(\d+)\s+missing=(\d+)\s+bad=(\d+)", log_text)
    if not match:
        return {"applied": -1, "skipped": -1, "missing": -1, "bad": -1}
    return {
        "applied": int(match.group(1)),
        "skipped": int(match.group(2)),
        "missing": int(match.group(3)),
        "bad": int(match.group(4)),
    }


def has_log_line(log_text: str, prefix: str, address: str, name: str) -> bool:
    return f"{prefix}: {address} {name}" in log_text


def find_row(rows: list[dict[str, str]], address: str) -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get("address", "")) == wanted:
            return row
    return None


def build_report(
    *,
    dry_log_path: Path = DEFAULT_DRY_LOG,
    apply_log_path: Path = DEFAULT_APPLY_LOG,
    metadata_path: Path = DEFAULT_METADATA,
) -> dict[str, object]:
    dry_log_path = resolve(dry_log_path)
    apply_log_path = resolve(apply_log_path)
    metadata_path = resolve(metadata_path)

    failures: list[str] = []
    for label, path in (
        ("dry comment log", dry_log_path),
        ("apply comment log", apply_log_path),
        ("metadata read-back", metadata_path),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")

    dry_text = read_text(dry_log_path)
    apply_text = read_text(apply_log_path)
    metadata_rows = read_metadata(metadata_path)

    dry_summary = parse_summary(dry_text)
    apply_summary = parse_summary(apply_text)

    expected_count = len(TARGETS)
    if dry_summary != {"applied": 0, "skipped": expected_count, "missing": 0, "bad": 0}:
        failures.append("dry comment log summary is not the expected clean dry-run shape")
    if apply_summary != {"applied": expected_count, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append("apply comment log summary is not the expected clean apply shape")

    readback: dict[str, object] = {}
    all_comments_present = True
    for target in TARGETS:
        address = target["address"]
        name = target["name"]
        if not has_log_line(dry_text, "DRY", address, name):
            failures.append(f"dry log missing expected target {address} {name}")
        if not has_log_line(apply_text, "OK", address, name):
            failures.append(f"apply log missing expected target {address} {name}")

        row = find_row(metadata_rows, address)
        if row is None:
            failures.append(f"metadata read-back missing {address}")
            readback[address] = {"name": None, "commentTokensPresent": False}
            all_comments_present = False
            continue

        row_name = row.get("name", "")
        comment = row.get("comment", "")
        tokens_present = all(token in comment for token in target["tokens"])
        row_ok = row_name == name and row.get("status") == "OK" and tokens_present
        readback[address] = {
            "name": row_name,
            "status": row.get("status"),
            "commentTokensPresent": tokens_present,
        }
        if not row_ok:
            failures.append(f"metadata read-back for {address} lacks expected name/status/comment tokens")
            all_comments_present = False

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "battleengine-weapon-burst-comment-pass.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "candidateClassification": "weapon-burst-cluster-comments-applied"
        if status == "PASS"
        else "weapon-burst-cluster-comment-pass-blocked",
        "drySummary": dry_summary,
        "applySummary": apply_summary,
        "targets": [{"address": t["address"], "name": t["name"]} for t in TARGETS],
        "readback": {
            "allCommentsPresent": all_comments_present,
            "functions": readback,
        },
        "inputs": {
            "dryLog": relative(dry_log_path),
            "applyLog": relative(apply_log_path),
            "metadata": relative(metadata_path),
        },
        "failures": failures,
        "whatIsProven": [
            "The saved Ghidra project has function comments for the four checked weapon/burst-cluster functions.",
            "The comments record behavior evidence and proof boundaries for the event handler, destructor, inner projectile-burst body, and shared preset fallback dispatcher.",
            "Read-back metadata confirms the expected current names and comment tokens after apply.",
        ],
        "notProven": [
            "This does not rename 0x005069f0 or 0x00506010.",
            "This does not harden signatures or parameter names.",
            "This does not prove exact source CWeapon::Fire or CBattleEngine::WeaponFired identity.",
            "This does not prove retail weapon fire clears or preserves stealth.",
            "This does not prove runtime cloak activation or fire-while-cloaked behavior.",
        ],
        "privacy": "Report stores repo-relative artifact paths, public addresses, function names, command summaries, counts, and proof boundaries only; raw Ghidra logs and metadata exports remain ignored under subagents/.",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--dry-log", type=Path, default=DEFAULT_DRY_LOG)
    parser.add_argument("--apply-log", type=Path, default=DEFAULT_APPLY_LOG)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    out = resolve(args.out)
    try:
        out.resolve().relative_to((ROOT / "subagents").resolve())
    except ValueError:
        print(f"Refusing to write report outside subagents/: {out}", file=sys.stderr)
        return 1

    report = build_report(dry_log_path=args.dry_log, apply_log_path=args.apply_log, metadata_path=args.metadata)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("BattleEngine weapon/burst comment-pass probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Classification: {report['candidateClassification']}")
        print(f"Dry summary: {report['drySummary']}")
        print(f"Apply summary: {report['applySummary']}")
        print(f"All comments present: {report['readback']['allCommentsPresent']}")
        if report["failures"]:
            print("Failures:")
            for failure in report["failures"]:
                print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
