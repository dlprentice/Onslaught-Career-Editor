#!/usr/bin/env python3
"""Summarize CDB Goodies selection observer logs.

The matching CDB command file is
``tools/runtime-probes/goodies-selection-observer.cdb.txt``. This parser does
not launch BEA, attach a debugger, mutate Ghidra, or read private game assets.
It consumes an existing text log and produces a public-safe summary shape.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_NORMAL_SEQUENCE = (66, 67, 68, 69, 70, 74)
HIDDEN_GOODIE_IDS = {71, 72, 73}

COORDINATE_RE = re.compile(
    r"Goodies get_goodie_number x=(?P<x>-?\d+) y=(?P<y>-?\d+) ret=(?P<ret>-?\d+)"
)
NAVIGATION_RE = re.compile(
    r"Goodies (?P<kind>vertical-up-scan|vertical-down-scan|right-probe-after-clamp|"
    r"right-backtrack-scan|selected-state-precheck|selected-load-gate|"
    r"post-load-state-check|mark-selected-old|StartLoadingGoody) "
    r"(?:(?:ret=(?P<ret>-?\d+) )?)"
    r"this=(?P<this>[0-9a-fA-F]+) mCX=(?P<mCX>-?\d+) mCY=(?P<mCY>-?\d+)"
)
BUTTON_ENTRY_RE = re.compile(
    r"Goodies ButtonPressed entry button=(?P<button>-?\d+) "
    r"this=(?P<this>[0-9a-fA-F]+) mCX=(?P<mCX>-?\d+) mCY=(?P<mCY>-?\d+)"
)
DEBUGGER_SKIPPED_WARNING = "commands were skipped because previous commands caused target execution"


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def contains_subsequence(values: list[int], expected: tuple[int, ...]) -> bool:
    if not expected:
        return True
    offset = 0
    for value in values:
        if value == expected[offset]:
            offset += 1
            if offset == len(expected):
                return True
    return False


def build_report_from_text(text: str, *, source: str = "<memory>") -> dict[str, object]:
    coordinate_samples: list[dict[str, int]] = []
    navigation_events: list[dict[str, object]] = []
    button_events: list[dict[str, object]] = []
    returned_id_events: list[int] = []
    debugger_skipped_warning_count = 0

    for line_number, line in enumerate(text.splitlines(), start=1):
        if DEBUGGER_SKIPPED_WARNING in line:
            debugger_skipped_warning_count += 1

        for coordinate_match in COORDINATE_RE.finditer(line):
            returned_id = int(coordinate_match.group("ret"))
            coordinate_samples.append(
                {
                    "line": line_number,
                    "x": int(coordinate_match.group("x")),
                    "y": int(coordinate_match.group("y")),
                    "returnedGoodieId": returned_id,
                }
            )
            returned_id_events.append(returned_id)

        for navigation_match in NAVIGATION_RE.finditer(line):
            event: dict[str, object] = {
                "line": line_number,
                "kind": navigation_match.group("kind"),
                "this": navigation_match.group("this"),
                "mCX": int(navigation_match.group("mCX")),
                "mCY": int(navigation_match.group("mCY")),
            }
            returned = navigation_match.group("ret")
            if returned is not None:
                returned_id = int(returned)
                event["returnedGoodieId"] = returned_id
                returned_id_events.append(returned_id)
            navigation_events.append(event)

        for button_match in BUTTON_ENTRY_RE.finditer(line):
            button_events.append(
                {
                    "line": line_number,
                    "button": int(button_match.group("button")),
                    "this": button_match.group("this"),
                    "mCX": int(button_match.group("mCX")),
                    "mCY": int(button_match.group("mCY")),
                }
            )

    returned_ids = returned_id_events
    hidden_ids = sorted({value for value in returned_ids if value in HIDDEN_GOODIE_IDS})
    normal_observed = contains_subsequence(returned_ids, EXPECTED_NORMAL_SEQUENCE)
    input_path_observed = bool(button_events or navigation_events)

    if not coordinate_samples and not input_path_observed:
        status = "FAIL"
        verdict = "NO_SELECTION_EVENTS"
    elif hidden_ids:
        status = "PASS"
        verdict = "HIDDEN_IDS_OBSERVED"
    elif normal_observed:
        status = "PASS"
        verdict = "NORMAL_SEQUENCE_CONFIRMED"
    else:
        status = "PASS"
        verdict = "INCOMPLETE_SEQUENCE"

    return {
        "schema": "goodies-selection-observer-log.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "status": status,
        "verdict": verdict,
        "expectedNormalSequence": list(EXPECTED_NORMAL_SEQUENCE),
        "expectedNormalSequenceObserved": normal_observed,
        "hiddenReturnIds": hidden_ids,
        "returnedGoodieIds": returned_ids,
        "uniqueReturnedGoodieIds": sorted(set(returned_ids)),
        "coordinateSampleCount": len(coordinate_samples),
        "inputPathObserved": input_path_observed,
        "buttonEventCount": len(button_events),
        "navigationEventCount": len(navigation_events),
        "debuggerSkippedCommandWarningCount": debugger_skipped_warning_count,
        "coordinateSamples": coordinate_samples,
        "buttonEvents": button_events,
        "navigationEvents": navigation_events,
        "notClaimed": [
            "This parser does not launch BEA.exe.",
            "This parser does not attach CDB or mutate runtime state.",
            "This parser only summarizes an existing observer log.",
        ],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    parser.add_argument(
        "--check-normal-skip",
        action="store_true",
        help="Exit non-zero unless the expected 66,67,68,69,70,74 sequence is observed without hidden 71-73 returns.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    text = args.log.read_text(encoding="utf-8", errors="replace")
    report = build_report_from_text(text, source=relative(args.log))

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(
        f"{report['status']}: {report['verdict']} "
        f"coordinates={report['coordinateSampleCount']} navigation={report['navigationEventCount']}"
    )
    if args.out:
        print(f"wrote {relative(args.out)}")

    if args.check_normal_skip and report["verdict"] != "NORMAL_SEQUENCE_CONFIRMED":
        return 1
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
