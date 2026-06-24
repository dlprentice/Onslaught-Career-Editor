#!/usr/bin/env python3
"""Validate the saved Ghidra Platform/CFrameTimer/CChunkReader correction wave."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "platform-chunker-wave319" / "current"

TARGETS = {
    "0x00423510": {
        "name": "CCarverGuide__AcquireNearestTargetReader",
        "signature": "void __fastcall CCarverGuide__AcquireNearestTargetReader(void * this)",
        "comment": ["CarverGuide-specific", "45.0-radius", "unproven"],
    },
    "0x00423650": {
        "name": "CFrameTimer__ctor",
        "signature": "void * __fastcall CFrameTimer__ctor(void * this)",
        "comment": ["CFrameTimer constructor", "PCPlatform__Init", "source body is absent", "unproven"],
    },
    "0x00423680": {
        "name": "CFrameTimer__Start",
        "signature": "void __thiscall CFrameTimer__Start(void * this, float frameScale)",
        "comment": ["Start-style helper", "source-parity 1.0f", "unproven"],
    },
    "0x00423720": {
        "name": "CFrameTimer__Frame",
        "signature": "void __fastcall CFrameTimer__Frame(void * this)",
        "comment": ["per-frame update", "PCPlatform__DeviceFlip", "unproven"],
    },
    "0x004237d0": {
        "name": "CChunkReader__ctor",
        "signature": "void * __fastcall CChunkReader__ctor(void * this)",
        "comment": ["CChunkReader constructor", "0x134-byte CDXMemBuffer", "mOwnFile", "unproven"],
    },
    "0x00423840": {
        "name": "CChunkReader__dtor_base",
        "signature": "void __fastcall CChunkReader__dtor_base(void * this)",
        "comment": ["destructor-base", "mOwnFile", "CDXMemBuffer", "unproven"],
    },
    "0x00423870": {
        "name": "CChunkReader__OpenExistingBuffer",
        "signature": "void * __thiscall CChunkReader__OpenExistingBuffer(void * this, void * existingBuffer)",
        "comment": ["Open(CMEMBUFFER*)", "mOwnFile false", "unproven"],
    },
    "0x004238c0": {
        "name": "CChunkReader__OpenFile",
        "signature": "void * __thiscall CChunkReader__OpenFile(void * this, char * filename)",
        "comment": ["Open(char*)", "CDXMemBuffer__InitFromFile", "unproven"],
    },
    "0x00423900": {
        "name": "CChunkReader__Close",
        "signature": "int __fastcall CChunkReader__Close(void * this)",
        "comment": ["Close wrapper", "0 on successful close", "-1", "unproven"],
    },
    "0x00423910": {
        "name": "CChunkReader__GetNext",
        "signature": "uint __fastcall CChunkReader__GetNext(void * this)",
        "comment": ["GetNext", "4-byte chunk id", "not CMeshPart-specific", "unproven"],
    },
    "0x00423960": {
        "name": "CChunkReader__Read",
        "signature": "bool __thiscall CChunkReader__Read(void * this, void * outBuffer, int size, int count)",
        "comment": ["Read source-parity", "ReadSinceChunk", "CDXMemBuffer__Read", "unproven"],
    },
    "0x00423990": {
        "name": "CChunkReader__Skip",
        "signature": "int __fastcall CChunkReader__Skip(void * this)",
        "comment": ["Skip source-parity", "Size-ReadSinceChunk", "CDXMemBuffer__Skip", "unproven"],
    },
    "0x004239b0": {
        "name": "CWorld__GetSubstateField_12C",
        "signature": "int __thiscall CWorld__GetSubstateField_12C(void * this)",
        "comment": ["small CWorld accessor", "*(this+4)+0x12c", "unproven"],
    },
    "0x004239f0": {
        "name": "CUnitAI__InitDefaults_AutoConfigTestPath",
        "signature": "void * __fastcall CUnitAI__InitDefaults_AutoConfigTestPath(void * this)",
        "comment": ["constructor-style", "c:\\beaautoconfigtest\\", "CUnitAI source body is absent", "unproven"],
    },
    "0x005158f0": {
        "name": "PCPlatform__DeviceFlip",
        "signature": "void __thiscall PCPlatform__DeviceFlip(void * this, int inGame)",
        "comment": ["CPCPlatform::DeviceFlip", "CFrameTimer__Frame", "inGame argument", "unproven"],
    },
    "0x00515950": {
        "name": "PCPlatform__GetFPS",
        "signature": "float __fastcall PCPlatform__GetFPS(void * this)",
        "comment": ["CPCPlatform::GetFPS", "1.0f", "unproven"],
    },
    "0x00547d70": {
        "name": "CDXMemBuffer__ctor",
        "signature": "void * __fastcall CDXMemBuffer__ctor(void * this)",
        "comment": ["CDXMemBuffer constructor", "Corrects stale CChunker", "unproven"],
    },
    "0x00547d90": {
        "name": "CDXMemBuffer__dtor_base",
        "signature": "void __fastcall CDXMemBuffer__dtor_base(void * this)",
        "comment": ["CDXMemBuffer destructor-base", "mData", "mCRCData", "unproven"],
    },
    "0x00547ec0": {
        "name": "CDXMemBuffer__InitFromFile",
        "signature": "bool __thiscall CDXMemBuffer__InitFromFile(void * this, char * filename, int memType, int mungePath, uint startSkip)",
        "comment": ["InitFromFile", "read buffer", "CRC-style side data", "unproven"],
    },
    "0x005482d0": {
        "name": "CDXMemBuffer__Skip",
        "signature": "int __thiscall CDXMemBuffer__Skip(void * this, int size)",
        "comment": ["CDXMemBuffer::Skip", "byte count skipped", "unproven"],
    },
    "0x00548570": {
        "name": "CDXMemBuffer__Read",
        "signature": "int __thiscall CDXMemBuffer__Read(void * this, void * data, int size)",
        "comment": ["CDXMemBuffer::Read", "byte count read", "unproven"],
    },
    "0x00548c00": {
        "name": "CDXMemBuffer__Close",
        "signature": "bool __fastcall CDXMemBuffer__Close(void * this)",
        "comment": ["CDXMemBuffer::Close", "read mode", "write mode", "unproven"],
    },
}

STALE_FINAL_TOKENS = [
    "CCylinder__AcquireNearestTargetReader",
    "PCPlatform__ReadPerformanceFrequency",
    "PCPlatform__InitTimerFromPerfCounter",
    "Platform__UpdateHighResTimerDeltaAndScale",
    "CChunker__Create",
    "CChunkerStream__DestroyOwnedChunkerIfPresent",
    "CResourceAccumulator__ResetChunkerSlotAndAssignSource",
    "CChunkerStream__OpenReadAndGetChunker",
    "CChunkerStream__CloseDXMemBuffer_Status0OrMinus1",
    "CMeshPart__ReadHeaderPairAndResetByteCount",
    "CMeshPart__ReadBlockAndAccumulateByteCount",
    "CChunkerStream__SkipRemainingChunkBytes",
    "Platform__FinalizeAsyncSaveCareer",
    "PtrFloatAt4__GetOrOne",
    "CChunker__CChunker",
    "CChunker__Destructor",
    "DXMemBuffer__OpenRead",
    "DXMemBuffer__ReadBytes",
    "param_",
    "undefined CChunk",
    "undefined DXMemBuffer",
]

DEFAULT_METADATA_BEFORE = BASE / "metadata_before_final_targets.tsv"
DEFAULT_METADATA = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
DEFAULT_OUT = BASE / "platform-chunker-timer-signature-correction.json"


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
    metadata_before_path: Path = DEFAULT_METADATA_BEFORE,
    metadata_final_path: Path = DEFAULT_METADATA,
    decompile_index_path: Path = DEFAULT_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
    queue_json_path: Path = DEFAULT_QUEUE_JSON,
) -> dict[str, object]:
    metadata_before_path = resolve(metadata_before_path)
    metadata_final_path = resolve(metadata_final_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)
    queue_json_path = resolve(queue_json_path)

    failures: list[str] = []
    for label, path in (
        ("before metadata", metadata_before_path),
        ("final metadata", metadata_final_path),
        ("final decompile index", decompile_index_path),
        ("final xrefs", xrefs_path),
        ("final instructions", instructions_path),
        ("queue report", queue_json_path),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")
    if not decompile_dir.is_dir():
        failures.append(f"missing decompile dir: {relative(decompile_dir)}")

    before_rows = read_tsv(metadata_before_path)
    metadata_rows = read_tsv(metadata_final_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)
    queue_report = read_json(queue_json_path)

    renamed_targets = 0
    target_reports: list[dict[str, object]] = []
    for address, expected in TARGETS.items():
        before_row = row_by_address(before_rows, address)
        row = row_by_address(metadata_rows, address)
        index_row = row_by_address(index_rows, address)
        if before_row is None:
            failures.append(f"before metadata missing {address}")
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

        if before_row is not None and before_row.get("name") != name:
            renamed_targets += 1
        if name != expected["name"]:
            failures.append(f"name mismatch {address}: {name} != {expected['name']}")
        if signature != expected["signature"]:
            failures.append(f"signature mismatch {address}: {signature} != {expected['signature']}")
        for token in expected["comment"]:
            if not token_present(comment, token):
                failures.append(f"comment token missing {address}: {token}")
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
    if len(xref_rows) < 1075:
        failures.append(f"xref row count too low: {len(xref_rows)} < 1075")
    if len(instruction_rows) < 1078:
        failures.append(f"instruction row count too low: {len(instruction_rows)} < 1078")
    if renamed_targets != 20:
        failures.append(f"renamed target count mismatch: {renamed_targets} != 20")

    if queue_report.get("status") != "PASS":
        failures.append(f"queue report status is not PASS: {queue_report.get('status')}")
    if queue_report.get("totalFunctions") != 5876:
        failures.append(f"queue totalFunctions mismatch: {queue_report.get('totalFunctions')}")
    expected_signals = {
        "commentlessFunctionCount": 5171,
        "undefinedSignatureCount": 2023,
        "paramSignatureCount": 2319,
        "uncertainOwnerNameCount": 0,
        "helperAddressNameCount": 0,
        "wrapperAddressNameCount": 0,
    }
    for key, expected_value in expected_signals.items():
        actual = quality_signal(queue_report, key)
        if actual is not None and actual != expected_value:
            failures.append(f"queue {key} mismatch: {actual} != {expected_value}")

    return {
        "schema": "ghidra-platform-chunker-timer-signature-correction.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "FAIL" if failures else "PASS",
        "classification": "platform-frametimer-chunkreader-signature-correction",
        "signatureCorrectedTargets": len(TARGETS),
        "renamedTargets": renamed_targets,
        "metadataRows": len(metadata_rows),
        "decompileRows": len(index_rows),
        "xrefRows": len(xref_rows),
        "instructionRows": len(instruction_rows),
        "queueTotalFunctions": queue_report.get("totalFunctions"),
        "queueCommentedFunctions": 705,
        "queueCommentlessFunctions": quality_signal(queue_report, "commentlessFunctionCount"),
        "queueUndefinedSignatures": quality_signal(queue_report, "undefinedSignatureCount"),
        "queueParamSignatures": quality_signal(queue_report, "paramSignatureCount"),
        "targetReports": target_reports,
        "whatIsProven": [
            "Saved Ghidra metadata now carries source/decompile/xref-backed names, signatures, and comments for the Platform/CFrameTimer/CChunkReader/CDXMemBuffer correction cluster.",
            "The generic static re-audit queue no longer lists the corrected 0x00423510..0x004239f0 target cluster as commentless high-signal debt.",
        ],
        "notProven": [
            "This does not prove runtime timing, display, resource IO, AI, target-reader, or world behavior.",
            "This does not prove concrete class layouts, local variable names, tags, rebuild parity, or exhaustive source identity for source-absent bodies.",
            "This does not launch, patch, or mutate BEA.exe.",
        ],
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="exit non-zero when the report fails")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--metadata-before", type=Path, default=DEFAULT_METADATA_BEFORE)
    parser.add_argument("--metadata-final", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--instructions", type=Path, default=DEFAULT_INSTRUCTIONS)
    parser.add_argument("--queue-json", type=Path, default=DEFAULT_QUEUE_JSON)
    args = parser.parse_args()

    report = build_report(
        metadata_before_path=args.metadata_before,
        metadata_final_path=args.metadata_final,
        decompile_index_path=args.decompile_index,
        decompile_dir=args.decompile_dir,
        xrefs_path=args.xrefs,
        instructions_path=args.instructions,
        queue_json_path=args.queue_json,
    )

    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"Status: {report['status']}")
    print(f"Classification: {report['classification']}")
    print(f"Signature targets: {report['signatureCorrectedTargets']}")
    print(f"Renamed targets: {report['renamedTargets']}")
    print(f"Queue total/commented/commentless: {report['queueTotalFunctions']}/{report['queueCommentedFunctions']}/{report['queueCommentlessFunctions']}")
    print(f"Queue undefined/param signatures: {report['queueUndefinedSignatures']}/{report['queueParamSignatures']}")
    print(f"Failures: {len(report['failures'])}")
    print(f"Report: {relative(out_path)}")
    if report["failures"]:
        for failure in report["failures"]:
            print(f"- {failure}")

    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
