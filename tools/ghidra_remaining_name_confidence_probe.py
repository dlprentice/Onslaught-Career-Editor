#!/usr/bin/env python3
"""Classify the remaining Ghidra name-confidence targets after read-only review."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "remaining-name-confidence" / "current"

DEFAULT_METADATA = BASE / "metadata.tsv"
DEFAULT_INDEX = BASE / "decompile" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile"
DEFAULT_XREFS = BASE / "xrefs.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions.tsv"
DEFAULT_CALLER_CONTEXT_INSTRUCTIONS = BASE / "caller_context_instructions.tsv"
DEFAULT_CALLER_INDEX = BASE / "caller_decompile" / "index.tsv"
DEFAULT_CALLER_DECOMPILE_DIR = BASE / "caller_decompile"
DEFAULT_OUT = BASE / "remaining-name-confidence.json"

RULES = {
    "0x00402dd0": {
        "currentName": "CHeightField_Unk_0047eb80__Wrapper_00402dd0",
        "classification": "shadow-heightfield-raw-caller-boundary-deferred",
        "action": "deferRawCallerBoundary",
        "candidateName": "ShadowHeightfield__AnyBoundsCornerAboveSampledHeight",
        "tokens": [
            "CStaticShadows__SampleShadowHeightBilinear",
            "DAT_006fbdfc",
            "return 1",
            "return 0",
        ],
        "expectedFromAddr": "0x004478a3",
        "expectedFromFunctionAddr": "<none>",
        "expectedXrefFunction": "<no_function>",
        "expectedRefType": "UNCONDITIONAL_CALL",
        "callerContextTarget": "0x004478a3",
        "callerContextTokens": ["0x00402dd0", "0x0047eb80", "0x0050ff10"],
        "note": "The body is still a specific shadow/heightfield corner test, but the only reviewed caller remains outside a named function boundary.",
    },
    "0x0040dda0": {
        "currentName": "CUnitAI_Unk_0044c720__Wrapper_0040dda0",
        "classification": "unitai-grid-cooldown-rename-candidate",
        "action": "renameCandidate",
        "candidateName": "CUnitAI__RefreshGridCooldownFromOccupiedCells",
        "tokens": [
            "CSquadNormal__GetCellValueAtWorldXY",
            "DAT_008a9d7c",
            "DAT_008a9d80",
            "0x2e8",
            "DAT_00672fd0",
        ],
        "expectedFromAddr": "0x004862af",
        "expectedFromFunctionAddr": "0x00485d50",
        "expectedXrefFunction": "CExplosionInitThing__RenderObjectiveStatusPanel",
        "expectedRefType": "UNCONDITIONAL_CALL",
        "callerFunction": "0x00485d50",
        "callerTokens": [
            "CUnitAI_Unk_0044c720__Wrapper_0040dda0(*(void **)(param_1 + 0x50))",
            "DAT_00672fd0 - *(float *)(*(int *)(param_1 + 0x50) + 0x2e8)",
        ],
        "note": "The callee and caller now agree that this refreshes a +0x2e8 grid/cooldown timestamp on the object stored at the status-panel owner pointer +0x50.",
    },
    "0x00418090": {
        "currentName": "FindAnimationIndex__Wrapper_00418090",
        "classification": "opening-animation-callback-table-owner-deferred",
        "action": "deferTableOwner",
        "candidateName": "OpeningAnimationStateCallback__StartOpeningIfPending",
        "tokens": [
            "FindAnimationIndex",
            "s_opening_00623ba4",
            "0x254",
            "0x25c",
            "0xf0",
        ],
        "expectedFromAddr": "0x005d9080",
        "expectedFromFunctionAddr": "<none>",
        "expectedXrefFunction": "<no_function>",
        "expectedRefType": "DATA",
        "missingInstructionTarget": "0x005d9080",
        "note": "The opening-animation callback behavior is still visible, but the only reviewed reference is a DATA slot, so table ownership stays deferred.",
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
    if value in {"", "<none>", "<no_function>", "<no_instruction>"}:
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def compact(value: str) -> str:
    return "".join(value.lower().split())


def has_token(text: str, token: str) -> bool:
    return compact(token) in compact(text)


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
        row["address"] = normalize_address(row.get("address", ""))
        row["comment"] = unescape_tsv(row.get("comment", ""))
    return rows


def read_index(path: Path) -> dict[str, dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["address"] = normalize_address(row.get("address", ""))
    return {row["address"]: row for row in rows if row.get("address")}


def read_xrefs(path: Path) -> list[dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["target_addr_norm"] = normalize_address(row.get("target_addr", ""))
        row["from_addr_norm"] = normalize_address(row.get("from_addr", ""))
        row["from_function_addr_norm"] = normalize_address(row.get("from_function_addr", ""))
    return rows


def read_instructions(path: Path) -> list[dict[str, str]]:
    rows = read_tsv(path)
    for row in rows:
        row["target_addr_norm"] = normalize_address(row.get("target_addr", ""))
        row["target_raw_norm"] = normalize_address(row.get("target_raw", ""))
        row["instruction_addr_norm"] = normalize_address(row.get("instruction_addr", ""))
    return rows


def find_decompile_file(decompile_dir: Path, address: str) -> Path | None:
    if not decompile_dir.is_dir():
        return None
    matches = sorted(decompile_dir.glob(f"{normalize_address(address)[2:]}_*.c"))
    return matches[0] if matches else None


def read_text(path: Path | None) -> str:
    if path is None or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def rows_text(rows: list[dict[str, str]]) -> str:
    return "\n".join("\t".join(str(value) for value in row.values()) for row in rows)


def build_report(
    *,
    metadata_path: Path = DEFAULT_METADATA,
    decompile_index_path: Path = DEFAULT_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
    caller_context_instructions_path: Path = DEFAULT_CALLER_CONTEXT_INSTRUCTIONS,
    caller_index_path: Path = DEFAULT_CALLER_INDEX,
    caller_decompile_dir: Path = DEFAULT_CALLER_DECOMPILE_DIR,
) -> dict[str, object]:
    metadata_path = resolve(metadata_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)
    caller_context_instructions_path = resolve(caller_context_instructions_path)
    caller_index_path = resolve(caller_index_path)
    caller_decompile_dir = resolve(caller_decompile_dir)

    failures: list[str] = []
    for label, path in (
        ("metadata export", metadata_path),
        ("decompile index", decompile_index_path),
        ("xref export", xrefs_path),
        ("instruction export", instructions_path),
        ("caller-context instruction export", caller_context_instructions_path),
        ("caller decompile index", caller_index_path),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")
    for label, path in (("decompile dir", decompile_dir), ("caller decompile dir", caller_decompile_dir)):
        if not path.is_dir():
            failures.append(f"missing {label}: {relative(path)}")

    metadata = read_metadata(metadata_path)
    decompile_index = read_index(decompile_index_path)
    caller_index = read_index(caller_index_path)
    xrefs = read_xrefs(xrefs_path)
    instructions = read_instructions(instructions_path)
    caller_context = read_instructions(caller_context_instructions_path)

    xrefs_by_target: dict[str, list[dict[str, str]]] = defaultdict(list)
    instructions_by_target: dict[str, list[dict[str, str]]] = defaultdict(list)
    caller_context_by_target: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in xrefs:
        xrefs_by_target[row["target_addr_norm"]].append(row)
    for row in instructions:
        instructions_by_target[row["target_addr_norm"]].append(row)
    for row in caller_context:
        caller_context_by_target[row["target_addr_norm"]].append(row)

    target_reports: list[dict[str, object]] = []
    action_counts: Counter[str] = Counter()
    classification_counts: Counter[str] = Counter()
    seen: set[str] = set()

    for row in metadata:
        address = row["address"]
        seen.add(address)
        rule = RULES.get(address)
        if rule is None:
            failures.append(f"{address} has no remaining-name-confidence rule")
            continue

        name = row.get("name", "")
        signature = row.get("signature", "")
        comment = row.get("comment", "")
        if row.get("status") != "OK":
            failures.append(f"{address}: metadata status is not OK")
        if name != rule["currentName"]:
            failures.append(f"{address}: expected current name {rule['currentName']}, found {name}")
        if not comment:
            failures.append(f"{address}: missing metadata comment")

        index_row = decompile_index.get(address)
        if not index_row or index_row.get("status") != "OK":
            failures.append(f"{address}: missing OK decompile index row")
        elif index_row.get("name", "") != name:
            failures.append(f"{address}: metadata/index name mismatch")

        decompile_file = find_decompile_file(decompile_dir, address)
        decompile_text = read_text(decompile_file)
        if not decompile_text:
            failures.append(f"{address}: missing decompile text")
        missing_tokens = [token for token in rule["tokens"] if not has_token(decompile_text, token)]
        if missing_tokens:
            failures.append(f"{address}: missing expected decompile tokens: {', '.join(missing_tokens)}")

        target_xrefs = xrefs_by_target[address]
        expected_from = normalize_address(str(rule["expectedFromAddr"]))
        expected_from_function_addr = normalize_address(str(rule["expectedFromFunctionAddr"]))
        expected_xref_function = str(rule["expectedXrefFunction"])
        expected_ref_type = str(rule["expectedRefType"])
        expected_xrefs = [
            xref
            for xref in target_xrefs
            if xref.get("from_addr_norm") == expected_from
            and xref.get("from_function_addr_norm") == expected_from_function_addr
            and xref.get("from_function", "") == expected_xref_function
            and xref.get("ref_type", "") == expected_ref_type
        ]
        if not target_xrefs:
            failures.append(f"{address}: missing xref rows")
        elif not expected_xrefs:
            failures.append(
                f"{address}: missing expected xref from {expected_from} / {expected_xref_function} / {expected_ref_type}"
            )

        target_instructions = instructions_by_target[address]
        if not target_instructions:
            failures.append(f"{address}: missing target instruction rows")

        extra_context: dict[str, object] = {}
        action = str(rule["action"])
        if action == "deferRawCallerBoundary":
            context_target = normalize_address(str(rule["callerContextTarget"]))
            context_rows = caller_context_by_target[context_target]
            context_text = rows_text(context_rows)
            if not context_rows:
                failures.append(f"{address}: missing raw caller context rows for {context_target}")
            if "<no_function>" not in context_text:
                failures.append(f"{address}: raw caller context no longer shows <no_function>")
            missing_context_tokens = [
                token for token in rule["callerContextTokens"] if not has_token(context_text, token)
            ]
            if missing_context_tokens:
                failures.append(
                    f"{address}: raw caller context missing tokens: {', '.join(missing_context_tokens)}"
                )
            extra_context = {
                "callerContextTarget": context_target,
                "callerContextRows": len(context_rows),
                "callerContextTokens": list(rule["callerContextTokens"]),
            }
        elif action == "renameCandidate":
            caller_function = normalize_address(str(rule["callerFunction"]))
            caller_row = caller_index.get(caller_function)
            caller_decompile_file = find_decompile_file(caller_decompile_dir, caller_function)
            caller_text = read_text(caller_decompile_file)
            if not caller_row or caller_row.get("status") != "OK":
                failures.append(f"{address}: missing OK caller decompile index row for {caller_function}")
            missing_caller_tokens = [token for token in rule["callerTokens"] if not has_token(caller_text, token)]
            if missing_caller_tokens:
                failures.append(
                    f"{address}: caller decompile missing object-pointer/timestamp evidence tokens"
                )
            extra_context = {
                "callerFunction": caller_function,
                "callerFunctionName": caller_row.get("name") if caller_row else None,
                "callerDecompile": relative(caller_decompile_file),
                "callerEvidenceTokenCount": len(rule["callerTokens"]) - len(missing_caller_tokens),
            }
        elif action == "deferTableOwner":
            missing_target = normalize_address(str(rule["missingInstructionTarget"]))
            context_rows = caller_context_by_target[missing_target]
            missing_rows = [
                context_row
                for context_row in context_rows
                if context_row.get("role") == "MISSING"
                and context_row.get("function_name") == "<no_instruction>"
            ]
            if not missing_rows:
                failures.append(f"{address}: table DATA slot {missing_target} no longer has missing-instruction context")
            extra_context = {
                "tableSlot": missing_target,
                "tableSlotInstructionRows": len(context_rows),
                "tableSlotMissingInstructionRows": len(missing_rows),
            }

        classification = str(rule["classification"])
        action_counts[action] += 1
        classification_counts[classification] += 1
        target_reports.append(
            {
                "address": address,
                "currentName": name,
                "signature": signature,
                "classification": classification,
                "suggestedAction": action,
                "candidateName": rule["candidateName"],
                "expectedXrefFunction": expected_xref_function,
                "expectedRefType": expected_ref_type,
                "xrefRows": len(target_xrefs),
                "instructionRows": len(target_instructions),
                "decompile": relative(decompile_file),
                "note": rule["note"],
                "missingDecompileTokens": missing_tokens,
                **extra_context,
            }
        )

    for address in RULES:
        if address not in seen:
            failures.append(f"{address} missing from metadata export")
    extra_addresses = sorted(seen - set(RULES))
    if extra_addresses:
        failures.append(f"metadata export has unexpected addresses: {', '.join(extra_addresses)}")
    if not metadata:
        failures.append("metadata export contained no rows")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-remaining-name-confidence.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "inputs": {
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
            "callerContextInstructions": relative(caller_context_instructions_path),
            "callerDecompileIndex": relative(caller_index_path),
            "callerDecompileDir": relative(caller_decompile_dir),
        },
        "targetCount": len(metadata),
        "expectedTargetCount": len(RULES),
        "xrefRows": len(xrefs),
        "instructionRows": len(instructions),
        "callerContextInstructionRows": len(caller_context),
        "callerDecompileIndexRows": len(caller_index),
        "actionCounts": dict(action_counts),
        "classificationCounts": dict(classification_counts),
        "targets": target_reports,
        "failures": failures,
        "whatIsProven": [
            "The three remaining name-confidence targets have current read-only metadata, decompile, xref, instruction, and caller/table context exports.",
            "0x0040dda0 has enough read-only caller/callee evidence to become a rename candidate for CUnitAI__RefreshGridCooldownFromOccupiedCells.",
            "0x00402dd0 remains blocked by a raw/no-function caller boundary, and 0x00418090 remains blocked by DATA table ownership.",
        ],
        "notProven": [
            "This does not mutate Ghidra names, comments, signatures, tags, types, locals, or function boundaries.",
            "This does not prove the proposed 0x0040dda0 rename is already saved in Ghidra.",
            "This does not prove exact source-to-retail identity or runtime behavior.",
        ],
        "privacy": "Report stores repo-relative artifact paths, public addresses, names, counts, classifications, candidate labels, and proof boundaries only; raw exports remain ignored under subagents/.",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--instructions", type=Path, default=DEFAULT_INSTRUCTIONS)
    parser.add_argument("--caller-context-instructions", type=Path, default=DEFAULT_CALLER_CONTEXT_INSTRUCTIONS)
    parser.add_argument("--caller-index", type=Path, default=DEFAULT_CALLER_INDEX)
    parser.add_argument("--caller-decompile-dir", type=Path, default=DEFAULT_CALLER_DECOMPILE_DIR)
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
        metadata_path=args.metadata,
        decompile_index_path=args.decompile_index,
        decompile_dir=args.decompile_dir,
        xrefs_path=args.xrefs,
        instructions_path=args.instructions,
        caller_context_instructions_path=args.caller_context_instructions,
        caller_index_path=args.caller_index,
        caller_decompile_dir=args.caller_decompile_dir,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("Ghidra remaining name-confidence probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Targets: {report['targetCount']} / {report['expectedTargetCount']}")
        print(f"Action counts: {json.dumps(report['actionCounts'], sort_keys=True)}")
        for failure in report["failures"]:
            print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
