#!/usr/bin/env python3
"""Validate the saved Ghidra cockpit/volume/UnitAI correction wave."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "cockpit-volume-unitai-wave321" / "current"

TARGETS = {
    "0x004244b0": {
        "before_name": "CCockpit__ctor_like_004244b0",
        "before_signature": "int __thiscall CCockpit__ctor_like_004244b0(void * this, void * param_1, int param_2)",
        "name": "CCockpit__ctor",
        "signature": "void * __thiscall CCockpit__ctor(void * this, void * battleEngine)",
        "comment": ["constructor", "battleEngine", "+0x110", "EVENT_MANAGER", "runtime behavior", "remain unproven"],
    },
    "0x004247a0": {
        "before_name": "CGeneralVolume__InitRandomizedVelocityOffsets",
        "before_signature": "void __thiscall CGeneralVolume__InitRandomizedVelocityOffsets(void * this, int param_1, float param_2)",
        "name": "CGeneralVolume__InitRandomizedVelocityOffsets",
        "signature": "void __thiscall CGeneralVolume__InitRandomizedVelocityOffsets(void * this, int randomRange)",
        "comment": ["randomized velocity offsets", "+0x90", "+0xa0", "0.01", "runtime behavior", "remain unproven"],
    },
    "0x00424920": {
        "before_name": "CGeneralVolume__BeginFlyToWalkTransition",
        "before_signature": "void __fastcall CGeneralVolume__BeginFlyToWalkTransition(int param_1)",
        "name": "CGeneralVolume__BeginFlyToWalkTransition",
        "signature": "void __fastcall CGeneralVolume__BeginFlyToWalkTransition(void * this)",
        "comment": ["fly-to-walk", "flytowalk animation", "+0x114", "+0x11c", "runtime behavior", "remain unproven"],
    },
    "0x00424990": {
        "before_name": "CGeneralVolume__BeginWalkToFlyTransition",
        "before_signature": "void __fastcall CGeneralVolume__BeginWalkToFlyTransition(int param_1)",
        "name": "CGeneralVolume__BeginWalkToFlyTransition",
        "signature": "void __fastcall CGeneralVolume__BeginWalkToFlyTransition(void * this)",
        "comment": ["walk-to-fly", "walktofly animation", "+0x114", "+0x11c", "runtime behavior", "remain unproven"],
    },
    "0x00424a20": {
        "before_name": "CUnitAI__UpdateDeployAimAndScheduleEvent",
        "before_signature": "void __fastcall CUnitAI__UpdateDeployAimAndScheduleEvent(void * param_1)",
        "name": "CUnitAI__UpdateDeployAimAndScheduleEvent",
        "signature": "void __fastcall CUnitAI__UpdateDeployAimAndScheduleEvent(void * this)",
        "comment": ["deploy aim", "previous transform", "event 0x7d1", "runtime behavior", "remain unproven"],
    },
    "0x00424be0": {
        "before_name": "CUnitAI__AdvanceDeployAnimationPhase",
        "before_signature": "void __fastcall CUnitAI__AdvanceDeployAnimationPhase(int param_1)",
        "name": "CUnitAI__AdvanceDeployAnimationPhase",
        "signature": "void __fastcall CUnitAI__AdvanceDeployAnimationPhase(void * this)",
        "comment": ["animation phase", "+0x120", "+0x114", "runtime behavior", "remain unproven"],
    },
    "0x00424ca0": {
        "before_name": "CUnitAI__UpdateDeployTrackingTransformTowardTarget",
        "before_signature": "void __fastcall CUnitAI__UpdateDeployTrackingTransformTowardTarget(int param_1)",
        "name": "CUnitAI__UpdateDeployTrackingTransformTowardTarget",
        "signature": "void __fastcall CUnitAI__UpdateDeployTrackingTransformTowardTarget(void * this)",
        "comment": ["tracking transform", "target", "terrain normal", "+0x2c", "runtime behavior", "remain unproven"],
    },
    "0x004250f0": {
        "before_name": "CUnitAI__DecayDeployTrackingTransformToNeutral",
        "before_signature": "void __fastcall CUnitAI__DecayDeployTrackingTransformToNeutral(int param_1)",
        "name": "CUnitAI__DecayDeployTrackingTransformToNeutral",
        "signature": "void __fastcall CUnitAI__DecayDeployTrackingTransformToNeutral(void * this)",
        "comment": ["neutral", "+0xa4/+0xa8", "+0x2c", "runtime behavior", "remain unproven"],
    },
    "0x00425760": {
        "before_name": "CUnitAI__OrthonormalizeMat34Axes",
        "before_signature": "void __fastcall CUnitAI__OrthonormalizeMat34Axes(void * param_1)",
        "name": "Mat34__OrthonormalizeAxes",
        "signature": "void __fastcall Mat34__OrthonormalizeAxes(void * mat34)",
        "comment": ["generic matrix", "cross product", "not CUnitAI-specific", "runtime behavior", "remain unproven"],
    },
}

DEFAULT_METADATA_BEFORE = BASE / "metadata_before.tsv"
DEFAULT_METADATA = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
DEFAULT_OUT = BASE / "cockpit-volume-unitai-signature-correction.json"

EXPECTED_QUEUE = {
    "totalFunctions": 5876,
    "commentlessFunctionCount": 5152,
    "undefinedSignatureCount": 2013,
    "paramSignatureCount": 2310,
}

OVERCLAIM_TOKENS = ("runtime behavior proven", "source identity proven", "fully re'ed", "100% re")


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


def queue_signal(report: dict[str, object], name: str) -> int | None:
    signals = report.get("qualitySignals", {})
    if isinstance(signals, dict) and isinstance(signals.get(name), int):
        return int(signals[name])
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
    for path, label in (
        (metadata_before_path, "metadata_before"),
        (metadata_final_path, "metadata_final"),
        (decompile_index_path, "decompile_index"),
        (xrefs_path, "xrefs"),
        (instructions_path, "instructions"),
        (queue_json_path, "queue_json"),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")

    before_rows = read_tsv(metadata_before_path)
    final_rows = read_tsv(metadata_final_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)
    queue = read_json(queue_json_path)

    corrected = 0
    renamed = 0
    stale_params = 0
    target_summaries: list[dict[str, object]] = []
    for address, expected in TARGETS.items():
        before = row_by_address(before_rows, address)
        final = row_by_address(final_rows, address)
        index = row_by_address(index_rows, address)
        decompile_text = decompile_text_for(decompile_dir, address)
        xrefs = rows_for_address(xref_rows, address, "target_addr")
        instructions = rows_for_address(instruction_rows, address, "target_addr")

        name = expected["name"]
        signature = expected["signature"]
        if before is None:
            failures.append(f"{address} missing from before metadata")
        else:
            if before.get("name") != expected["before_name"]:
                failures.append(f"{name} before name mismatch: {before.get('name', '')} != {expected['before_name']}")
            if before.get("signature") != expected["before_signature"]:
                failures.append(f"{name} before signature mismatch: {before.get('signature', '')} != {expected['before_signature']}")
            if before.get("name") != name:
                renamed += 1

        if final is None:
            failures.append(f"{address} missing from final metadata")
        else:
            if final.get("name") != name:
                failures.append(f"{name} final name mismatch: {final.get('name', '')}")
            if final.get("signature") != signature:
                failures.append(f"{name} signature mismatch: {final.get('signature', '')} != {signature}")
            elif before is not None and before.get("signature") != signature:
                corrected += 1
            if "param_" in final.get("signature", ""):
                stale_params += 1
                failures.append(f"{name} final signature still has param_N placeholder: {final.get('signature', '')}")
            comment = final.get("comment", "")
            for token in expected["comment"]:
                if not token_present(comment, token):
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

        target_summaries.append(
            {
                "address": address,
                "name": name,
                "signature": signature,
                "xrefRows": len(xrefs),
                "instructionRows": len(instructions),
            }
        )

    if queue.get("status") != "PASS":
        failures.append(f"queue status is not PASS: {queue.get('status')}")
    if queue.get("totalFunctions") != EXPECTED_QUEUE["totalFunctions"]:
        failures.append(f"totalFunctions drift: {queue.get('totalFunctions')} != {EXPECTED_QUEUE['totalFunctions']}")
    for key in ("commentlessFunctionCount", "undefinedSignatureCount", "paramSignatureCount"):
        actual = queue_signal(queue, key)
        expected = EXPECTED_QUEUE[key]
        if actual != expected:
            failures.append(f"{key} drift: {actual} != {expected}")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-cockpit-volume-unitai-signature-correction.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "inputs": {
            "metadataBefore": relative(metadata_before_path),
            "metadataFinal": relative(metadata_final_path),
            "decompileIndex": relative(decompile_index_path),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
            "queue": relative(queue_json_path),
        },
        "signatureCorrectedTargets": corrected,
        "renamedTargets": renamed,
        "staleParamSignatures": stale_params,
        "targetCount": len(TARGETS),
        "xrefRows": len(xref_rows),
        "instructionRows": len(instruction_rows),
        "queueCommentlessFunctions": queue_signal(queue, "commentlessFunctionCount"),
        "queueUndefinedSignatures": queue_signal(queue, "undefinedSignatureCount"),
        "queueParamSignatures": queue_signal(queue, "paramSignatureCount"),
        "targets": target_summaries,
        "failures": failures,
        "whatIsProven": [
            "The saved Ghidra project has corrected names/signatures/comments for the cockpit constructor-like body, GeneralVolume transition/random-offset helpers, UnitAI deploy transform helpers, and a generic Mat34 axis-normalization helper.",
            "Callsite read-back narrows stale phantom parameters for the cockpit constructor, transition helpers, and randomized-offset helper.",
            "The matrix orthonormalization helper is no longer recorded as CUnitAI-specific because current xrefs span broader callers.",
        ],
        "notProven": [
            "This does not prove runtime morph, deploy, cockpit, or matrix behavior.",
            "This does not prove exact source-to-retail identity for source bodies absent from the current Stuart source snapshot.",
            "This does not prove concrete class/struct layouts, locals, tags, or rebuild parity.",
            "This does not mutate or run BEA.exe.",
        ],
        "privacy": "Report stores repo-relative paths, public addresses, names, signatures, aggregate counts, and public-safe summaries only; raw decompile/read-back files remain ignored under subagents/.",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--metadata-before", type=Path, default=DEFAULT_METADATA_BEFORE)
    parser.add_argument("--metadata-final", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--instructions", type=Path, default=DEFAULT_INSTRUCTIONS)
    parser.add_argument("--queue-json", type=Path, default=DEFAULT_QUEUE_JSON)
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
        metadata_before_path=args.metadata_before,
        metadata_final_path=args.metadata_final,
        decompile_index_path=args.decompile_index,
        decompile_dir=args.decompile_dir,
        xrefs_path=args.xrefs,
        instructions_path=args.instructions,
        queue_json_path=args.queue_json,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("Ghidra cockpit/volume/UnitAI signature correction probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Targets: {report['signatureCorrectedTargets']}/{report['targetCount']}")
        print(f"Renamed targets: {report['renamedTargets']}")
        print(f"Queue commentless functions: {report['queueCommentlessFunctions']}")
        print(f"Queue undefined signatures: {report['queueUndefinedSignatures']}")
        print(f"Queue param signatures: {report['queueParamSignatures']}")
        for failure in report["failures"]:
            print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
