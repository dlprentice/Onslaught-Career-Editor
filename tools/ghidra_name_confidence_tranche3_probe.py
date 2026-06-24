#!/usr/bin/env python3
"""Classify the third read-only Ghidra name-confidence re-audit tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "name-confidence-tranche3" / "current"
DEFAULT_SEEDS = BASE / "seed_names.json"
DEFAULT_INDEX = BASE / "decompile" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile"
DEFAULT_XREFS = BASE / "xrefs.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions.tsv"
DEFAULT_OUT = BASE / "name-confidence-tranche3.json"

RULES = {
    "0x0050b010": {
        "classification": "world-occupancy-grid-add-wrapper",
        "action": "renameCandidate",
        "tokens": ["CWorld__AddUnitToOccupancyGridAndRebuildShadows", "param_1"],
        "expectedXrefRows": 6,
        "expectedXrefFunctions": [
            "CUnitAI__PlayWingFoldedAnimationAndSetState3",
            "CFeature__VFunc_09_0044ca30",
            "CWarspiteDome__Init",
        ],
        "note": "Thin stdcall wrapper into the now-named CWorld add-to-occupancy-grid/shadow rebuild helper; the old dispatch-helper label is weaker than the callee evidence.",
    },
    "0x0050b020": {
        "classification": "world-occupancy-grid-remove-wrapper",
        "action": "renameCandidate",
        "tokens": ["CWorld__RemoveUnitFromOccupancyGrid", "param_1"],
        "expectedXrefRows": 6,
        "expectedXrefFunctions": [
            "CNamedMesh__VFunc_02_004bc050",
            "CCannon__Destructor",
            "CDropship__VFunc_02_00447100",
        ],
        "note": "Thin stdcall wrapper into the now-named CWorld occupancy-grid removal helper; destructor/vfunc callers support a lifecycle detach role.",
    },
    "0x0053f7d0": {
        "classification": "bitmap-font-slot-string-init",
        "action": "ownerCorrectionCandidate",
        "tokens": ["StringScratch__CopyRotating4K", "+ 0x54", "+ 0x58", "+ 0x170", "+ 0x15c"],
        "expectedXrefFunctions": ["PCPlatform__LoadFonts"],
        "note": "Copies a font/name string into a CDXBitmapFont-like object and initializes font-slot fields; the current CWaypoint owner is likely stale.",
    },
    "0x0055e412": {
        "classification": "texture-load-fallback-no-flags-wrapper",
        "action": "renameCandidate",
        "tokens": ["CDXTexture__LoadFromPathWithFallbackExtensions", "(int)&stack0x0000000c", ",0"],
        "expectedXrefFunctions": ["FatalError__ExitProcess"],
        "note": "Forwards to the texture path/fallback loader with a stack-local option pointer and fixed flags zero; the old CRT helper label now hides the app texture behavior.",
    },
    "0x0055e45f": {
        "classification": "crt-open-file-mode-auto-unlock-wrapper",
        "action": "renameCandidate",
        "tokens": ["CRT__AcquireFileStreamSlot", "CRT__OpenFileByModeString", "CRT__UnlockRouteByAddress"],
        "expectedXrefFunctions": ["fopen"],
        "note": "Acquires a CRT file-stream slot, opens by mode string, then unlocks by routed address; the name can now use the resolved open-file callee instead of an address helper label.",
    },
    "0x0056d21c": {
        "classification": "ctype-digit-mask-return-wrapper",
        "action": "renameCandidate",
        "tokens": ["CRT__IsCharTypeMaskOrLeadByte_0056d22d", "param_1,0,4"],
        "instructionTokens": [
            ("CALL", "0x0056d22d"),
            ("ADD", "ESP, 0xc"),
            ("RET", ""),
        ],
        "expectedXrefFunctions": ["CRT__ParseCommandLineToken"],
        "note": "Pushes ctype digit mask 4, calls the char-type helper, stack-adjusts, and returns with EAX preserved; the current void signature is likely stale.",
    },
}


def relative(path: Path | None) -> str | None:
    if path is None:
        return None
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


def read_instructions(path: Path) -> list[dict[str, str]]:
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


def has_instruction_token(rows: list[dict[str, str]], mnemonic: str, operand_token: str) -> bool:
    for row in rows:
        if row.get("mnemonic", "") != mnemonic:
            continue
        if operand_token and operand_token not in row.get("operands", ""):
            continue
        return True
    return False


def build_report(
    *,
    seed_path: Path = DEFAULT_SEEDS,
    decompile_index_path: Path = DEFAULT_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
) -> dict[str, object]:
    seed_path = resolve(seed_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)

    failures: list[str] = []
    for label, path in (
        ("seed list", seed_path),
        ("decompile index", decompile_index_path),
        ("decompile dir", decompile_dir),
        ("xref export", xrefs_path),
        ("instruction export", instructions_path),
    ):
        if label == "decompile dir":
            if not path.is_dir():
                failures.append(f"missing {label}: {relative(path)}")
        elif not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")

    seeds = read_seed_rows(seed_path)
    index = read_index(decompile_index_path)
    xrefs = read_xrefs(xrefs_path)
    instructions = read_instructions(instructions_path)
    xrefs_by_target: dict[str, list[dict[str, str]]] = defaultdict(list)
    instructions_by_target: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in xrefs:
        xrefs_by_target[row["target_addr"]].append(row)
    for row in instructions:
        instructions_by_target[row["target_addr"]].append(row)

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

        target_instructions = instructions_by_target[address]
        missing_instruction_tokens = [
            f"{mnemonic} {operand}".strip()
            for mnemonic, operand in rule.get("instructionTokens", [])
            if not has_instruction_token(target_instructions, mnemonic, operand)
        ]
        if missing_instruction_tokens:
            failures.append(
                f"{address} missing expected instruction context: {', '.join(missing_instruction_tokens)}"
            )

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
                "instructionRows": len(target_instructions),
                "expectedXrefFunctions": sorted(expected_functions),
                "note": rule["note"],
                "missingTokens": missing_tokens,
                "missingInstructionTokens": missing_instruction_tokens,
                "decompile": relative(decompile_file),
            }
        )

    if not seeds:
        failures.append("seed list contained no rows")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-name-confidence-tranche3.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "inputs": {
            "seedList": relative(seed_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
        },
        "targetCount": len(seeds),
        "xrefRows": len(xrefs),
        "instructionRows": len(instructions),
        "actionCounts": dict(action_counts),
        "classificationCounts": dict(classification_counts),
        "targets": targets,
        "failures": failures,
        "whatIsProven": [
            "The third name-confidence queue tranche has read-only decompile, xref, and instruction context for each selected target.",
            "Each selected target has a public-safe classification and next suggested action.",
            "The tranche identifies multiple old helper/wrapper labels that can be improved in future mutation waves after dry/apply/read-back gates.",
        ],
        "notProven": [
            "This does not mutate Ghidra names, signatures, comments, tags, or function boundaries.",
            "This does not prove the suggested names or signatures are final.",
            "This does not prove exact source-to-retail identity or runtime behavior.",
        ],
        "privacy": "Report stores repo-relative artifact paths, public addresses, function names, counts, classifications, caller names, and proof boundaries only; raw decompiles, instructions, and xrefs remain ignored under subagents/.",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--seeds", type=Path, default=DEFAULT_SEEDS)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--instructions", type=Path, default=DEFAULT_INSTRUCTIONS)
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
        instructions_path=args.instructions,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("Ghidra name-confidence tranche 3 probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Targets: {report['targetCount']}")
        print(f"Xref rows: {report['xrefRows']}")
        print(f"Instruction rows: {report['instructionRows']}")
        print(f"Action counts: {report['actionCounts']}")
        print(f"Classification counts: {report['classificationCounts']}")
        for failure in report["failures"]:
            print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
