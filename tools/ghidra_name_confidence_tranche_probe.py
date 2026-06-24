#!/usr/bin/env python3
"""Classify a read-only Ghidra name-confidence re-audit tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "name-confidence-tranche1" / "current"
DEFAULT_SEEDS = BASE / "seed_names.json"
DEFAULT_INDEX = BASE / "decompile" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile"
DEFAULT_XREFS = BASE / "xrefs.tsv"
DEFAULT_OUT = BASE / "name-confidence-tranche1.json"

RULES = {
    "0x004026b0": {
        "classification": "vector-length-sqrt-wrapper",
        "action": "renameCandidate",
        "tokens": ["SQRT(", "+ 8", "+ 4"],
        "note": "Computes a 3-float vector length through SQRT; broad xrefs suggest a generic math helper.",
    },
    "0x00402dd0": {
        "classification": "heightfield-shadow-corner-test",
        "action": "commentCandidate",
        "tokens": ["CStaticShadows__SampleShadowHeightBilinear", "iStack_40", "return 1"],
        "note": "Tests object/heightfield corner samples against static shadow height; owner/name needs more context before rename.",
    },
    "0x00403ff0": {
        "classification": "resource-descriptor-array-destroy-wrapper",
        "action": "commentCandidate",
        "tokens": ["CDXLandscape__DestroyArrayWithCallback", "CResourceDescriptor__dtor"],
        "note": "Destroys an array with CResourceDescriptor destructors; CFastVB owner remains questionable.",
    },
    "0x00406d50": {
        "classification": "vector-normalize-sqrt-wrapper",
        "action": "renameCandidate",
        "tokens": ["SQRT(", "_DAT_005d8568 / fVar1", "+ 8"],
        "note": "Normalizes a 3-float vector in place when length is non-zero.",
    },
    "0x0040dcc0": {
        "classification": "transition-state-wrapper",
        "action": "commentCandidate",
        "tokens": ["CMonitor__UpdateFlightWalkerTransitionState", "+ 0x58c", "+ 0x260) == 3"],
        "note": "Clears state 0x58c and conditionally calls the transition-state helper.",
    },
    "0x0040dda0": {
        "classification": "unitai-grid-cooldown-wrapper",
        "action": "commentCandidate",
        "tokens": ["CSquadNormal__GetCellValueAtWorldXY", "+ 0x2e8", "DAT_00672fd0"],
        "note": "Refreshes a UnitAI timestamp when squad grid cells are active.",
    },
    "0x0040e280": {
        "classification": "versioned-dxmem-buffer-reader",
        "action": "signatureCandidate",
        "tokens": ["DXMemBuffer__ReadBytes", "0x3b0", "0x2e"],
        "note": "Version-gated DXMemBuffer deserializer with repeated field/string reads.",
    },
    "0x0040f140": {
        "classification": "global-oid-pool-free-wrapper",
        "action": "signatureCandidate",
        "tokens": ["OID__FreeObject", "DAT_00660250", "DAT_00660200"],
        "note": "Clears the global OID object pool and frees non-null entries.",
    },
    "0x0040f520": {
        "classification": "sptrset-pair-init-wrapper",
        "action": "signatureCandidate",
        "tokens": ["CSPtrSet__Init", "+ 0x40", "+ 0x50"],
        "note": "Initializes paired CSPtrSet fields and clears adjacent state fields.",
    },
    "0x00410670": {
        "classification": "general-volume-energy-drain-wrapper",
        "action": "commentCandidate",
        "tokens": ["CGeneralVolume__ToDoubleIdentity", "+ 0x280", "+ 0x520"],
        "note": "Applies a scaled drain/update to a linked object; exact owner/semantics remain provisional.",
    },
    "0x00410c50": {
        "classification": "monitor-movement-complex-update",
        "action": "defer",
        "tokens": [
            "CMonitor__UpdateTrackedRenderPair",
            "CMonitor__IntegrateMovementAgainstTerrain",
            "CMonitor__UpdateFlightWalkerTransitionState",
        ],
        "note": "Large monitor movement/update body; needs a dedicated source/signature pass before mutation.",
    },
    "0x00411b90": {
        "classification": "burst-dispatch-wrapper",
        "action": "commentCandidate",
        "tokens": ["CGeneralVolume__SpawnBurstFromPresetWithFallback", "+ 0x588", "+ 0x9c"],
        "note": "Walks the list to a selected entry, clears linked owner state, and dispatches the shared burst helper.",
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
    rows: list[dict[str, str]] = []
    for item in data:
        rows.append(
            {
                "address": normalize_address(str(item.get("address", ""))),
                "name": str(item.get("name", "")),
            }
        )
    return rows


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
    xrefs_by_target = Counter(row["target_addr"] for row in xrefs)

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
                "xrefRows": xrefs_by_target[address],
                "note": rule["note"],
                "missingTokens": missing_tokens,
                "decompile": relative(decompile_file) if decompile_file else None,
            }
        )

    if not seeds:
        failures.append("seed list contained no rows")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-name-confidence-tranche.v1",
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
            "The first name-confidence queue tranche has read-only decompile and xref context for each selected target.",
            "Each selected target has a public-safe classification and next suggested action.",
            "This separates rename candidates from comment/signature candidates and deferred complex bodies.",
        ],
        "notProven": [
            "This does not mutate Ghidra names, signatures, comments, tags, or boundaries.",
            "This does not prove the suggested names or signatures are final.",
            "This does not prove runtime behavior or exact source identity.",
        ],
        "privacy": "Report stores repo-relative artifact paths, public addresses, function names, counts, classifications, and proof boundaries only; raw decompiles and xrefs remain ignored under subagents/.",
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
        print("Ghidra name-confidence tranche probe")
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
