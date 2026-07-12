#!/usr/bin/env python3
"""Validate the retired static-to-proof register and its active handoff."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_MIRROR = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
FRONT_DOOR = ROOT / "roadmap" / "rebuild-front-door-chain-map.md"
REBUILD_README = ROOT / "rebuild" / "README.md"

REQUIRED_BACKLOG_MARKERS = (
    "Status: historical evidence register; superseded as implementation guidance",
    "## Historical Terminal Proof Slice",
    "No additional child proof-plan slice is selected from it.",
    "Do not select new implementation work from this register.",
    "Static Ghidra function-quality closure",
    "tmm-arm4-readiness-gate",
)

FORBIDDEN_ACTIVE_MARKERS = (
    "Status: active planning backlog",
    "## Active Proof Slice",
    "Start a runtime, visual, patch, Godot, or rebuild slice only after choosing one row",
)

REQUIRED_FRONT_DOOR_MARKERS = (
    "Status: active implementation routing map",
    "rebuild/README.md",
    "OnslaughtRebuild.Core",
    "OnslaughtRebuild.Headless",
    "Future Godot .NET client",
    "Historical Chain",
)


def validate_backlog(text: str) -> list[str]:
    failures: list[str] = []
    for marker in REQUIRED_BACKLOG_MARKERS:
        if marker not in text:
            failures.append(f"backlog missing historical marker: {marker}")

    for marker in FORBIDDEN_ACTIVE_MARKERS:
        if marker in text:
            failures.append(f"backlog still contains active-guidance marker: {marker}")

    numbered_rows = re.findall(r"^\|\s*(\d+)\s*\|", text, flags=re.MULTILINE)
    if numbered_rows != [str(number) for number in range(1, 91)]:
        failures.append("historical backlog rows are not the intact ordered range 1 through 90")

    return failures


def validate_front_door(text: str) -> list[str]:
    return [
        f"front door missing marker: {marker}"
        for marker in REQUIRED_FRONT_DOOR_MARKERS
        if marker not in text
    ]


def check_repository() -> list[str]:
    failures: list[str] = []
    for path in (BACKLOG, LORE_MIRROR, FRONT_DOOR, REBUILD_README):
        if not path.is_file():
            failures.append(f"required file missing: {path.relative_to(ROOT).as_posix()}")

    if failures:
        return failures

    backlog_text = BACKLOG.read_text(encoding="utf-8")
    mirror_text = LORE_MIRROR.read_text(encoding="utf-8")
    if backlog_text != mirror_text:
        failures.append("roadmap backlog and lore-book mirror differ")

    failures.extend(validate_backlog(backlog_text))
    failures.extend(validate_front_door(FRONT_DOOR.read_text(encoding="utf-8")))
    return failures


def self_test() -> list[str]:
    failures: list[str] = []
    synthetic = "\n".join(
        [*REQUIRED_BACKLOG_MARKERS]
        + [f"| {number} | row |" for number in range(1, 91)]
    )
    if validate_backlog(synthetic):
        failures.append("self-test rejected a valid historical register")

    stale = synthetic + "\n## Active Proof Slice\n"
    stale_failures = validate_backlog(stale)
    if not any("active-guidance marker" in failure for failure in stale_failures):
        failures.append("self-test did not reject stale active guidance")

    damaged = synthetic.replace("| 47 | row |", "")
    damaged_failures = validate_backlog(damaged)
    if not any("ordered range" in failure for failure in damaged_failures):
        failures.append("self-test did not reject a missing historical row")

    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    failures = check_repository() if args.check else self_test()
    label = "check" if args.check else "self-test"
    if failures:
        print(f"Static-to-proof historical register {label}: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"Static-to-proof historical register {label}: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
