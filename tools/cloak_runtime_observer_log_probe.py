#!/usr/bin/env python3
"""Summarize CDB cloak-latch observer logs.

The matching CDB command file is
``tools/runtime-probes/cloak-latch-observer.cdb.txt``. This parser does not
launch BEA, attach a debugger, mutate runtime state, or read private game
assets. It consumes an existing text log and produces a public-safe summary.
"""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]

EVENT_RE = re.compile(
    r"Cloak latch helper (?P<phase>enter|exit) "
    r"(?:path=(?P<path>[a-zA-Z0-9_-]+) )?"
    r"this=(?P<this>[0-9a-fA-F`]+) "
    r"latch=(?P<latch>[0-9a-fA-F]+) "
    r"targetRaw=(?P<target>[0-9a-fA-F]+) "
    r"energyRaw=(?P<energy>[0-9a-fA-F]+) "
    r"currentRaw=(?P<current>[0-9a-fA-F]+) "
    r"desiredRaw=(?P<desired>[0-9a-fA-F]+)"
    r"(?: "
    r"linkedPtr=(?P<linked_ptr>[0-9a-fA-F`]+) "
    r"linked2cRaw=(?P<linked_2c>[0-9a-fA-F]+) "
    r"linkedA0Raw=(?P<linked_a0>[0-9a-fA-F]+) "
    r"thresholdRaw=(?P<threshold>[0-9a-fA-F]+)"
    r")?"
)

CHECKSUM_WARNING_RE = re.compile(
    r"this=\*\*\* WARNING: Unable to verify checksum for [^\r\n]*\r?\n"
)


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def hex_to_int(value: str) -> int:
    return int(value.replace("`", ""), 16)


def optional_hex_to_int(value: str | None) -> int | None:
    if not value:
        return None
    return hex_to_int(value)


def raw_float(value: int | None) -> float | None:
    if value is None:
        return None
    return struct.unpack("<f", value.to_bytes(4, byteorder="little", signed=False))[0]


def gate_summary(event: dict[str, object]) -> dict[str, object] | None:
    linked_2c = event.get("linked2cRaw")
    linked_a0 = event.get("linkedA0Raw")
    threshold = event.get("thresholdRaw")
    if linked_2c is None or linked_a0 is None or threshold is None:
        return None

    linked_2c_float = raw_float(linked_2c if isinstance(linked_2c, int) else None)
    linked_a0_float = raw_float(linked_a0 if isinstance(linked_a0, int) else None)
    threshold_float = raw_float(threshold if isinstance(threshold, int) else None)
    energy_float = raw_float(event.get("energyRaw") if isinstance(event.get("energyRaw"), int) else None)

    energy_gate_pass = (
        linked_2c_float is not None and energy_float is not None and linked_2c_float <= energy_float
    )
    threshold_gate_pass = (
        linked_a0_float is not None and threshold_float is not None and threshold_float < linked_a0_float
    )
    blocked_by: list[str] = []
    if not energy_gate_pass:
        blocked_by.append("linked2c_gt_energy")
    if not threshold_gate_pass:
        blocked_by.append("linkedA0_not_above_threshold")

    return {
        "linked2cFloat": linked_2c_float,
        "linkedA0Float": linked_a0_float,
        "thresholdFloat": threshold_float,
        "energyFloat": energy_float,
        "energyGatePass": energy_gate_pass,
        "thresholdGatePass": threshold_gate_pass,
        "gateInputsPass": energy_gate_pass and threshold_gate_pass,
        "blockedBy": blocked_by,
    }


def parse_events(text: str) -> list[dict[str, object]]:
    events: list[dict[str, object]] = []
    cleaned = CHECKSUM_WARNING_RE.sub("this=", text)
    for line_number, line in enumerate(cleaned.splitlines(), start=1):
        for match in EVENT_RE.finditer(line):
            event = {
                "line": line_number,
                "phase": match.group("phase"),
                "path": match.group("path") or "",
                "this": match.group("this").replace("`", ""),
                "latch": hex_to_int(match.group("latch")),
                "targetRaw": hex_to_int(match.group("target")),
                "energyRaw": hex_to_int(match.group("energy")),
                "currentRaw": hex_to_int(match.group("current")),
                "desiredRaw": hex_to_int(match.group("desired")),
                "linkedPtr": (match.group("linked_ptr") or "").replace("`", ""),
                "linked2cRaw": optional_hex_to_int(match.group("linked_2c")),
                "linkedA0Raw": optional_hex_to_int(match.group("linked_a0")),
                "thresholdRaw": optional_hex_to_int(match.group("threshold")),
            }
            summary = gate_summary(event)
            if summary is not None:
                event["gateSummary"] = summary
            events.append(event)
    return events


def pair_events(events: list[dict[str, object]]) -> list[dict[str, object]]:
    pairs: list[dict[str, object]] = []
    pending: dict[str, object] | None = None
    for event in events:
        if event["phase"] == "enter":
            pending = event
            continue
        if event["phase"] != "exit" or pending is None:
            continue
        pairs.append({"enter": pending, "exit": event})
        pending = None
    return pairs


