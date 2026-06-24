#!/usr/bin/env python3
"""Summarize mission-script Goodie state call sites.

The probe scans a local mission-script corpus for ``GetGoodieState`` and
``SetGoodieState`` calls. It is designed to produce public-safe counts while raw
script files remain private/release-excluded when they live under ``game/``.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCRIPT_ROOT = ROOT / "game" / "data" / "MissionScripts"
DEFAULT_RESOURCE_ROOT = ROOT / "game" / "data" / "Resources"
DEFAULT_OUT = (
    ROOT
    / "subagents"
    / "goodies-script-corpus"
    / "current"
    / "goodies-script-corpus.json"
)
CALL_RE = re.compile(r"\b(?P<call>GetGoodieState|SetGoodieState)\s*\(\s*(?P<index>\d+)\b")
GOODIE_TOKEN_RE = re.compile(r"\b(?:GOODIE|Goodie|goodie)\b")
TARGET_SCRIPT_INDICES = {72, 73, 74}


def display_path(path: Path, root_path: Path | None = None, root_label: str = "<script-root>") -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        pass
    if root_path is not None:
        try:
            root_resolved = root_path.resolve()
            if resolved == root_resolved:
                return root_label
            return f"{root_label}/" + resolved.relative_to(root_resolved).as_posix()
        except ValueError:
            pass
    return "<external-path>"


def iter_scripts(script_root: Path) -> list[Path]:
    if not script_root.is_dir():
        return []
    return sorted(script_root.rglob("*.msl"))


def iter_packed_resource_archives(resource_root: Path) -> list[Path]:
    if not resource_root.is_dir():
        return []
    return sorted(path for path in resource_root.glob("*.aya") if path.is_file())


def scan_scripts(script_root: Path) -> tuple[list[dict[str, object]], Counter[int], Counter[str]]:
    calls: list[dict[str, object]] = []
    index_counts: Counter[int] = Counter()
    call_counts: Counter[str] = Counter()
    for script in iter_scripts(script_root):
        text = script.read_text(encoding="utf-8", errors="replace")
        for line_number, line in enumerate(text.splitlines(), start=1):
            for match in CALL_RE.finditer(line):
                script_index = int(match.group("index"))
                call_name = match.group("call")
                index_counts[script_index] += 1
                call_counts[call_name] += 1
                calls.append(
                    {
                        "file": display_path(script, script_root),
                        "line": line_number,
                        "call": call_name,
                        "scriptIndex": script_index,
                        "saveGoodieIndex": script_index - 1,
                    }
                )
    return calls, index_counts, call_counts


def scan_packed_resources(resource_root: Path) -> dict[str, object]:
    try:
        from aya_archive_inventory import inflate_aya
    except ImportError as exc:  # pragma: no cover - import failure is environment-specific.
        return {
            "enabled": True,
            "status": "FAIL",
            "resourceRoot": display_path(resource_root, resource_root, "<resource-root>"),
            "archiveCount": 0,
            "inflateErrorCount": 0,
            "inflateErrors": [],
            "tokenFileCount": 0,
            "callCount": 0,
            "callCounts": {},
            "scriptIndexCounts": {},
            "saveGoodieIndices": [],
            "targetHitCount": 0,
            "targetHits": [],
            "failures": [f"could not import aya_archive_inventory.inflate_aya: {exc}"],
        }

    archives = iter_packed_resource_archives(resource_root)
    calls: list[dict[str, object]] = []
    index_counts: Counter[int] = Counter()
    call_counts: Counter[str] = Counter()
    inflate_errors: list[dict[str, str]] = []
    token_file_count = 0

    for archive in archives:
        archive_label = display_path(archive, resource_root, "<resource-root>")
        try:
            raw = inflate_aya(archive)
        except Exception as exc:  # noqa: BLE001 - this is a corpus probe; record and continue.
            inflate_errors.append(
                {
                    "archive": archive_label,
                    "errorType": type(exc).__name__,
                    "message": str(exc),
                }
            )
            continue

        text = raw.decode("latin-1", errors="replace")
        if GOODIE_TOKEN_RE.search(text):
            token_file_count += 1

        for match in CALL_RE.finditer(text):
            script_index = int(match.group("index"))
            call_name = match.group("call")
            index_counts[script_index] += 1
            call_counts[call_name] += 1
            calls.append(
                {
                    "archive": archive_label,
                    "line": text.count("\n", 0, match.start()) + 1,
                    "call": call_name,
                    "scriptIndex": script_index,
                    "saveGoodieIndex": script_index - 1,
                }
            )

    target_hits = [call for call in calls if call["scriptIndex"] in TARGET_SCRIPT_INDICES]
    failures: list[str] = []
    if inflate_errors:
        failures.append("one or more packed resource archives could not be inflated")
    if target_hits:
        failures.append("packed resource Goodie calls target script indices 72-74")

    unique_indices = sorted(index_counts)
    return {
        "enabled": True,
        "status": "PASS" if not failures else "FAIL",
        "resourceRoot": display_path(resource_root, resource_root, "<resource-root>"),
        "archiveCount": len(archives),
        "inflateErrorCount": len(inflate_errors),
        "inflateErrors": inflate_errors,
        "tokenFileCount": token_file_count,
        "callCount": len(calls),
        "callCounts": dict(sorted(call_counts.items())),
        "scriptIndexCounts": {str(key): index_counts[key] for key in unique_indices},
        "saveGoodieIndices": [key - 1 for key in unique_indices],
        "targetHitCount": len(target_hits),
        "targetHits": target_hits,
        "failures": failures,
    }


def build_report(
    script_root: Path,
    require_root: bool,
    *,
    resource_root: Path,
    scan_packed_resource_archives_enabled: bool,
) -> dict[str, object]:
    failures: list[str] = []
    scripts = iter_scripts(script_root)
    if not scripts and require_root:
        failures.append(
            f"missing or empty script root: {display_path(script_root, script_root, '<script-root>')}"
        )

    calls, index_counts, call_counts = scan_scripts(script_root)
    target_hits = [call for call in calls if call["scriptIndex"] in TARGET_SCRIPT_INDICES]
    if target_hits:
        failures.append("mission-script Goodie calls target script indices 72-74")

    if scan_packed_resource_archives_enabled:
        packed_scan = scan_packed_resources(resource_root)
        if not packed_scan["archiveCount"] and require_root:
            packed_scan["failures"].append(
                f"missing or empty resource root: {display_path(resource_root, resource_root, '<resource-root>')}"
            )
            packed_scan["status"] = "FAIL"
        failures.extend(f"packed resource scan: {failure}" for failure in packed_scan["failures"])
    else:
        packed_scan = {
            "enabled": False,
            "resourceRoot": display_path(resource_root, resource_root, "<resource-root>"),
            "archiveCount": 0,
            "inflateErrorCount": 0,
            "tokenFileCount": 0,
            "callCount": 0,
            "targetHitCount": 0,
            "failures": [],
        }

    unique_indices = sorted(index_counts)
    return {
        "schema": "goodies-script-corpus.v2",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "scriptRoot": display_path(script_root, script_root, "<script-root>"),
        "scriptFileCount": len(scripts),
        "callCount": len(calls),
        "callCounts": dict(sorted(call_counts.items())),
        "scriptIndexCounts": {str(key): index_counts[key] for key in unique_indices},
        "saveGoodieIndices": [key - 1 for key in unique_indices],
        "targetScriptIndices": sorted(TARGET_SCRIPT_INDICES),
        "targetHitCount": len(target_hits),
        "targetHits": target_hits,
        "packedResourceScan": packed_scan,
        "currentClaims": [
            "The local mission-script corpus uses Goodie state APIs for the listed 1-based script indices.",
            "Goodies 71-73 would correspond to script indices 72-74.",
            "The current local mission-script corpus has no Goodie state calls for script indices 72-74.",
            "When enabled, the packed resource scan checks top-level inflated AYA archives for literal Goodie state API calls.",
        ],
        "notClaimed": [
            "This probe does not prove compiled, bytecode, indirect, or runtime-generated scripts cannot differ from the checked text corpus.",
            "This probe does not launch BEA.exe or prove runtime reachability.",
            "This probe does not inspect non-MSL binary paths.",
        ],
        "failures": failures,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--script-root", type=Path, default=DEFAULT_SCRIPT_ROOT)
    parser.add_argument("--resource-root", type=Path, default=DEFAULT_RESOURCE_ROOT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--scan-packed-resources",
        action="store_true",
        help="Also scan top-level inflated AYA resource archives for literal Goodie state API calls.",
    )
    parser.add_argument(
        "--require-root",
        action="store_true",
        help="Fail if the script root is missing or empty.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if target script indices are found or required input is missing.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report = build_report(
        args.script_root,
        args.require_root,
        resource_root=args.resource_root,
        scan_packed_resource_archives_enabled=args.scan_packed_resources,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{report['status']}: wrote {display_path(args.out)}")
    print(
        "mission-script Goodie calls: "
        f"files={report['scriptFileCount']} calls={report['callCount']} "
        f"indices={','.join(map(str, report['scriptIndexCounts'].keys()))} "
        f"target72to74={report['targetHitCount']}"
    )
    packed_scan = report["packedResourceScan"]
    if packed_scan["enabled"]:
        print(
            "packed resource Goodie calls: "
            f"archives={packed_scan['archiveCount']} "
            f"inflateErrors={packed_scan['inflateErrorCount']} "
            f"tokenFiles={packed_scan['tokenFileCount']} "
            f"calls={packed_scan['callCount']} "
            f"target72to74={packed_scan['targetHitCount']}"
        )
    if args.check and report["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
