#!/usr/bin/env python3
"""Validate the saved Ghidra UnitAI activation/boundary correction wave."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "unitai-activation-wave325" / "current"

COMMON_TAGS = ["static-reaudit", "unitai-activation-wave325", "unitai-system", "signature-hardened"]

TARGETS = {
    "0x00428710": {
        "name": "CUnitAI__GetRenderPosFromActorOrCache",
        "signature": "void * __thiscall CUnitAI__GetRenderPosFromActorOrCache(void * this, void * outRenderPos, void * unused)",
        "comment": ["CActor__GetRenderPos", "cached component position", "runtime render behavior", "remain unproven"],
        "tags": COMMON_TAGS,
    },
    "0x00428770": {
        "name": "CUnitAI__GetRenderOrientationFromActorOrCache",
        "signature": "void * __thiscall CUnitAI__GetRenderOrientationFromActorOrCache(void * this, void * outRenderOrientation, void * unused)",
        "comment": ["CActor__GetRenderOrientation", "cached orientation matrix", "runtime render behavior", "remain unproven"],
        "tags": COMMON_TAGS,
    },
    "0x00428800": {
        "name": "CUnitAI__HandleTriggerEventAndMoveToOffset",
        "signature": "bool __fastcall CUnitAI__HandleTriggerEventAndMoveToOffset(void * this)",
        "comment": ["marks the unit destroyed", "normalized offset", "runtime trigger/movement behavior", "remain unproven"],
        "tags": COMMON_TAGS,
    },
    "0x004289b0": {
        "name": "CUnitAI__AdvanceActivationAnimationState",
        "signature": "bool __fastcall CUnitAI__AdvanceActivationAnimationState(void * this)",
        "comment": ["Hit", "Activate", "Activated", "Deactivated", "runtime animation behavior", "remain unproven"],
        "tags": COMMON_TAGS,
    },
    "0x00428b50": {
        "name": "CUnit__SetReaderAndComputeRelativeYaw",
        "signature": "void __thiscall CUnit__SetReaderAndComputeRelativeYaw(void * this, void * reader, void * readerContext, int unusedMode)",
        "comment": ["CUnit active-reader setter", "relative yaw", "third observed stack argument is unused", "remain unproven"],
        "tags": COMMON_TAGS,
    },
    "0x00428bc0": {
        "name": "CUnitAI__GetTargetHeadingWithOffset",
        "signature": "double __fastcall CUnitAI__GetTargetHeadingWithOffset(void * this)",
        "comment": ["active reader heading", "relative-yaw offset", "zero heading constant", "remain unproven"],
        "tags": COMMON_TAGS,
    },
    "0x00428c70": {
        "name": "CUnitAI__RunSharedStepAndMaybeTriggerFlag4Action",
        "signature": "void __fastcall CUnitAI__RunSharedStepAndMaybeTriggerFlag4Action(void * this)",
        "comment": ["resets field D0", "flag bit 4", "runtime AI-step behavior", "remain unproven"],
        "tags": COMMON_TAGS,
    },
    "0x00428cb0": {
        "name": "CUnitAI__PlayHitAnimationAndSetFlag",
        "signature": "void __fastcall CUnitAI__PlayHitAnimationAndSetFlag(void * this)",
        "comment": ["Hit animation token", "+0x2bc", "prior ExplosionInitThing owner", "remain unproven"],
        "tags": COMMON_TAGS + ["owner-corrected"],
    },
    "0x00428cf0": {
        "name": "CUnitAI__ForwardCommandToAttachedNodeThenDispatch",
        "signature": "void __thiscall CUnitAI__ForwardCommandToAttachedNodeThenDispatch(void * this, int command, int unusedStackParam)",
        "comment": ["active reader vtable slot 0x1ac", "EDI-sourced score", "caller-context", "remain unproven"],
        "tags": COMMON_TAGS,
    },
    "0x00428d50": {
        "name": "CUnitAI__PlayActivateAnimationOrFinalizeActivated",
        "signature": "void __fastcall CUnitAI__PlayActivateAnimationOrFinalizeActivated(void * this)",
        "comment": ["Activate animation token", "finalizes activation", "runtime animation behavior", "remain unproven"],
        "tags": COMMON_TAGS,
    },
    "0x00428e80": {
        "name": "CComponentAI__ClearReaderIfTargetDestroyedThenForward",
        "signature": "void __fastcall CComponentAI__ClearReaderIfTargetDestroyedThenForward(void * this)",
        "comment": ["CComponentBomberAI", "CFenrirMainGunAI", "flag bit 4", "remain unproven"],
        "tags": COMMON_TAGS + ["owner-corrected"],
    },
    "0x00429270": {
        "name": "CUnitAI__UpdateHeadingTowardTargetClamped",
        "signature": "void __fastcall CUnitAI__UpdateHeadingTowardTargetClamped(void * turnContext)",
        "comment": ["true entry at 0x00429270", "turn context", "heading/clamp logic", "remain unproven"],
        "tags": COMMON_TAGS + ["boundary-corrected"],
    },
}

VTABLE_TYPES = {
    "0x005d96b4": "CComponentBomberAI",
    "0x005d9680": "CFenrirMainGunAI",
}

DEFAULT_METADATA_FINAL = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_TAGS = BASE / "tags_final.tsv"
DEFAULT_VTABLE_TYPES = BASE / "vtable_type_names.tsv"
DEFAULT_QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
DEFAULT_OUT = BASE / "unitai-activation-signature-correction.json"

OVERCLAIM_TOKENS = ("runtime behavior proven", "source identity proven", "fully re'ed", "100% re", "exact source identity proven")


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if not value or value.startswith("<"):
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def compact(value: str) -> str:
    return "".join(value.lower().split())


def token_present(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def read_json(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {}
    return json.loads(read_text(path))


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in ("address", "target_addr", "from_addr", "from_function_addr", "function_entry", "target_raw", "vtable", "instruction_addr"):
            if key in row and row[key]:
                row[key] = normalize_address(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def row_by_address(rows: list[dict[str, str]], address: str, key: str = "address") -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(key, "")) == wanted:
            return row
    return None


def rows_for_address(rows: list[dict[str, str]], address: str, key: str) -> list[dict[str, str]]:
    wanted = normalize_address(address)
    return [row for row in rows if normalize_address(row.get(key, "")) == wanted]


def decompile_text_for(directory: Path, address: str) -> str:
    if not directory.is_dir():
        return ""
    matches = sorted(directory.glob(f"{normalize_address(address)[2:]}_*.c"))
    if not matches:
        return ""
    return read_text(matches[0])


def parse_tags(value: str) -> set[str]:
    return {part.strip() for part in value.split(";") if part.strip()}


def queue_signal(report: dict[str, object], name: str) -> int | None:
    signals = report.get("qualitySignals", {})
    if isinstance(signals, dict) and isinstance(signals.get(name), int):
        return int(signals[name])
    return None


def build_report(
    *,
    metadata_final_path: Path = DEFAULT_METADATA_FINAL,
    decompile_index_path: Path = DEFAULT_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
    tags_path: Path = DEFAULT_TAGS,
    vtable_types_path: Path = DEFAULT_VTABLE_TYPES,
    queue_json_path: Path = DEFAULT_QUEUE_JSON,
) -> dict[str, object]:
    metadata_final_path = resolve(metadata_final_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)
    tags_path = resolve(tags_path)
    vtable_types_path = resolve(vtable_types_path)
    queue_json_path = resolve(queue_json_path)

    failures: list[str] = []
    for path, label in (
        (metadata_final_path, "metadata_final"),
        (decompile_index_path, "decompile_index"),
        (xrefs_path, "xrefs"),
        (instructions_path, "instructions"),
        (tags_path, "tags"),
        (vtable_types_path, "vtable_types"),
        (queue_json_path, "queue_json"),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")

    final_rows = read_tsv(metadata_final_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)
    tag_rows = read_tsv(tags_path)
    vtable_rows = read_tsv(vtable_types_path)
    queue = read_json(queue_json_path)

    vtable_types = {row.get("vtable", ""): row.get("demangled_type_name", "") for row in vtable_rows}
    for vtable, expected_type in VTABLE_TYPES.items():
        actual = vtable_types.get(normalize_address(vtable), "")
        if actual != expected_type:
            failures.append(f"vtable type missing/mismatch at {vtable}: {actual} != {expected_type}")

    target_summaries: list[dict[str, object]] = []
    owner_or_boundary_targets = 0
    for address, expected in TARGETS.items():
        final = row_by_address(final_rows, address)
        index = row_by_address(index_rows, address)
        tag_row = row_by_address(tag_rows, address)
        decompile_text = decompile_text_for(decompile_dir, address)
        xrefs = rows_for_address(xref_rows, address, "target_addr")
        instructions = rows_for_address(instruction_rows, address, "target_addr")

        name = str(expected["name"])
        signature = str(expected["signature"])
        if "owner-corrected" in expected["tags"] or "boundary-corrected" in expected["tags"]:
            owner_or_boundary_targets += 1

        if final is None:
            failures.append(f"{address} missing from final metadata")
        else:
            actual_name = final.get("name", "")
            actual_signature = final.get("signature", "")
            actual_comment = final.get("comment", "")
            if actual_name != name:
                failures.append(f"{address} name mismatch: {actual_name} != {name}")
            if actual_signature != signature:
                failures.append(f"{address} signature mismatch: {actual_signature} != {signature}")
            for token in expected["comment"]:
                if not token_present(actual_comment, str(token)):
                    failures.append(f"{address} comment missing token: {token}")
            lowered_comment = actual_comment.lower()
            for token in OVERCLAIM_TOKENS:
                if token in lowered_comment:
                    failures.append(f"{address} comment overclaim token present: {token}")

        if index is None or index.get("status") != "OK":
            failures.append(f"{address} missing successful decompile index row")
        if not decompile_text:
            failures.append(f"{address} missing decompile body")
        elif address == "0x00429270":
            if "unaff_ESI" in decompile_text or "unaff_EDI" in decompile_text:
                failures.append("0x00429270 decompile still has unaff register artifacts after boundary correction")
            if "turnContext" not in decompile_text:
                failures.append("0x00429270 decompile missing turnContext parameter after signature correction")

        if tag_row is None:
            failures.append(f"{address} missing tag row")
        else:
            actual_tags = parse_tags(tag_row.get("tags", ""))
            for tag in expected["tags"]:
                if tag not in actual_tags:
                    failures.append(f"{address} tag missing: {tag}")

        if not instructions:
            failures.append(f"{address} missing instruction rows")
        if address != "0x00429270" and not xrefs:
            failures.append(f"{address} missing xref rows")

        target_summaries.append(
            {
                "address": address,
                "name": name,
                "xrefRows": len(xrefs),
                "instructionRows": len(instructions),
                "tags": sorted(parse_tags(tag_row.get("tags", ""))) if tag_row else [],
            }
        )

    old_boundary_rows = rows_for_address(instruction_rows, "0x00429280", "instruction_addr")
    if old_boundary_rows and not any(row.get("function_entry") == "0x00429270" for row in old_boundary_rows):
        failures.append("0x00429280 instruction is not owned by the recovered 0x00429270 function")

    component_xrefs = rows_for_address(xref_rows, "0x00428e80", "target_addr")
    component_from = {row.get("from_addr") for row in component_xrefs}
    for expected_from in ("0x005d96c4", "0x005d9690"):
        if expected_from not in component_from:
            failures.append(f"0x00428e80 missing component vtable DATA xref {expected_from}")

    queue_total = queue.get("totalFunctions")
    queue_status = queue.get("status")
    queue_commentless = queue_signal(queue, "commentlessFunctionCount")
    queue_undefined = queue_signal(queue, "undefinedSignatureCount")
    queue_params = queue_signal(queue, "paramSignatureCount")
    if queue_status != "PASS":
        failures.append(f"queue status is not PASS: {queue_status}")
    if queue_total is not None and queue_total < 5884:
        failures.append(f"totalFunctions regressed: {queue_total} < 5884")
    if queue_commentless is not None and queue_commentless > 5123:
        failures.append(f"commentlessFunctionCount regressed: {queue_commentless} > 5123")
    if queue_undefined is not None and queue_undefined > 1994:
        failures.append(f"undefinedSignatureCount regressed: {queue_undefined} > 1994")
    if queue_params is not None and queue_params > 2299:
        failures.append(f"paramSignatureCount regressed: {queue_params} > 2299")

    return {
        "schemaVersion": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "targetCount": len(TARGETS),
        "ownerOrBoundaryTargetCount": owner_or_boundary_targets,
        "targetSummaries": target_summaries,
        "queueTotalFunctions": queue_total,
        "queueCommentlessFunctions": queue_commentless,
        "queueUndefinedSignatures": queue_undefined,
        "queueParamSignatures": queue_params,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata-final", type=Path, default=DEFAULT_METADATA_FINAL)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--instructions", type=Path, default=DEFAULT_INSTRUCTIONS)
    parser.add_argument("--tags", type=Path, default=DEFAULT_TAGS)
    parser.add_argument("--vtable-types", type=Path, default=DEFAULT_VTABLE_TYPES)
    parser.add_argument("--queue-json", type=Path, default=DEFAULT_QUEUE_JSON)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_report(
        metadata_final_path=args.metadata_final,
        decompile_index_path=args.decompile_index,
        decompile_dir=args.decompile_dir,
        xrefs_path=args.xrefs,
        instructions_path=args.instructions,
        tags_path=args.tags,
        vtable_types_path=args.vtable_types,
        queue_json_path=args.queue_json,
    )
    out = resolve(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{report['status']}: wrote {relative(out)}")
    if report["failures"]:
        for failure in report["failures"]:
            print(f" - {failure}")
    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