def build_report_from_text(text: str, *, source: str = "<memory>") -> dict[str, object]:
    events = parse_events(text)
    pairs = pair_events(events)

    activation_pairs = [
        pair
        for pair in pairs
        if pair["enter"]["latch"] == 0
        and pair["exit"]["latch"] != 0
        and pair["exit"]["targetRaw"] != 0
    ]
    deactivation_pairs = [
        pair
        for pair in pairs
        if pair["enter"]["latch"] != 0
        and pair["exit"]["latch"] == 0
        and pair["exit"]["targetRaw"] == 0
    ]
    gate_blocked_pairs = [
        pair
        for pair in pairs
        if pair["enter"].get("gateSummary")
        and not pair["enter"]["gateSummary"].get("gateInputsPass")
    ]

    if not events:
        status = "FAIL"
        verdict = "NO_LATCH_EVENTS"
    elif activation_pairs:
        status = "PASS"
        verdict = "ACTIVATION_OBSERVED"
    elif deactivation_pairs:
        status = "PASS"
        verdict = "DEACTIVATION_ONLY"
    else:
        status = "PASS"
        verdict = "EVENTS_WITHOUT_ACTIVATION"

    return {
        "schema": "cloak-runtime-observer-log.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "status": status,
        "verdict": verdict,
        "eventCount": len(events),
        "pairCount": len(pairs),
        "activationPairCount": len(activation_pairs),
        "deactivationPairCount": len(deactivation_pairs),
        "gateBlockedPairCount": len(gate_blocked_pairs),
        "events": events,
        "pairs": pairs,
        "notClaimed": [
            "This parser does not launch BEA.exe.",
            "This parser does not attach CDB or mutate runtime state.",
            "This parser only summarizes an existing cloak-latch observer log.",
            "A latch transition is a candidate cloak-active detector, not exact CBattleEngine source-method identity.",
        ],
    }


def run_self_test() -> int:
    sample = "\n".join(
        [
            "Cloak latch helper enter this=01234567 latch=0 targetRaw=00000000 energyRaw=42c80000 currentRaw=00000000 desiredRaw=00000000",
            "Cloak latch helper exit path=set-or-skip this=01234567 latch=1 targetRaw=42c80000 energyRaw=42c80000 currentRaw=00000000 desiredRaw=00000000",
        ]
    )
    report = build_report_from_text(sample)
    if report["status"] != "PASS" or report["verdict"] != "ACTIVATION_OBSERVED":
        print(json.dumps(report, indent=2))
        return 1

    noisy_same_line = (
        "Cloak latch helper enter path=entry this=*** WARNING: Unable to verify checksum for copied BEA.exe\n"
        "01234567 latch=0 targetRaw=00000000 energyRaw=41000000 currentRaw=3f800000 desiredRaw=3f800000 "
        "Cloak latch helper exit path=set-or-skip this=01234567 latch=0 targetRaw=00000000 "
        "energyRaw=41000000 currentRaw=3f800000 desiredRaw=3f800000 "
        "Cloak latch helper enter path=entry this=01234567 latch=0 targetRaw=00000000 "
        "energyRaw=41000000 currentRaw=3f800000 desiredRaw=3f800000 "
        "Cloak latch helper exit path=set-or-skip this=01234567 latch=0 targetRaw=00000000 "
        "energyRaw=41000000 currentRaw=3f800000 desiredRaw=3f800000"
    )
    noisy_report = build_report_from_text(noisy_same_line)
    if (
        noisy_report["status"] != "PASS"
        or noisy_report["verdict"] != "EVENTS_WITHOUT_ACTIVATION"
        or noisy_report["eventCount"] != 4
        or noisy_report["pairCount"] != 2
    ):
        print(json.dumps(noisy_report, indent=2))
        return 1

    gate_blocked = (
        "Cloak latch helper enter path=entry this=01234567 latch=0 targetRaw=00000000 "
        "energyRaw=3f000000 currentRaw=3f800000 desiredRaw=3f800000 linkedPtr=07654321 "
        "linked2cRaw=40000000 linkedA0Raw=00000000 thresholdRaw=3dcccccd\n"
        "Cloak latch helper exit path=set-or-skip this=01234567 latch=0 targetRaw=00000000 "
        "energyRaw=3f000000 currentRaw=3f800000 desiredRaw=3f800000 linkedPtr=07654321 "
        "linked2cRaw=40000000 linkedA0Raw=00000000 thresholdRaw=3dcccccd"
    )
    gate_report = build_report_from_text(gate_blocked)
    if (
        gate_report["status"] != "PASS"
        or gate_report["verdict"] != "EVENTS_WITHOUT_ACTIVATION"
        or gate_report["gateBlockedPairCount"] != 1
        or gate_report["events"][0]["gateSummary"]["blockedBy"]
        != ["linked2c_gt_energy", "linkedA0_not_above_threshold"]
    ):
        print(json.dumps(gate_report, indent=2))
        return 1

    no_events = build_report_from_text("ordinary debugger noise")
    if no_events["status"] != "FAIL" or no_events["verdict"] != "NO_LATCH_EVENTS":
        print(json.dumps(no_events, indent=2))
        return 1

    print("PASS: cloak runtime observer parser self-test")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--require-activation",
        action="store_true",
        help="Exit non-zero unless the observer log contains a latch-off to latch-on transition.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.self_test:
        return run_self_test()
    if not args.log:
        print("expected --log or --self-test", file=sys.stderr)
        return 2

    text = args.log.read_text(encoding="utf-8", errors="replace")
    report = build_report_from_text(text, source=relative(args.log))

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(
        f"{report['status']}: {report['verdict']} "
        f"events={report['eventCount']} pairs={report['pairCount']} "
        f"activations={report['activationPairCount']}"
    )
    if args.out:
        print(f"wrote {relative(args.out)}")

    if args.require_activation and report["verdict"] != "ACTIVATION_OBSERVED":
        return 1
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
