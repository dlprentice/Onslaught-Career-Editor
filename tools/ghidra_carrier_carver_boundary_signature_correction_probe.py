#!/usr/bin/env python3
"""Validate the saved Ghidra Carrier/Carver boundary and signature correction wave."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "carrier-carver-wave318" / "current"

TARGETS = {
    "0x00421a80": {
        "name": "CCarrier__Init",
        "signature": "void __thiscall CCarrier__Init(void * this, void * init)",
        "comment": ["Carrier init", "CAirUnit__Init", "Carrier.cpp source is absent", "unproven"],
    },
    "0x00421b80": {
        "name": "CCarrierAI__scalar_deleting_dtor",
        "signature": "void * __thiscall CCarrierAI__scalar_deleting_dtor(void * this, byte flags)",
        "comment": ["scalar-deleting destructor", "Corrects the stale", "unproven"],
    },
    "0x00421ba0": {
        "name": "CCarrierAI__dtor_base",
        "signature": "void __fastcall CCarrierAI__dtor_base(void * this)",
        "comment": ["destructor-base", "CMonitor__Shutdown", "unproven"],
    },
    "0x00421c40": {
        "name": "CUnit__ApplyFlag4DampingAndScaleSpeed",
        "signature": "void __fastcall CUnit__ApplyFlag4DampingAndScaleSpeed(void * this)",
        "comment": ["flag-bit-4", "CUnit__UpdateMotionAndTrailEffects", "unproven"],
    },
    "0x00422440": {
        "name": "CCarver__Init",
        "signature": "void __thiscall CCarver__Init(void * this, void * init)",
        "comment": ["Function-boundary recovery", "CCarverGuide", "Carver.cpp source is absent", "unproven"],
    },
    "0x00422560": {
        "name": "CCarverAI__scalar_deleting_dtor",
        "signature": "void * __thiscall CCarverAI__scalar_deleting_dtor(void * this, byte flags)",
        "comment": ["scalar-deleting destructor", "CCarverAI__dtor_base", "unproven"],
    },
    "0x00422580": {
        "name": "CCarverAI__dtor_base",
        "signature": "void __fastcall CCarverAI__dtor_base(void * this)",
        "comment": ["destructor-base", "CMonitor__Shutdown", "unproven"],
    },
    "0x00422620": {
        "name": "CCarver__UpdateMotionAndWingPose",
        "signature": "void __fastcall CCarver__UpdateMotionAndWingPose(void * this)",
        "comment": ["Function-boundary recovery", "wing/blend", "CUnit__UpdateMotionAndTrailEffects", "unproven"],
    },
    "0x00422760": {
        "name": "CCarverAI__OpenWings",
        "signature": "void __fastcall CCarverAI__OpenWings(void * this)",
        "comment": ["wingopen", "animation", "unproven"],
    },
    "0x004227a0": {
        "name": "CCarverAI__CloseWings",
        "signature": "void __fastcall CCarverAI__CloseWings(void * this)",
        "comment": ["wingclose", "animation", "unproven"],
    },
    "0x004227e0": {
        "name": "CCarverAI__OnHit",
        "signature": "void __thiscall CCarverAI__OnHit(void * this, void * otherThing, void * collisionReport)",
        "comment": ["Carver hit override", "collisionReport", "unproven"],
    },
    "0x00422820": {
        "name": "CCarverAI__Fire",
        "signature": "int __fastcall CCarverAI__Fire(void * this)",
        "comment": ["fire helper", "wing/attack animation", "unproven"],
    },
    "0x00422930": {
        "name": "CCarverAI__SetLastAttackTime",
        "signature": "void __fastcall CCarverAI__SetLastAttackTime(void * this)",
        "comment": ["current global time", "last-attack", "unproven"],
    },
    "0x00422940": {
        "name": "CCarverAI__IsRecentlyAttacked",
        "signature": "int __fastcall CCarverAI__IsRecentlyAttacked(void * this)",
        "comment": ["last-attack timestamp", "cooldown", "unproven"],
    },
    "0x00422970": {
        "name": "CCarverAI__CanStartAttack",
        "signature": "int __fastcall CCarverAI__CanStartAttack(void * this)",
        "comment": ["Function-boundary recovery", "attack cooldown", "unproven"],
    },
    "0x004229b0": {
        "name": "CarverAimGlobals__ResetVector",
        "signature": "void __cdecl CarverAimGlobals__ResetVector(void)",
        "comment": ["Function-boundary recovery", "Carver aim/vector globals", "unproven"],
    },
    "0x004229d0": {
        "name": "CarverAimGlobals__InitMatrix",
        "signature": "void __cdecl CarverAimGlobals__InitMatrix(void)",
        "comment": ["Function-boundary recovery", "orientation global matrix", "unproven"],
    },
    "0x00422aa0": {
        "name": "CCarverAI__RefreshTargetReaderAndScheduleMove",
        "signature": "void __thiscall CCarverAI__RefreshTargetReaderAndScheduleMove(void * this, void * event)",
        "comment": ["Function-boundary recovery", "target-reader", "schedules event 0xbb9", "unproven"],
    },
    "0x00422b90": {
        "name": "CCarverAI__UpdateAttackAndReschedule",
        "signature": "void __thiscall CCarverAI__UpdateAttackAndReschedule(void * this, void * event)",
        "comment": ["Function-boundary recovery", "reschedules event 3000", "unproven"],
    },
    "0x00422db0": {
        "name": "CCarverAI__CheckNearbyEnemies",
        "signature": "void __fastcall CCarverAI__CheckNearbyEnemies(void * this)",
        "comment": ["map-who entries", "last-attack timestamp", "unproven"],
    },
    "0x00422f90": {
        "name": "CCarverGuide__ctor",
        "signature": "void * __thiscall CCarverGuide__ctor(void * this, void * guideTarget)",
        "comment": ["CCarverGuide constructor", "CAirGuide__ctor", "unproven"],
    },
    "0x00422fb0": {
        "name": "CCarverGuide__scalar_deleting_dtor",
        "signature": "void * __thiscall CCarverGuide__scalar_deleting_dtor(void * this, byte flags)",
        "comment": ["scalar-deleting destructor", "CCarverGuide__dtor_base", "unproven"],
    },
    "0x00422fd0": {
        "name": "CCarverGuide__dtor_base",
        "signature": "void __fastcall CCarverGuide__dtor_base(void * this)",
        "comment": ["destructor-base", "active-reader", "CMonitor__Shutdown", "unproven"],
    },
    "0x00423490": {
        "name": "CCarverGuide__HandleEvent",
        "signature": "void __thiscall CCarverGuide__HandleEvent(void * this, void * event)",
        "comment": ["Function-boundary recovery", "CAirGuide__HandleEvent", "0x7d1", "unproven"],
    },
}

CREATED_BOUNDARIES = {
    "0x00422440": "CCarver__Init_candidate",
    "0x00422620": "CCarver__Process_candidate",
    "0x00422970": "CCarverAI__CanAttack_candidate",
    "0x004229b0": "CCarverAimGlobals__Reset_candidate",
    "0x004229d0": "CCarverAimGlobals__InitMatrix_candidate",
    "0x00422aa0": "CCarverAI__Event3000Candidate",
    "0x00422b90": "CCarverAI__UpdateAttackCandidate",
    "0x00423490": "CCarverGuide__HandleEvent_candidate",
}

STALE_FINAL_TOKENS = [
    "_candidate",
    "CUnitAI__ctor_like_00421ba0",
    "CUnit__ApplyFlag4DampingAndScaleSpeed_00421c40",
    "CCarrierAI__VFunc_01_00421b80",
    "CCarverAI__ScalarDeletingDestructor",
    "CCarverAI__Destructor",
    "CCarverGuide__Constructor",
    "CCarverGuide__ScalarDeletingDestructor",
    "CCarverGuide__Destructor",
    "undefined CCarrier",
    "undefined CCarver",
    "param_",
]

DEFAULT_CREATED = BASE / "create_missing_boundaries_apply.tsv"
DEFAULT_AFTER_CREATE = BASE / "metadata_after_create.tsv"
DEFAULT_METADATA = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
DEFAULT_BASELINE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "current" / "static-reaudit-baseline.json"
DEFAULT_OUT = BASE / "carrier-carver-boundary-signature-correction.json"


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("<") or not value:
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
        for key in ("address", "target_addr", "function_entry", "target_raw"):
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


def quality_signal(report: dict[str, object], name: str) -> int | None:
    value = report.get("qualitySignals", {})
    if isinstance(value, dict) and isinstance(value.get(name), int):
        return int(value[name])
    return None


def build_report(
    *,
    created_boundaries_path: Path = DEFAULT_CREATED,
    metadata_after_create_path: Path = DEFAULT_AFTER_CREATE,
    metadata_final_path: Path = DEFAULT_METADATA,
    decompile_index_path: Path = DEFAULT_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
    queue_json_path: Path = DEFAULT_QUEUE_JSON,
    baseline_json_path: Path = DEFAULT_BASELINE_JSON,
) -> dict[str, object]:
    created_boundaries_path = resolve(created_boundaries_path)
    metadata_after_create_path = resolve(metadata_after_create_path)
    metadata_final_path = resolve(metadata_final_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)
    queue_json_path = resolve(queue_json_path)
    baseline_json_path = resolve(baseline_json_path)

    failures: list[str] = []
    for label, path in (
        ("created boundary report", created_boundaries_path),
        ("after-create metadata", metadata_after_create_path),
        ("final metadata", metadata_final_path),
        ("final decompile index", decompile_index_path),
        ("final xrefs", xrefs_path),
        ("final instructions", instructions_path),
        ("queue report", queue_json_path),
        ("baseline report", baseline_json_path),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")
    if not decompile_dir.is_dir():
        failures.append(f"missing decompile dir: {relative(decompile_dir)}")

    created_rows = read_tsv(created_boundaries_path)
    after_create_rows = read_tsv(metadata_after_create_path)
    metadata_rows = read_tsv(metadata_final_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)
    queue_report = read_json(queue_json_path)
    baseline_report = read_json(baseline_json_path)

    created_ok = [
        row for row in created_rows
        if row.get("status") == "created" and token_present(row.get("note", ""), "renamed")
    ]
    if len(created_ok) != len(CREATED_BOUNDARIES):
        failures.append(f"created boundary count mismatch: {len(created_ok)} != {len(CREATED_BOUNDARIES)}")
    for address, name in CREATED_BOUNDARIES.items():
        row = row_by_address(created_rows, address)
        if row is None:
            failures.append(f"created boundary missing {address}")
            continue
        if row.get("status") != "created":
            failures.append(f"created boundary status mismatch {address}: {row.get('status')}")
        if row.get("name") != name:
            failures.append(f"created boundary name mismatch {address}: {row.get('name')} != {name}")

    renamed_targets = 0
    target_reports: list[dict[str, object]] = []
    for address, expected in TARGETS.items():
        after_row = row_by_address(after_create_rows, address)
        row = row_by_address(metadata_rows, address)
        index_row = row_by_address(index_rows, address)
        if after_row is None:
            failures.append(f"after-create metadata missing {address}")
        if row is None:
            failures.append(f"final metadata missing {address}")
            continue
        if index_row is None:
            failures.append(f"decompile index missing {address}")
            continue

        name = row.get("name", "")
        signature = row.get("signature", "")
        comment = row.get("comment", "")
        decompile_text = decompile_text_for(decompile_dir, address)
        target_xrefs = rows_for_address(xref_rows, address, "target_addr")
        target_instructions = rows_for_address(instruction_rows, address, "target_addr")

        if after_row is not None and after_row.get("name") != name:
            renamed_targets += 1
        if name != expected["name"]:
            failures.append(f"name mismatch {address}: {name} != {expected['name']}")
        if signature != expected["signature"]:
            failures.append(f"signature mismatch {address}: {signature} != {expected['signature']}")
        for token in expected["comment"]:
            if not token_present(comment, token):
                failures.append(f"comment token missing {address}: {token}")
        if not comment:
            failures.append(f"missing final comment {address}")
        if index_row.get("status") != "OK":
            failures.append(f"decompile index status mismatch {address}: {index_row.get('status')}")
        if not decompile_text:
            failures.append(f"decompile text missing {address}")
        if not target_xrefs:
            failures.append(f"xrefs missing {address}")
        if not target_instructions:
            failures.append(f"instructions missing {address}")

        target_reports.append(
            {
                "address": address,
                "name": name,
                "signature": signature,
                "xrefRows": len(target_xrefs),
                "instructionRows": len(target_instructions),
            }
        )

    final_text = "\n".join(
        [
            read_text(metadata_final_path),
            read_text(decompile_index_path),
            "\n".join(decompile_text_for(decompile_dir, address) for address in TARGETS),
        ]
    )
    for stale_token in STALE_FINAL_TOKENS:
        if stale_token in final_text:
            failures.append(f"stale token remains in final read-back: {stale_token}")

    if len(metadata_rows) != len(TARGETS):
        failures.append(f"metadata row count mismatch: {len(metadata_rows)} != {len(TARGETS)}")
    if len(index_rows) != len(TARGETS):
        failures.append(f"decompile row count mismatch: {len(index_rows)} != {len(TARGETS)}")
    if len(xref_rows) < 29:
        failures.append(f"xref row count too low: {len(xref_rows)} < 29")
    if len(instruction_rows) < 1944:
        failures.append(f"instruction row count too low: {len(instruction_rows)} < 1944")
    if renamed_targets != 16:
        failures.append(f"renamed target count mismatch: {renamed_targets} != 16")

    if queue_report.get("status") != "PASS":
        failures.append(f"queue report status is not PASS: {queue_report.get('status')}")
    if baseline_report.get("status") != "PASS":
        failures.append(f"baseline report status is not PASS: {baseline_report.get('status')}")
    if queue_report.get("totalFunctions") != 5876:
        failures.append(f"queue totalFunctions mismatch: {queue_report.get('totalFunctions')}")
    if baseline_report.get("totalFunctions") != 5876:
        failures.append(f"baseline totalFunctions mismatch: {baseline_report.get('totalFunctions')}")
    expected_signals = {
        "commentlessFunctionCount": 5193,
        "undefinedSignatureCount": 2032,
        "paramSignatureCount": 2330,
        "uncertainOwnerNameCount": 0,
        "helperAddressNameCount": 0,
        "wrapperAddressNameCount": 0,
    }
    for key, expected_value in expected_signals.items():
        actual = quality_signal(queue_report, key)
        if actual is not None and actual != expected_value:
            failures.append(f"queue {key} mismatch: {actual} != {expected_value}")
    for key, expected_value in (
        ("undefinedSignatureCount", 2032),
        ("paramSignatureCount", 2330),
        ("uncertainOwnerNameCount", 0),
        ("helperAddressNameCount", 0),
        ("wrapperAddressNameCount", 0),
    ):
        actual = quality_signal(baseline_report, key)
        if actual is not None and actual != expected_value:
            failures.append(f"baseline {key} mismatch: {actual} != {expected_value}")

    return {
        "schema": "ghidra-carrier-carver-boundary-signature-correction.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "FAIL" if failures else "PASS",
        "classification": "carrier-carver-boundary-and-signature-correction",
        "createdBoundaryCount": len(created_ok),
        "signatureCorrectedTargets": len(TARGETS),
        "renamedTargets": renamed_targets,
        "metadataRows": len(metadata_rows),
        "decompileRows": len(index_rows),
        "xrefRows": len(xref_rows),
        "instructionRows": len(instruction_rows),
        "queueTotalFunctions": queue_report.get("totalFunctions"),
        "queueCommentedFunctions": 683,
        "queueCommentlessFunctions": quality_signal(queue_report, "commentlessFunctionCount"),
        "queueUndefinedSignatures": quality_signal(queue_report, "undefinedSignatureCount"),
        "queueParamSignatures": quality_signal(queue_report, "paramSignatureCount"),
        "targetReports": target_reports,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="exit non-zero when the report fails")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--created-boundaries", type=Path, default=DEFAULT_CREATED)
    parser.add_argument("--metadata-after-create", type=Path, default=DEFAULT_AFTER_CREATE)
    parser.add_argument("--metadata-final", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--instructions", type=Path, default=DEFAULT_INSTRUCTIONS)
    parser.add_argument("--queue-json", type=Path, default=DEFAULT_QUEUE_JSON)
    parser.add_argument("--baseline-json", type=Path, default=DEFAULT_BASELINE_JSON)
    args = parser.parse_args()

    report = build_report(
        created_boundaries_path=args.created_boundaries,
        metadata_after_create_path=args.metadata_after_create,
        metadata_final_path=args.metadata_final,
        decompile_index_path=args.decompile_index,
        decompile_dir=args.decompile_dir,
        xrefs_path=args.xrefs,
        instructions_path=args.instructions,
        queue_json_path=args.queue_json,
        baseline_json_path=args.baseline_json,
    )

    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"Status: {report['status']}")
    print(f"Classification: {report['classification']}")
    print(f"Created boundaries: {report['createdBoundaryCount']}")
    print(f"Signature targets: {report['signatureCorrectedTargets']}")
    print(f"Renamed targets: {report['renamedTargets']}")
    print(f"Queue total/commented/commentless: {report['queueTotalFunctions']}/{report['queueCommentedFunctions']}/{report['queueCommentlessFunctions']}")
    print(f"Failures: {len(report['failures'])}")
    print(f"Report: {relative(out_path)}")
    if report["failures"]:
        for failure in report["failures"]:
            print(f"- {failure}")

    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
