#!/usr/bin/env python3
"""Classify the second read-only Ghidra name-confidence re-audit tranche."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "name-confidence-tranche2" / "current"
DEFAULT_SEEDS = BASE / "seed_names.json"
DEFAULT_INDEX = BASE / "decompile" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile"
DEFAULT_XREFS = BASE / "xrefs.tsv"
DEFAULT_OUT = BASE / "name-confidence-tranche2.json"

RULES = {
    "0x00411bf0": {
        "classification": "mode-specific-burst-dispatch-helper",
        "action": "commentCandidate",
        "tokens": [
            "CEngine__CanProceedByTargetRangeGate",
            "CEngine__ClampBurstStartTimeFloorNow",
            "CGeneralVolume__SpawnBurstFromPresetWithFallback",
        ],
        "expectedXrefFunctions": ["CGeneralVolume__DispatchModeSpecificReset_13CF0_or_11BF0"],
        "note": "Walks the selected preset/set entry, applies range/cooldown/start-time gates, and dispatches the shared burst spawn helper; owner/name need a focused source-boundary pass before rename.",
    },
    "0x00412240": {
        "classification": "selected-entry-rounded-slot-value",
        "action": "commentCandidate",
        "tokens": ["ROUND(", "+ 0x55c", "+ 0x52c"],
        "expectedXrefFunctions": ["CExplosionInitThing__GetCurrentEntryRoundedSlotValue"],
        "note": "Returns a rounded current slot/cooldown-style value for the selected entry rather than acting as a generic ROUND wrapper.",
    },
    "0x00412420": {
        "classification": "selected-entry-display-string",
        "action": "commentCandidate",
        "tokens": ["CText__GetStringById", "g_Text", "+ 0x3c"],
        "expectedXrefFunctions": ["CExplosionInitThing__GetCurrentEntryDisplayString"],
        "note": "Resolves the selected entry's text id through CText::GetStringById; the wrapper label is weaker than the observed behavior.",
    },
    "0x00412650": {
        "classification": "profile-weapon-list-rebuild",
        "action": "commentCandidate",
        "tokens": ["CSPtrSet__Remove", "CWorldPhysicsManager__CreateWeaponByIndex", "+ 0x50"],
        "expectedXrefFunctions": [
            "CBattleEngine__ApplyWeaponProfileByIndex",
            "CBattleEngine__InitTargetSetBucketState",
        ],
        "note": "Destroys existing set entries and recreates weapon objects from a profile/config list; exact jet/walker ownership remains deferred.",
    },
    "0x00412830": {
        "classification": "cockpit-disable-matching-weapon-and-reselect",
        "action": "commentCandidate",
        "tokens": ["CCockpit__CycleToNextUsableWeapon", "+ 0x9c", "param_1"],
        "expectedXrefRows": 1,
        "note": "Finds weapon entries whose nested name matches the input, clears their usable flag, and cycles selection if the current weapon was disabled.",
    },
    "0x00412ad0": {
        "classification": "monitor-surface-alignment-angle-update",
        "action": "commentCandidate",
        "tokens": ["ABS(", "+ 0x24", "_DAT_005d85e0"],
        "expectedXrefFunctions": ["CMonitor__ProcessTrackingAndSurfaceAlignment"],
        "note": "Updates a wrapped angle/state field from transformed direction components during monitor tracking/surface alignment.",
    },
    "0x00413660": {
        "classification": "general-volume-scaled-energy-drain",
        "action": "commentCandidate",
        "tokens": ["CGeneralVolume__ToDoubleIdentity", "+ 0x278", "+ 0x2c8"],
        "expectedXrefRows": 1,
        "note": "Applies a class/profile-scaled drain to a linked object's energy-like field; owner/method boundary remain provisional.",
    },
    "0x004146b0": {
        "classification": "profile-weapon-and-special-slot-rebuild",
        "action": "commentCandidate",
        "tokens": ["CSPtrSet__Remove", "CWorldPhysicsManager__CreateWeaponByIndex", "+ 0x40", "+ 0x60"],
        "expectedXrefFunctions": [
            "CBattleEngine__ApplyWeaponProfileByIndex",
            "CBattleEngine__InitDashMoveParams",
        ],
        "note": "Rebuilds a primary weapon set and two owned special/singleton weapon slots from profile/config names.",
    },
    "0x00414b30": {
        "classification": "target-set-timeout-scan",
        "action": "renameCandidate",
        "tokens": ["CUnit__IsTargetTimeoutBeforeProfileLimit", "return 1"],
        "expectedXrefFunctions": ["CBattleEngine__UpdateAutoTargetSetAndFireProjectiles"],
        "note": "Scans a target/unit set and returns true when any entry passes the timeout/profile-limit predicate; current CVBufTexture owner is very likely wrong.",
    },
    "0x00418090": {
        "classification": "opening-animation-state-helper",
        "action": "defer",
        "tokens": ["s_opening_00623ba4", "FindAnimationIndex", "+ 0x254", "+ 0x25c"],
        "expectedXrefRows": 1,
        "note": "Handles an 'opening' animation state transition with a data/vtable-style xref; owner identity needs vtable/context recovery before mutation.",
    },
    "0x004d3080": {
        "classification": "game-reader-rebind-and-postload-toggle-helper",
        "action": "commentCandidate",
        "tokens": ["CGenericActiveReader__SetReader", "+ 0x574", "+ 0x154"],
        "expectedXrefFunctions": ["CGame__PostLoadProcess", "CGame__RespawnPlayer"],
        "note": "Rebinds a nested ActiveReader relationship and toggles follow-up virtual behavior during post-load/respawn paths.",
    },
    "0x00505c30": {
        "classification": "named-entry-nearest-position-lookup",
        "action": "renameCandidate",
        "tokens": ["stricmp", "DAT_00854fc8", "0x4b18967f", "+ 0x24"],
        "expectedXrefRows": 2,
        "note": "Looks up a named list entry case-insensitively, then returns the nearest child point by squared distance; it is not a generic stricmp wrapper.",
    },
}


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


def read_seed_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [
        {
            "address": normalize_address(str(item.get("address", ""))),
            "name": str(item.get("name", "")),
        }
        for item in data
    ]


def read_index(path: Path) -> dict[str, dict[str, str]]:
    if not path.is_file():
        return {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    return {normalize_address(row.get("address", "")): row for row in rows}


def read_xrefs(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        row["target_addr"] = normalize_address(row.get("target_addr", ""))
    return rows


def find_decompile_file(decompile_dir: Path, address: str) -> Path | None:
    if not decompile_dir.is_dir():
        return None
    needle = normalize_address(address)[2:]
    matches = sorted(decompile_dir.glob(f"{needle}_*.c"))
    return matches[0] if matches else None


def read_text(path: Path | None) -> str:
    if path is None or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def build_report(
    *,
    seed_path: Path = DEFAULT_SEEDS,
    decompile_index_path: Path = DEFAULT_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
) -> dict[str, object]:
    seed_path = resolve(seed_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)

    failures: list[str] = []
    for label, path in (
        ("seed list", seed_path),
        ("decompile index", decompile_index_path),
        ("decompile dir", decompile_dir),
        ("xref export", xrefs_path),
    ):
        if label == "decompile dir":
            if not path.is_dir():
                failures.append(f"missing {label}: {relative(path)}")
        elif not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")

    seeds = read_seed_rows(seed_path)
    index = read_index(decompile_index_path)
    xrefs = read_xrefs(xrefs_path)
    xrefs_by_target: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in xrefs:
        xrefs_by_target[row["target_addr"]].append(row)

    targets: list[dict[str, object]] = []
    action_counts: Counter[str] = Counter()
    classification_counts: Counter[str] = Counter()

    for seed in seeds:
        address = seed["address"]
        rule = RULES.get(address)
        if rule is None:
            failures.append(f"{address} has no tranche classification rule")
            continue

        index_row = index.get(address)
        decompile_file = find_decompile_file(decompile_dir, address)
        decompile_text = read_text(decompile_file)
        if index_row is None or index_row.get("status") != "OK":
            failures.append(f"{address} missing OK decompile index row")
        if not decompile_text:
            failures.append(f"{address} missing decompile file")

        missing_tokens = [token for token in rule["tokens"] if token not in decompile_text]
        if missing_tokens:
            failures.append(f"{address} missing expected decompile tokens: {', '.join(missing_tokens)}")

        name = seed["name"]
        index_name = index_row.get("name", "") if index_row else ""
        if index_name and index_name != name:
            failures.append(f"{address} seed name mismatch: seed={name} index={index_name}")

        target_xrefs = xrefs_by_target[address]
        expected_rows = int(rule.get("expectedXrefRows", 0))
        if expected_rows and len(target_xrefs) < expected_rows:
            failures.append(f"{address} expected xref context rows >= {expected_rows}, found {len(target_xrefs)}")
        expected_functions = set(rule.get("expectedXrefFunctions", []))
        if expected_functions:
            observed = {row.get("from_function", "") for row in target_xrefs}
            missing = sorted(expected_functions - observed)
            if missing:
                failures.append(f"{address} missing expected xref context: {', '.join(missing)}")

        action = str(rule["action"])
        classification = str(rule["classification"])
        action_counts[action] += 1
        classification_counts[classification] += 1
        targets.append(
            {
                "address": address,
                "name": name,
                "signature": index_row.get("signature", "") if index_row else "",
                "classification": classification,
                "suggestedAction": action,
                "xrefRows": len(target_xrefs),
                "expectedXrefFunctions": sorted(expected_functions),
                "note": rule["note"],
                "missingTokens": missing_tokens,
                "decompile": relative(decompile_file) if decompile_file else None,
            }
        )

    if not seeds:
        failures.append("seed list contained no rows")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-name-confidence-tranche2.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "inputs": {
            "seedList": relative(seed_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
        },
        "targetCount": len(seeds),
        "xrefRows": len(xrefs),
        "actionCounts": dict(action_counts),
        "classificationCounts": dict(classification_counts),
        "targets": targets,
        "failures": failures,
        "whatIsProven": [
            "The second name-confidence queue tranche has read-only decompile and xref context for each selected target.",
            "Each selected target has a public-safe classification and next suggested action.",
            "The tranche separates likely rename candidates from comment candidates and a vtable/context-dependent deferred body.",
        ],
        "notProven": [
            "This does not mutate Ghidra names, signatures, comments, tags, or boundaries.",
            "This does not prove the suggested names or signatures are final.",
            "This does not prove exact source-to-retail identity or runtime behavior.",
        ],
        "privacy": "Report stores repo-relative artifact paths, public addresses, function names, counts, classifications, caller names, and proof boundaries only; raw decompiles and xrefs remain ignored under subagents/.",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--seeds", type=Path, default=DEFAULT_SEEDS)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
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

    report = build_report(
        seed_path=args.seeds,
        decompile_index_path=args.decompile_index,
        decompile_dir=args.decompile_dir,
        xrefs_path=args.xrefs,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("Ghidra name-confidence tranche 2 probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Targets: {report['targetCount']}")
        print(f"Xref rows: {report['xrefRows']}")
        print(f"Action counts: {report['actionCounts']}")
        print(f"Classification counts: {report['classificationCounts']}")
        for failure in report["failures"]:
            print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
