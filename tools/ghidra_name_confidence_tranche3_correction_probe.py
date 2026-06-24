#!/usr/bin/env python3
"""Verify the third Ghidra name-confidence correction pass.

The headless mutation commands for this wave were run directly through
analyzeHeadless after the Windows shell wrapper failed before Ghidra launch.
This probe therefore validates the durable inputs and read-back artifacts
instead of requiring terminal-only dry/apply logs.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "name-confidence-tranche3-correction" / "current"
DEFAULT_RENAME_MAP = BASE / "rename_map_tranche3_corrections.txt"
DEFAULT_COMMENTS = BASE / "comments_after_rename.tsv"
DEFAULT_METADATA = BASE / "metadata_readback.tsv"
DEFAULT_DECOMPILE_INDEX = BASE / "decompile_readback" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_readback"
DEFAULT_XREFS = BASE / "xrefs_readback.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_readback.tsv"
DEFAULT_QUEUE_REPORT = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
DEFAULT_OUT = BASE / "name-confidence-tranche3-correction.json"

EXPECTED_QUEUE_SIGNALS = {
    "commentlessFunctionCount": 5495,
    "undefinedSignatureCount": 2087,
    "paramSignatureCount": 2563,
    "uncertainOwnerNameCount": 9,
    "helperAddressNameCount": 0,
    "wrapperAddressNameCount": 16,
}

TARGETS = [
    {
        "address": "0x0050b010",
        "oldName": "CWorld__DispatchHelper_004bc480",
        "name": "CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk",
        "classification": "world-occupancy-grid-add-wrapper-renamed",
        "commentTokens": [
            "Proof boundary 2026-05-09 Wave 259",
            "CWorld__AddUnitToOccupancyGridAndRebuildShadows",
            "remain open",
        ],
        "decompileTokens": ["CWorld__AddUnitToOccupancyGridAndRebuildShadows", "param_1"],
        "expectedXrefRows": 5,
        "expectedXrefFunctions": [
            "CUnitAI__PlayWingFoldedAnimationAndSetState3",
            "CFeature__VFunc_09_0044ca30",
            "CWarspiteDome__Init",
            "CCannon__Init",
            "CNamedMesh__VFunc_09_004bbcd0",
        ],
        "note": "Thin wrapper into the named CWorld occupancy-grid add/shadow rebuild helper.",
    },
    {
        "address": "0x0050b020",
        "oldName": "CWorld__DispatchHelper_004bc3e0",
        "name": "CWorld__RemoveUnitFromOccupancyGrid_Thunk",
        "classification": "world-occupancy-grid-remove-wrapper-renamed",
        "commentTokens": [
            "Proof boundary 2026-05-09 Wave 259",
            "CWorld__RemoveUnitFromOccupancyGrid",
            "remain open",
        ],
        "decompileTokens": ["CWorld__RemoveUnitFromOccupancyGrid", "param_1"],
        "expectedXrefRows": 4,
        "expectedXrefFunctions": [
            "CCannon__Destructor",
            "CNamedMesh__VFunc_02_004bc050",
            "CDropship__VFunc_02_00447100",
            "CFeature__VFunc_02_0044cbe0",
        ],
        "note": "Thin wrapper into the named CWorld occupancy-grid removal helper.",
    },
    {
        "address": "0x0053f7d0",
        "oldName": "CWaypoint_Unk_004f7cd0__Wrapper_0053f7d0",
        "name": "CDXBitmapFont__InitNamedFontSlot",
        "classification": "bitmap-font-slot-owner-correction-renamed",
        "commentTokens": [
            "Proof boundary 2026-05-09 Wave 259",
            "PCPlatform__LoadFonts",
            "CDXBitmapFont ownership",
            "remain open",
        ],
        "decompileTokens": ["StringScratch__CopyRotating4K", "+ 0x54", "+ 0x58", "+ 0x170", "+ 0x15c"],
        "expectedXrefRows": 1,
        "expectedXrefFunctions": ["PCPlatform__LoadFonts"],
        "note": "Corrects a stale CWaypoint owner label to a behavior-backed bitmap-font slot initializer.",
    },
    {
        "address": "0x0055e412",
        "oldName": "CRT__CallHelper_00564a0b_NoFlags",
        "name": "CDXTexture__LoadPathFallbackNoFlags_Thunk",
        "classification": "texture-load-fallback-no-flags-renamed",
        "commentTokens": [
            "Proof boundary 2026-05-09 Wave 259",
            "CDXTexture__LoadFromPathWithFallbackExtensions",
            "fixed no-flags behavior",
            "remain open",
        ],
        "decompileTokens": ["CDXTexture__LoadFromPathWithFallbackExtensions", "(int)&stack0x0000000c", ",0"],
        "expectedXrefRows": 1,
        "expectedXrefFunctions": ["FatalError__ExitProcess"],
        "note": "Replaces the generic CRT helper name with texture-loader behavior while keeping signature/source identity open.",
    },
    {
        "address": "0x0055e45f",
        "oldName": "CRT__CallHelper_00564c09_WithAutoUnlock",
        "name": "CRT__OpenFileByModeString_AutoUnlock",
        "classification": "crt-open-file-auto-unlock-renamed",
        "commentTokens": [
            "Proof boundary 2026-05-09 Wave 259",
            "CRT__OpenFileByModeString",
            "routed unlock helper",
            "remain open",
        ],
        "decompileTokens": ["CRT__AcquireFileStreamSlot", "CRT__OpenFileByModeString", "CRT__UnlockRouteByAddress"],
        "expectedXrefRows": 1,
        "expectedXrefFunctions": ["fopen"],
        "note": "Names the CRT file-open wrapper by its resolved open-by-mode behavior and auto-unlock path.",
    },
    {
        "address": "0x0056d21c",
        "oldName": "CRT__IsDigit_Wrapper_0056d21c",
        "name": "CRT__IsDigitCharTypeMask_Thunk",
        "classification": "ctype-digit-mask-wrapper-renamed-signature-still-open",
        "commentTokens": [
            "Proof boundary 2026-05-09 Wave 259",
            "CRT__IsCharTypeMaskOrLeadByte_0056d22d",
            "Current saved signature still needs review",
            "remain open",
        ],
        "decompileTokens": ["CRT__IsCharTypeMaskOrLeadByte_0056d22d", "param_1,0,4"],
        "instructionTokens": [("CALL", "0x0056d22d"), ("ADD", "ESP, 0xc"), ("RET", "")],
        "expectedXrefRows": 1,
        "expectedXrefFunctions": ["CRT__ParseCommandLineToken"],
        "note": "Names the digit-mask ctype thunk while explicitly preserving the stale-signature caveat.",
    },
]


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


def read_text(path: Path | None) -> str:
    if path is None or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def unescape_tsv(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_metadata(path: Path) -> list[dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["comment"] = unescape_tsv(row.get("comment", ""))
    return rows


def read_comments(path: Path) -> dict[str, dict[str, str]]:
    rows = read_tsv(path)
    comments: dict[str, dict[str, str]] = {}
    for row in rows:
        address = normalize_address(row.get("address", ""))
        if address == "0x00000000":
            continue
        comments[address] = {
            "name": row.get("name") or row.get("expected_name", ""),
            "comment": unescape_tsv(row.get("comment", "")),
        }
    return comments


def read_rename_map(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    rows: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) != 2:
            rows[f"bad:{len(rows)}"] = line
            continue
        rows[normalize_address(parts[0])] = parts[1]
    return rows


def read_xrefs(path: Path) -> list[dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["target_addr"] = normalize_address(row.get("target_addr", ""))
    return rows


def read_instructions(path: Path) -> list[dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["target_addr"] = normalize_address(row.get("target_addr", ""))
    return rows


def read_queue_report(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def find_row(rows: list[dict[str, str]], address_key: str, address: str) -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(address_key, "")) == wanted:
            return row
    return None


def find_decompile_file(decompile_dir: Path, address: str) -> Path | None:
    if not decompile_dir.is_dir():
        return None
    needle = normalize_address(address)[2:]
    matches = sorted(decompile_dir.glob(f"{needle}_*.c"))
    return matches[0] if matches else None


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
    rename_map_path: Path = DEFAULT_RENAME_MAP,
    comments_path: Path = DEFAULT_COMMENTS,
    metadata_path: Path = DEFAULT_METADATA,
    decompile_index_path: Path = DEFAULT_DECOMPILE_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
    queue_report_path: Path = DEFAULT_QUEUE_REPORT,
) -> dict[str, object]:
    rename_map_path = resolve(rename_map_path)
    comments_path = resolve(comments_path)
    metadata_path = resolve(metadata_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)
    queue_report_path = resolve(queue_report_path)

    failures: list[str] = []
    for label, path in (
        ("rename map", rename_map_path),
        ("comment TSV", comments_path),
        ("metadata read-back", metadata_path),
        ("decompile index", decompile_index_path),
        ("xref read-back", xrefs_path),
        ("instruction read-back", instructions_path),
        ("static re-audit queue report", queue_report_path),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")
    if not decompile_dir.is_dir():
        failures.append(f"missing decompile dir: {relative(decompile_dir)}")

    rename_map = read_rename_map(rename_map_path)
    comment_rows = read_comments(comments_path)
    metadata_rows = read_metadata(metadata_path)
    index_rows = read_tsv(decompile_index_path)
    xrefs = read_xrefs(xrefs_path)
    instructions = read_instructions(instructions_path)
    queue_report = read_queue_report(queue_report_path)

    bad_rows = [value for key, value in rename_map.items() if key.startswith("bad:")]
    for bad_row in bad_rows:
        failures.append(f"bad rename-map row: {bad_row}")

    xrefs_by_target: dict[str, list[dict[str, str]]] = defaultdict(list)
    instructions_by_target: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in xrefs:
        xrefs_by_target[row["target_addr"]].append(row)
    for row in instructions:
        instructions_by_target[row["target_addr"]].append(row)

    readback: dict[str, object] = {}
    all_present = True
    for target in TARGETS:
        address = target["address"]
        normalized = normalize_address(address)
        name = target["name"]

        if rename_map.get(normalized) != name:
            failures.append(f"rename map missing expected final name for {address}")

        comment_row = comment_rows.get(normalized)
        if comment_row is None:
            failures.append(f"comment TSV missing {address}")
        elif comment_row.get("name") != name:
            failures.append(f"comment TSV for {address} has unexpected name {comment_row.get('name')}")

        metadata_row = find_row(metadata_rows, "address", address)
        index_row = find_row(index_rows, "address", address)
        decompile_file = find_decompile_file(decompile_dir, address)
        decompile_text = read_text(decompile_file)
        target_xrefs = xrefs_by_target[normalized]
        target_instructions = instructions_by_target[normalized]

        comment = metadata_row.get("comment", "") if metadata_row else ""
        comment_tokens_present = all(token in comment for token in target["commentTokens"])
        metadata_ok = bool(
            metadata_row
            and metadata_row.get("name") == name
            and metadata_row.get("status") == "OK"
            and comment_tokens_present
        )
        if not metadata_ok:
            failures.append(f"metadata read-back for {address} lacks expected name/status/comment tokens")

        index_ok = bool(index_row and index_row.get("name") == name and index_row.get("status") == "OK")
        if not index_ok:
            failures.append(f"decompile index for {address} lacks expected name/status")

        decompile_tokens_present = bool(decompile_text) and all(
            token in decompile_text for token in target["decompileTokens"]
        )
        if not decompile_tokens_present:
            failures.append(f"decompile read-back for {address} lacks expected behavior tokens")

        xref_ok = True
        expected_rows = int(target.get("expectedXrefRows", 0))
        if len(target_xrefs) < expected_rows:
            failures.append(f"{address} expected xref rows >= {expected_rows}, found {len(target_xrefs)}")
            xref_ok = False
        expected_functions = set(target.get("expectedXrefFunctions", []))
        if expected_functions:
            observed = {row.get("from_function", "") for row in target_xrefs}
            missing = sorted(expected_functions - observed)
            if missing:
                failures.append(f"{address} missing expected xref context: {', '.join(missing)}")
                xref_ok = False

        missing_instruction_tokens = [
            f"{mnemonic} {operand}".strip()
            for mnemonic, operand in target.get("instructionTokens", [])
            if not has_instruction_token(target_instructions, mnemonic, operand)
        ]
        instruction_ok = not missing_instruction_tokens
        if missing_instruction_tokens:
            failures.append(
                f"{address} missing expected instruction context: {', '.join(missing_instruction_tokens)}"
            )

        target_ok = metadata_ok and index_ok and decompile_tokens_present and xref_ok and instruction_ok
        all_present = all_present and target_ok
        readback[address] = {
            "oldName": target["oldName"],
            "name": metadata_row.get("name") if metadata_row else None,
            "status": metadata_row.get("status") if metadata_row else None,
            "signature": metadata_row.get("signature") if metadata_row else None,
            "classification": target["classification"],
            "commentTokensPresent": comment_tokens_present,
            "decompileTokensPresent": decompile_tokens_present,
            "xrefRows": len(target_xrefs),
            "instructionTokensPresent": instruction_ok,
            "decompile": relative(decompile_file),
            "note": target["note"],
        }

    queue_signals = queue_report.get("qualitySignals", {}) if isinstance(queue_report, dict) else {}
    if queue_report.get("status") != "PASS":
        failures.append("static re-audit queue report is not PASS")
    if queue_report.get("totalFunctions") != 5863:
        failures.append("static re-audit queue totalFunctions is not the expected 5863")
    for key, expected in EXPECTED_QUEUE_SIGNALS.items():
        if queue_signals.get(key) != expected:
            failures.append(f"static re-audit queue {key} expected {expected}, found {queue_signals.get(key)}")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-name-confidence-tranche3-correction.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "candidateClassification": "tranche3-corrections-renamed-commented"
        if status == "PASS"
        else "tranche3-correction-readback-blocked",
        "targetCount": len(TARGETS),
        "targets": [
            {
                "address": target["address"],
                "oldName": target["oldName"],
                "name": target["name"],
                "classification": target["classification"],
                "note": target["note"],
            }
            for target in TARGETS
        ],
        "mutationAccounting": {
            "renameMap": relative(rename_map_path),
            "commentTsv": relative(comments_path),
            "dryApplyLogsRequired": False,
            "reason": "Direct analyzeHeadless dry/apply output was terminal-only after the Windows wrapper failed before launching Ghidra.",
        },
        "readback": {
            "allNamesCommentsAndContextPresent": all_present,
            "functions": readback,
            "xrefRows": len(xrefs),
            "instructionRows": len(instructions),
        },
        "queue": {
            "status": queue_report.get("status") if isinstance(queue_report, dict) else None,
            "totalFunctions": queue_report.get("totalFunctions") if isinstance(queue_report, dict) else None,
            "qualitySignals": {key: queue_signals.get(key) for key in EXPECTED_QUEUE_SIGNALS},
        },
        "inputs": {
            "renameMap": relative(rename_map_path),
            "comments": relative(comments_path),
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
            "queueReport": relative(queue_report_path),
        },
        "failures": failures,
        "whatIsProven": [
            "The saved Ghidra project now has conservative names for all six third-tranche name-confidence targets.",
            "Read-back metadata confirms proof-boundary comments for all six renamed/commented functions.",
            "Decompile, xref, and instruction read-backs preserve the behavior/caller context that justified the correction pass.",
            "The follow-up queue snapshot records 368 commented functions, 5495 commentless functions, 9 uncertain-owner names, and 16 address-suffixed wrappers.",
        ],
        "notProven": [
            "This does not change signatures, parameter names, local names, tags, structures, or data types.",
            "The saved void signature for CRT__IsDigitCharTypeMask_Thunk still needs review.",
            "This does not prove exact source-to-retail identity or runtime behavior.",
            "This does not complete the broader Ghidra static re-audit queue.",
        ],
        "privacy": "Report stores repo-relative artifact paths, public addresses, function names, command summaries, counts, and proof boundaries only; raw Ghidra exports remain ignored under subagents/.",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--rename-map", type=Path, default=DEFAULT_RENAME_MAP)
    parser.add_argument("--comments", type=Path, default=DEFAULT_COMMENTS)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_DECOMPILE_INDEX)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--instructions", type=Path, default=DEFAULT_INSTRUCTIONS)
    parser.add_argument("--queue-report", type=Path, default=DEFAULT_QUEUE_REPORT)
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
        rename_map_path=args.rename_map,
        comments_path=args.comments,
        metadata_path=args.metadata,
        decompile_index_path=args.decompile_index,
        decompile_dir=args.decompile_dir,
        xrefs_path=args.xrefs,
        instructions_path=args.instructions,
        queue_report_path=args.queue_report,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("Ghidra name-confidence tranche 3 correction probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Classification: {report['candidateClassification']}")
        print(f"Targets: {report['targetCount']}")
        print(f"Xref rows: {report['readback']['xrefRows']}")
        print(f"Instruction rows: {report['readback']['instructionRows']}")
        print(f"All names/comments/context present: {report['readback']['allNamesCommentsAndContextPresent']}")
        print(f"Queue: {report['queue']}")
        if report["failures"]:
            print("Failures:")
            for failure in report["failures"]:
                print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
