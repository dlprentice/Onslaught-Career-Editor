#!/usr/bin/env python3
"""Validate the saved transition/targeting Ghidra signature tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "transition-targeting-signature-tranche" / "current"

TARGETS = {
    "0x0040a580": {
        "name": "CBattleEngine__Morph",
        "previousName": "CMonitor__UpdateFlightWalkerTransitionState",
        "signatureTokens": ["void", "__fastcall", "CBattleEngine__Morph", "void * battleEngine"],
        "forbiddenSignatureTokens": ["CMonitor__UpdateFlightWalkerTransitionState", "param_1"],
        "commentTokens": ["Source bridge/name correction", "CBattleEngine::Morph", "special-move lockouts", "0x1771", "6000", "flytowalk/walktofly", "runtime behavior", "remain unproven"],
        "decompileTokens": ["battleEngine", "+0x260", "CGeneralVolume__BeginFlyToWalkTransition", "CGeneralVolume__BeginWalkToFlyTransition", "s_flytowalk", "s_walktofly", "CBattleEngine__SwapPrimarySecondaryPartReadersForState"],
        "instructionRet": "",
    },
    "0x0040ac50": {
        "name": "CBattleEngine__Rearm",
        "previousName": "CGeneralVolume__IntegrateSlotAccumulators",
        "signatureTokens": ["void", "__thiscall", "CBattleEngine__Rearm", "void * this", "float inAmount"],
        "forbiddenSignatureTokens": ["CGeneralVolume__IntegrateSlotAccumulators", "param_1", "param_2", "int inAmount"],
        "commentTokens": ["Source bridge/name correction", "CBattleEngine::Rearm", "ret 0x4", "inAmount", "six stores", "heated stores", "runtime behavior", "remain unproven"],
        "decompileTokens": ["this", "inAmount", "+0x52c", "+0x4b0"],
        "instructionRet": "0x4",
    },
    "0x0040acc0": {
        "name": "CBattleEngine__CalcUnitOverCrossHair",
        "previousName": "CBattleEngine__SelectBestAimTargetAndMaybeQueueEvent",
        "signatureTokens": ["void *", "__thiscall", "CBattleEngine__CalcUnitOverCrossHair", "void * this", "void * event", "int useMeshCollision", "int updateReaders"],
        "forbiddenSignatureTokens": ["CBattleEngine__SelectBestAimTargetAndMaybeQueueEvent", "event_payload", "query_context", "trace_mode", "param_"],
        "commentTokens": ["Source bridge/name correction", "CBattleEngine::CalcUnitOverCrossHair", "ret 0xc", "view ray", "mesh/outer-sphere", "event 0x1772", "runtime behavior", "remain unproven"],
        "decompileTokens": ["this", "event", "useMeshCollision", "updateReaders", "CPlayer__GetCurrentViewPoint", "CPlayer__GetCurrentViewOrientation", "OID__TraceLineAndSelectBestTargetHit", "CEventManager__AddEvent_AtTime", "0x1772"],
        "instructionRet": "0xc",
    },
    "0x0040b100": {
        "name": "CGeneralVolume__ctor_base",
        "previousName": "CGeneralVolume__ctor_zero_fields",
        "signatureTokens": ["void", "__fastcall", "CGeneralVolume__ctor_base", "void * generalVolume"],
        "forbiddenSignatureTokens": ["CGeneralVolume__ctor_like_0040b100", "CGeneralVolume__ctor_zero_fields", "param_1"],
        "commentTokens": ["Owner/name correction", "CGeneralVolume vtable", "zeroes +0x4/+0x8/+0xc", "ResolveVtableTypeNames", "runtime behavior", "remain unproven"],
        "decompileTokens": ["generalVolume", "PTR_LAB_005d892c"],
        "instructionRet": "",
        "vtable": "0x005d892c",
        "vtableType": "CGeneralVolume",
    },
    "0x0040b120": {
        "name": "CBattleEngine__UpdateAutoAim",
        "previousName": "CMonitor__UpdateTargetTrackingAimOffsets",
        "signatureTokens": ["void", "__fastcall", "CBattleEngine__UpdateAutoAim", "void * battleEngine"],
        "forbiddenSignatureTokens": ["CMonitor__UpdateTargetTrackingAimOffsets", "param_1"],
        "commentTokens": ["Source bridge/name correction", "CBattleEngine::UpdateAutoAim", "+0x4e8/+0x4f4", "AngleDifference", "runtime behavior", "remain unproven"],
        "decompileTokens": ["battleEngine", "+0x4e4", "+0x4f0", "CUnitAI__GetWorldPositionForTargeting", "AngleDifference"],
        "instructionRet": "",
    },
    "0x0040b660": {
        "name": "AngleDifference",
        "previousName": "Math__GetSignedWrappedAngleDelta",
        "signatureTokens": ["float", "__cdecl", "AngleDifference", "float currentAngle", "float targetAngle"],
        "forbiddenSignatureTokens": ["CGeneralVolume__GetWrappedDeltaSigned", "Math__GetSignedWrappedAngleDelta", "param_1", "param_2"],
        "commentTokens": ["Source bridge/name correction", "AngleDifference", "signed wrapped angular delta", "two float inputs", "not CGeneralVolume-owned", "runtime behavior", "remain unproven"],
        "decompileTokens": ["currentAngle", "targetAngle", "_DAT_005d85e0"],
        "instructionRet": "",
    },
    "0x0040b6d0": {
        "name": "CBattleEngine__HandleAutoAim",
        "previousName": "CBattleEngine__AcquireTargetWithBallisticConstraints",
        "signatureTokens": ["void", "__thiscall", "CBattleEngine__HandleAutoAim", "void * this", "void * event"],
        "forbiddenSignatureTokens": ["CBattleEngine__AcquireTargetWithBallisticConstraints", "eventContext", "param_1", "param_2"],
        "commentTokens": ["Source bridge/name correction", "CBattleEngine::HandleAutoAim", "ret 0x4", "target reader +0x4e0", "MapWho", "line trace", "0x1773", "runtime behavior"],
        "decompileTokens": ["this", "event", "CGenericActiveReader__SetReader", "CUnit__ComputeMinBallisticTravelDistance", "CUnit__ComputeMaxBallisticTravelDistance", "OID__TraceLineAndSelectBestTargetHit", "CEventManager__AddEvent_AtTime"],
        "instructionRet": "0x4",
    },
}

DEFAULT_DRY = BASE / "signature_dry.log"
DEFAULT_APPLY = BASE / "signature_apply.log"
DEFAULT_METADATA = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_VTABLES = BASE / "vtables_final.tsv"
DEFAULT_OUT = BASE / "transition-targeting-signature-tranche.json"

OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "exact source identity proven",
    "concrete layout proven",
    "tagged in ghidra",
    "rebuild parity proven",
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


def compact(value: str) -> str:
    return "".join(value.lower().split())


def token_present(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def read_text(path: Path | None) -> str:
    if path is None or not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def parse_update_summary(log_text: str) -> dict[str, int]:
    match = re.search(r"updated=(\d+)\s+skipped=(\d+)\s+missing=(\d+)\s+bad=(\d+)", log_text)
    if not match:
        return {"updated": -1, "skipped": -1, "missing": -1, "bad": -1}
    return {
        "updated": int(match.group(1)),
        "skipped": int(match.group(2)),
        "missing": int(match.group(3)),
        "bad": int(match.group(4)),
    }


def clean_dry_summary(summary: dict[str, int], target_count: int) -> bool:
    return summary.get("updated") == 0 and summary.get("skipped", -1) >= target_count and summary.get("missing") == 0 and summary.get("bad") == 0


def clean_apply_summary(summary: dict[str, int], target_count: int) -> bool:
    return summary.get("updated", -1) + summary.get("skipped", -1) >= target_count and summary.get("missing") == 0 and summary.get("bad") == 0


def find_row(rows: list[dict[str, str]], key: str, address: str) -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(key, "")) == wanted:
            return row
    return None


def find_vtable_row(rows: list[dict[str, str]], address: str) -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get("vtable", "")) == wanted:
            return row
    return None


def decompile_file_for(decompile_dir: Path, address: str) -> Path | None:
    if not decompile_dir.is_dir():
        return None
    matches = sorted(decompile_dir.glob(f"{normalize_address(address)[2:]}_*.c"))
    return matches[0] if matches else None


def matching_ret_rows(instruction_rows: list[dict[str, str]], address: str, operand: str) -> list[dict[str, str]]:
    wanted = normalize_address(address)
    return [
        row for row in instruction_rows
        if normalize_address(row.get("target_addr", "")) == wanted
        and normalize_address(row.get("function_entry", "")) == wanted
        and row.get("mnemonic", "").upper() == "RET"
        and row.get("operands", "") == operand
    ]


def build_report(
    *,
    dry_log_path: Path = DEFAULT_DRY,
    apply_log_path: Path = DEFAULT_APPLY,
    metadata_path: Path = DEFAULT_METADATA,
    decompile_index_path: Path = DEFAULT_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
    vtables_path: Path = DEFAULT_VTABLES,
) -> dict[str, object]:
    dry_log_path = resolve(dry_log_path)
    apply_log_path = resolve(apply_log_path)
    metadata_path = resolve(metadata_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)
    vtables_path = resolve(vtables_path)

    failures: list[str] = []
    for label, path in (
        ("dry log", dry_log_path),
        ("apply log", apply_log_path),
        ("metadata", metadata_path),
        ("decompile index", decompile_index_path),
        ("xrefs", xrefs_path),
        ("instructions", instructions_path),
        ("vtables", vtables_path),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")
    if not decompile_dir.is_dir():
        failures.append(f"missing decompile dir: {relative(decompile_dir)}")

    dry_summary = parse_update_summary(read_text(dry_log_path))
    apply_summary = parse_update_summary(read_text(apply_log_path))
    if not clean_dry_summary(dry_summary, len(TARGETS)):
        failures.append("dry summary is not clean")
    if not clean_apply_summary(apply_summary, len(TARGETS)):
        failures.append("apply summary is not clean")

    metadata_rows = read_tsv(metadata_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)
    vtable_rows = read_tsv(vtables_path)

    target_reports: list[dict[str, object]] = []
    param_signature_hits = 0
    comment_overclaims = 0
    ret_evidence_hits = 0
    vtable_evidence_hits = 0
    renamed_targets = 0

    for address, expected in TARGETS.items():
        row = find_row(metadata_rows, "address", address)
        index_row = find_row(index_rows, "address", address)
        if row is None:
            failures.append(f"metadata missing {address}")
            continue

        signature = row.get("signature", "")
        comment = row.get("comment", "")
        if row.get("name") != expected["name"] or row.get("status") != "OK":
            failures.append(f"name/status mismatch for {address}: {row.get('name')}")
        if expected.get("previousName"):
            renamed_targets += 1
            if token_present(signature, str(expected["previousName"])):
                failures.append(f"previous name remains in signature at {address}")
        if "param_" in signature:
            param_signature_hits += 1
            failures.append(f"param_N signature remains at {address}")
        for forbidden in expected.get("forbiddenSignatureTokens", []):
            if token_present(signature, str(forbidden)):
                param_signature_hits += 1
                failures.append(f"forbidden signature token remains at {address}: {forbidden}")

        missing_signature_tokens = [token for token in expected["signatureTokens"] if not token_present(signature, token)]
        if missing_signature_tokens:
            failures.append(f"signature tokens missing at {address}: {missing_signature_tokens}")

        missing_comment_tokens = [token for token in expected["commentTokens"] if not token_present(comment, token)]
        if missing_comment_tokens:
            failures.append(f"comment tokens missing at {address}: {missing_comment_tokens}")

        lowered_comment = comment.lower()
        if any(token in lowered_comment for token in OVERCLAIM_TOKENS):
            comment_overclaims += 1
            failures.append(f"runtime/source overclaim in comment at {address}")

        if index_row is None or index_row.get("status") != "OK":
            failures.append(f"decompile index missing/failed for {address}")

        decompile_file = decompile_file_for(decompile_dir, address)
        decompile_text = read_text(decompile_file)
        missing_decompile_tokens = [token for token in expected["decompileTokens"] if not token_present(decompile_text, token)]
        if missing_decompile_tokens:
            failures.append(f"decompile tokens missing at {address}: {missing_decompile_tokens}")

        ret_rows = matching_ret_rows(instruction_rows, address, str(expected["instructionRet"]))
        if ret_rows:
            ret_evidence_hits += 1
        else:
            failures.append(f"RET evidence missing at {address}: {expected['instructionRet']!r}")

        vtable_row = None
        if expected.get("vtable"):
            vtable_row = find_vtable_row(vtable_rows, str(expected["vtable"]))
            if vtable_row is None or vtable_row.get("demangled_type_name") != expected.get("vtableType"):
                failures.append(f"vtable RTTI evidence missing at {address}: {expected.get('vtable')}")
            else:
                vtable_evidence_hits += 1

        target_reports.append({
            "address": address,
            "name": row.get("name"),
            "previousName": expected.get("previousName"),
            "signature": signature,
            "commented": bool(comment.strip()),
            "xrefs": len([xref for xref in xref_rows if normalize_address(xref.get("target_addr", "")) == normalize_address(address)]),
            "retEvidenceRows": len(ret_rows),
            "vtableType": vtable_row.get("demangled_type_name") if vtable_row else None,
            "decompile": relative(decompile_file),
        })

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-transition-targeting-signature-tranche.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "inputs": {
            "dryLog": relative(dry_log_path),
            "applyLog": relative(apply_log_path),
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
            "vtables": relative(vtables_path),
        },
        "summary": {
            "targets": len(TARGETS),
            "renamedTargets": renamed_targets,
            "paramSignatureHits": param_signature_hits,
            "commentOverclaims": comment_overclaims,
            "retEvidenceHits": ret_evidence_hits,
            "vtableEvidenceHits": vtable_evidence_hits,
            "xrefRows": len(xref_rows),
            "instructionRows": len(instruction_rows),
        },
        "targets": target_reports,
        "failures": failures,
        "whatIsProven": [
            "Seven selected transition/targeting-adjacent Ghidra functions have saved names, signatures, and comments matching the checked read-back artifacts.",
            "The tranche corrects 0x0040a580 to the source-backed CBattleEngine::Morph bridge.",
            "The tranche corrects 0x0040ac50 to the source-backed CBattleEngine::Rearm bridge.",
            "The tranche corrects 0x0040acc0 to the source-backed CBattleEngine::CalcUnitOverCrossHair bridge.",
            "The tranche corrects 0x0040b100 to a CGeneralVolume zero-field constructor label using vtable/RTTI evidence.",
            "The tranche corrects 0x0040b120 and 0x0040b6d0 to the source-backed CBattleEngine::UpdateAutoAim and CBattleEngine::HandleAutoAim bridges.",
            "The tranche corrects 0x0040b660 away from a CGeneralVolume owner label to the source-backed AngleDifference helper.",
            "The comments preserve runtime/source/layout/tag proof boundaries.",
        ],
        "notProven": [
            "This does not prove concrete CGeneralVolume, CBattleEngine, weapon, target-reader, or line/collision layouts.",
            "This does not prove runtime targeting behavior, runtime transform behavior, tags, local names, or rebuild parity.",
            "This does not launch, patch, or mutate BEA.exe.",
        ],
        "privacy": "Report stores repo-relative artifact paths, public addresses, names, signatures, counts, and explicit proof boundaries only. Raw decompile artifacts remain ignored under subagents/.",
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--dry-log", type=Path, default=DEFAULT_DRY)
    parser.add_argument("--apply-log", type=Path, default=DEFAULT_APPLY)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--instructions", type=Path, default=DEFAULT_INSTRUCTIONS)
    parser.add_argument("--vtables", type=Path, default=DEFAULT_VTABLES)
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
        dry_log_path=args.dry_log,
        apply_log_path=args.apply_log,
        metadata_path=args.metadata,
        decompile_index_path=args.decompile_index,
        decompile_dir=args.decompile_dir,
        xrefs_path=args.xrefs,
        instructions_path=args.instructions,
        vtables_path=args.vtables,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        summary = report["summary"]
        print("Ghidra transition/targeting signature tranche probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Targets: {summary['targets']}")
        print(f"Renamed targets: {summary['renamedTargets']}")
        print(f"Param signature hits: {summary['paramSignatureHits']}")
        print(f"Comment overclaims: {summary['commentOverclaims']}")
        print(f"RET evidence hits: {summary['retEvidenceHits']}")
        print(f"Vtable evidence hits: {summary['vtableEvidenceHits']}")
        print(f"Xref rows: {summary['xrefRows']}")
        print(f"Instruction rows: {summary['instructionRows']}")
        for failure in report["failures"]:
            print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
