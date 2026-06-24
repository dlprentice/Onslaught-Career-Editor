#!/usr/bin/env python3
"""Validate the saved Ghidra Component signature/comment/tag correction wave."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "component-wave324" / "current"

COMMON_TAGS = ["static-reaudit", "component-wave324", "component-system", "signature-hardened"]

TARGETS = {
    "0x00427b80": {
        "name": "CComponent__VFunc_09_00427b80",
        "signature": "void __thiscall CComponent__VFunc_09_00427b80(void * this, void * init)",
        "comment": ["init-like", "Thunderhead Main Gun", "Normal", "Activated", "runtime activation behavior", "remain unproven"],
        "tags": COMMON_TAGS,
    },
    "0x00427cd0": {
        "name": "CComponent__CreateSubComponent1",
        "signature": "void __fastcall CComponent__CreateSubComponent1(void * this)",
        "comment": ["0x14", "this+0x70", "Component.cpp", "line 0x4d", "remain unproven"],
        "tags": COMMON_TAGS,
    },
    "0x00427d50": {
        "name": "CComponent__CreateSubComponent2",
        "signature": "void __fastcall CComponent__CreateSubComponent2(void * this)",
        "comment": ["0x20", "this+0x208", "CComponentGuide", "line 0x53", "remain unproven"],
        "tags": COMMON_TAGS,
    },
    "0x00427dd0": {
        "name": "CComponent__CreateWeaponComponent",
        "signature": "void __thiscall CComponent__CreateWeaponComponent(void * this, void * initOrContext)",
        "comment": ["Fenrir Bomb Launcher", "Fenrir Main Gun", "Carrier Health Pad", "CRepairPadAI", "field +0x14", "remain unproven"],
        "tags": COMMON_TAGS,
    },
    "0x00427f90": {
        "name": "CComponentBomberAI__scalar_deleting_dtor",
        "signature": "void * __thiscall CComponentBomberAI__scalar_deleting_dtor(void * this, byte flags)",
        "comment": ["scalar-delete", "CComponentBomberAI", "OID__FreeObject", "vtable 0x005d96b4", "remain unproven"],
        "tags": COMMON_TAGS + ["owner-corrected", "destructor"],
    },
    "0x00427fb0": {
        "name": "CComponentBomberAI__dtor_base",
        "signature": "void __fastcall CComponentBomberAI__dtor_base(void * this)",
        "comment": ["destructor-base", "CUnitAI", "+0x28/+0x24/+0xc", "CSPtrSet__Remove", "CMonitor__Shutdown", "remain unproven"],
        "tags": COMMON_TAGS + ["owner-corrected", "destructor"],
    },
    "0x00428050": {
        "name": "CFenrirMainGunAI__scalar_deleting_dtor",
        "signature": "void * __thiscall CFenrirMainGunAI__scalar_deleting_dtor(void * this, byte flags)",
        "comment": ["scalar-delete", "CFenrirMainGunAI", "OID__FreeObject", "vtable 0x005d9680", "remain unproven"],
        "tags": COMMON_TAGS + ["owner-corrected", "destructor"],
    },
    "0x00428070": {
        "name": "CFenrirMainGunAI__dtor_base",
        "signature": "void __fastcall CFenrirMainGunAI__dtor_base(void * this)",
        "comment": ["destructor-base", "CUnitAI", "+0x28/+0x24/+0xc", "CSPtrSet__Remove", "CMonitor__Shutdown", "remain unproven"],
        "tags": COMMON_TAGS + ["owner-corrected", "destructor"],
    },
    "0x00428110": {
        "name": "CUnitAI__UpdateActivationStateAndSpawnPickup",
        "signature": "void __fastcall CUnitAI__UpdateActivationStateAndSpawnPickup(void * this)",
        "comment": ["Activate", "Deactivated", "Gill_M_Claw_Hit", "CWorldPhysicsManager__CreatePickup", "remain unproven"],
        "tags": COMMON_TAGS,
    },
    "0x00428500": {
        "name": "CUnitAI__RefreshCachedComponentTransform",
        "signature": "void __fastcall CUnitAI__RefreshCachedComponentTransform(void * this)",
        "comment": ["Component", "this+0x278", "DAT_008a9aac", "Mat34__SetRows", "remain unproven"],
        "tags": COMMON_TAGS,
    },
}

VTABLE_TYPES = {
    "0x005d96b4": "CComponentBomberAI",
    "0x005d9680": "CFenrirMainGunAI",
    "0x005d8e08": "CRepairPadAI",
    "0x005d9654": "CComponentGuide",
    "0x005d8d1c": "CUnitAI",
}

DEFAULT_METADATA_FINAL = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_TAGS = BASE / "tags_final.tsv"
DEFAULT_VTABLE_TYPES = BASE / "vtable_type_names.tsv"
DEFAULT_QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
DEFAULT_OUT = BASE / "component-signature-correction.json"

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
        for key in ("address", "target_addr", "function_entry", "target_raw", "vtable"):
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


def queue_signal(report: dict[str, object], name: str) -> int | None:
    signals = report.get("qualitySignals", {})
    if isinstance(signals, dict) and isinstance(signals.get(name), int):
        return int(signals[name])
    return None


def parse_tags(value: str) -> set[str]:
    return {part.strip() for part in value.split(";") if part.strip()}


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
    renamed_targets = 0
    stale_params = 0
    for address, expected in TARGETS.items():
        final = row_by_address(final_rows, address)
        index = row_by_address(index_rows, address)
        tag_row = row_by_address(tag_rows, address)
        decompile_text = decompile_text_for(decompile_dir, address)
        xrefs = rows_for_address(xref_rows, address, "target_addr")
        instructions = rows_for_address(instruction_rows, address, "target_addr")

        name = str(expected["name"])
        signature = str(expected["signature"])
        if "owner-corrected" in expected["tags"]:
            renamed_targets += 1

        if final is None:
            failures.append(f"{address} missing from final metadata")
        else:
            if final.get("name") != name:
                failures.append(f"{address} final name mismatch: {final.get('name', '')} != {name}")
            if final.get("signature") != signature:
                failures.append(f"{name} signature mismatch: {final.get('signature', '')} != {signature}")
            if "param_" in final.get("signature", ""):
                stale_params += 1
                failures.append(f"{name} final signature still has param_N placeholder: {final.get('signature', '')}")
            comment = final.get("comment", "")
            for token in expected["comment"]:
                if not token_present(comment, str(token)):
                    failures.append(f"{name} comment missing token: {token}")
            lowered_comment = comment.lower()
            for token in OVERCLAIM_TOKENS:
                if token in lowered_comment:
                    failures.append(f"{name} comment overclaim token: {token}")

        if index is None:
            failures.append(f"{address} missing from decompile index")
        elif index.get("signature") != signature:
            failures.append(f"{name} decompile index signature mismatch: {index.get('signature', '')}")
        if not token_present(decompile_text, signature):
            failures.append(f"{name} decompile text did not include final signature")
        if len(xrefs) == 0:
            failures.append(f"{name} has no xref rows")
        if len(instructions) == 0:
            failures.append(f"{name} has no instruction rows")
        if tag_row is None:
            failures.append(f"{name} missing tag read-back row")
            present_tags: set[str] = set()
        else:
            present_tags = parse_tags(tag_row.get("tags", ""))
        for tag in expected["tags"]:
            if tag not in present_tags:
                failures.append(f"{name} tag missing: {tag}")

        target_summaries.append(
            {
                "address": address,
                "name": name,
                "signature": signature,
                "tags": sorted(present_tags),
                "xrefRows": len(xrefs),
                "instructionRows": len(instructions),
            }
        )

    if queue.get("status") != "PASS":
        failures.append(f"queue status is not PASS: {queue.get('status')}")
    total_functions = queue.get("totalFunctions")
    if not isinstance(total_functions, int) or total_functions < 5884:
        failures.append(f"totalFunctions below expected floor: {total_functions}")

    commentless = queue_signal(queue, "commentlessFunctionCount")
    undefined = queue_signal(queue, "undefinedSignatureCount")
    param_signatures = queue_signal(queue, "paramSignatureCount")
    if commentless is not None and commentless > 5123:
        failures.append(f"commentlessFunctionCount did not drop to expected ceiling: {commentless}")
    if undefined is not None and undefined > 1994:
        failures.append(f"undefinedSignatureCount did not drop to expected ceiling: {undefined}")
    if param_signatures is not None and param_signatures > 2299:
        failures.append(f"paramSignatureCount did not drop to expected ceiling: {param_signatures}")

    return {
        "schema": "ghidra-component-signature-correction.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "targetCount": len(TARGETS),
        "renamedTargets": renamed_targets,
        "staleParamSignatures": stale_params,
        "queueTotalFunctions": total_functions,
        "queueCommentlessFunctions": commentless,
        "queueUndefinedSignatures": undefined,
        "queueParamSignatures": param_signatures,
        "vtableTypes": vtable_types,
        "targets": target_summaries,
        "evidence": {
            "metadataFinal": relative(metadata_final_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
            "tags": relative(tags_path),
            "vtableTypes": relative(vtable_types_path),
            "queueJson": relative(queue_json_path),
        },
        "failures": failures,
        "notProven": [
            "Exact source method identity remains open where current source bodies are absent.",
            "Concrete Component/CUnitAI/weapon-component layouts, local names, and type definitions remain partial.",
            "Runtime activation, animation, pickup spawning, destruction behavior, and rebuild parity are not proven by this static correction.",
        ],
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
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{report['status']}: wrote {relative(out)}")
    if report["failures"]:
        for failure in report["failures"]:
            print(f"- {failure}")
    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
