#!/usr/bin/env python3
"""Validate the saved vector/geometry Ghidra signature tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "vector-geometry-signature-tranche" / "current"

TARGETS = {
    "0x0040d120": {
        "name": "Vec3__SubtractToOut",
        "signatureTokens": ["void", "__thiscall", "Vec3__SubtractToOut", "void * this", "void * outVec", "void * rhs"],
        "forbiddenSignatureTokens": ["param_1", "param_2", "param_3"],
        "commentTokens": ["Signature hardening", "Vec3 subtract", "outVec", "rhs", "ret 0x8", "Not concrete Vec3 layout"],
        "decompileTokens": ["Vec3__SubtractToOut", "outVec", "rhs"],
        "instructionRet": "0x8",
    },
    "0x0040d150": {
        "name": "Vec3__ScaleToOut",
        "signatureTokens": ["void", "__thiscall", "Vec3__ScaleToOut", "void * this", "void * outVec", "float scale"],
        "forbiddenSignatureTokens": ["param_1", "param_2", "param_3"],
        "commentTokens": ["Signature hardening", "Vec3 scale", "outVec", "scale", "ret 0x8", "Not concrete Vec3 layout"],
        "decompileTokens": ["Vec3__ScaleToOut", "outVec", "scale"],
        "instructionRet": "0x8",
    },
    "0x0040d180": {
        "name": "Vec3__Dot",
        "signatureTokens": ["double", "__thiscall", "Vec3__Dot", "void * this", "void * rhs"],
        "forbiddenSignatureTokens": ["param_1", "param_2"],
        "commentTokens": ["Signature hardening", "Vec3 dot", "rhs", "ret 0x4", "Not concrete Vec3 layout"],
        "decompileTokens": ["Vec3__Dot", "rhs"],
        "instructionRet": "0x4",
    },
    "0x0040d1a0": {
        "name": "Vec3__ElevationOrZero",
        "previousName": "CMonitor__ComputeVectorLengthOrZero",
        "signatureTokens": ["double", "__fastcall", "Vec3__ElevationOrZero", "void * vec"],
        "forbiddenSignatureTokens": ["CMonitor__ComputeVectorLengthOrZero", "param_1"],
        "commentTokens": ["Owner/name correction", "vector-angle helper", "z over length", "OID__AcosWrapper", "FVector::Elevation", "remain unproven"],
        "decompileTokens": ["Vec3__ElevationOrZero", "vec", "SQRT", "OID__AcosWrapper"],
        "instructionRet": "",
    },
    "0x0040d1f0": {
        "name": "Mat34__SetFromEulerAngles",
        "previousName": "OID__BuildOrientationMatrixFromEuler",
        "signatureTokens": ["void", "__thiscall", "Mat34__SetFromEulerAngles", "void * this", "float angle0", "float angle1", "float angle2"],
        "forbiddenSignatureTokens": ["OID__BuildOrientationMatrixFromEuler", "param_1", "param_2", "param_3", "param_4"],
        "commentTokens": ["Owner/name correction", "matrix builder", "cos/sin", "three stack float angles", "ret 0xc", "Broad xrefs"],
        "decompileTokens": ["Mat34__SetFromEulerAngles", "angle0", "angle1", "angle2", "fcos", "fsin"],
        "instructionRet": "0xc",
    },
    "0x0040d2c0": {
        "name": "Mat34__TransformVec3ByBasisToOut",
        "previousName": "CSquadNormal__TransformVec3ByOrientationMatrix",
        "signatureTokens": ["void", "__thiscall", "Mat34__TransformVec3ByBasisToOut", "void * this", "void * outVec", "void * vec"],
        "forbiddenSignatureTokens": ["CSquadNormal__TransformVec3ByOrientationMatrix", "param_1", "param_2", "param_3"],
        "commentTokens": ["Owner/name correction", "basis-transform helper", "+0x0/+0x10/+0x20", "outVec", "ret 0x8", "does not prove translation"],
        "decompileTokens": ["Mat34__TransformVec3ByBasisToOut", "outVec", "vec"],
        "instructionRet": "0x8",
    },
}

DEFAULT_DRY = BASE / "signature_dry.log"
DEFAULT_APPLY = BASE / "signature_apply.log"
DEFAULT_METADATA = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_OUT = BASE / "vector-geometry-signature-tranche.json"

STALE_TOKENS = [
    "CMonitor__ComputeVectorLengthOrZero",
    "OID__BuildOrientationMatrixFromEuler",
    "CSquadNormal__TransformVec3ByOrientationMatrix",
    "param_1",
    "param_2",
    "param_3",
    "param_4",
]

OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "source identity proven",
    "exact source identity proven",
    "concrete vec3 layout proven",
    "concrete mat34 layout proven",
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


def find_row(rows: list[dict[str, str]], key: str, address: str) -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(key, "")) == wanted:
            return row
    return None


def decompile_file_for(decompile_dir: Path, address: str) -> Path | None:
    if not decompile_dir.is_dir():
        return None
    matches = sorted(decompile_dir.glob(f"{normalize_address(address)[2:]}_*.c"))
    return matches[0] if matches else None


def rows_for(rows: list[dict[str, str]], address: str) -> list[dict[str, str]]:
    wanted = normalize_address(address)
    return [row for row in rows if normalize_address(row.get("target_addr", "")) == wanted]


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
) -> dict[str, object]:
    dry_log_path = resolve(dry_log_path)
    apply_log_path = resolve(apply_log_path)
    metadata_path = resolve(metadata_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)

    failures: list[str] = []
    for label, path in (
        ("dry log", dry_log_path),
        ("apply log", apply_log_path),
        ("metadata", metadata_path),
        ("decompile index", decompile_index_path),
        ("xrefs", xrefs_path),
        ("instructions", instructions_path),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")
    if not decompile_dir.is_dir():
        failures.append(f"missing decompile dir: {relative(decompile_dir)}")

    dry_summary = parse_update_summary(read_text(dry_log_path))
    apply_summary = parse_update_summary(read_text(apply_log_path))
    expected_count = len(TARGETS)
    if dry_summary != {"updated": 0, "skipped": expected_count, "missing": 0, "bad": 0}:
        failures.append(f"dry summary mismatch: {dry_summary}")
    if apply_summary != {"updated": expected_count, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append(f"apply summary mismatch: {apply_summary}")

    metadata_rows = read_tsv(metadata_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)

    target_reports: list[dict[str, object]] = []
    renamed_targets = 0
    signature_hardened = 0
    param_signature_hits = 0
    comment_overclaims = 0
    stale_hits: list[str] = []
    overclaim_hits: list[str] = []
    ret_evidence_hits = 0

    for address, expected in TARGETS.items():
        meta = find_row(metadata_rows, "address", address)
        index = find_row(index_rows, "address", address)
        decompile_path = decompile_file_for(decompile_dir, address)
        decompile_text = read_text(decompile_path)

        if meta is None:
            failures.append(f"metadata missing {address}")
            continue
        if index is None or index.get("status") != "OK":
            failures.append(f"decompile index missing/failed for {address}")
        if decompile_path is None:
            failures.append(f"missing decompile file for {address}")

        if expected.get("previousName"):
            renamed_targets += 1
        if meta.get("name") != expected["name"] or meta.get("status") != "OK":
            failures.append(f"name/status mismatch for {address}: {meta.get('name')}")

        signature = meta.get("signature", "")
        missing_signature = [token for token in expected["signatureTokens"] if not token_present(signature, token)]
        if missing_signature:
            failures.append(f"signature tokens missing at {address}: {missing_signature}")
        else:
            signature_hardened += 1

        if "param_" in signature:
            param_signature_hits += 1
            failures.append(f"param_N signature remains at {address}")
        for forbidden in expected.get("forbiddenSignatureTokens", []):
            if token_present(signature, str(forbidden)):
                param_signature_hits += 1
                failures.append(f"forbidden signature token remains at {address}: {forbidden}")

        comment = meta.get("comment", "")
        missing_comment = [token for token in expected["commentTokens"] if not token_present(comment, token)]
        if missing_comment:
            failures.append(f"comment tokens missing at {address}: {missing_comment}")

        missing_decompile = [token for token in expected["decompileTokens"] if not token_present(decompile_text, token)]
        if missing_decompile:
            failures.append(f"decompile tokens missing at {address}: {missing_decompile}")
        if not rows_for(xref_rows, address):
            failures.append(f"{address} has no xref rows")
        if not rows_for(instruction_rows, address):
            failures.append(f"{address} has no instruction rows")

        ret_rows = matching_ret_rows(instruction_rows, address, str(expected["instructionRet"]))
        if ret_rows:
            ret_evidence_hits += 1
        else:
            failures.append(f"RET evidence missing at {address}: {expected['instructionRet']!r}")

        combined = "\n".join([meta.get("name", ""), signature, comment, decompile_text])
        for token in STALE_TOKENS:
            if token_present(combined, token):
                stale_hits.append(f"{address}:{token}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                overclaim_hits.append(f"{address}:{token}")

        target_reports.append({
            "address": address,
            "name": meta.get("name"),
            "previousName": expected.get("previousName"),
            "signature": signature,
            "commented": bool(comment.strip()),
            "xrefs": len(rows_for(xref_rows, address)),
            "retEvidenceRows": len(ret_rows),
            "decompile": relative(decompile_path),
        })

    for hit in stale_hits:
        failures.append(f"stale token observed: {hit}")
    for hit in overclaim_hits:
        comment_overclaims += 1
        failures.append(f"overclaim token observed: {hit}")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-vector-geometry-signature-tranche.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "inputs": {
            "dryLog": relative(dry_log_path),
            "applyLog": relative(apply_log_path),
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
        },
        "summary": {
            "targets": expected_count,
            "renamedTargets": renamed_targets,
            "signatureHardenedTargets": signature_hardened,
            "paramSignatureHits": param_signature_hits,
            "commentOverclaims": comment_overclaims,
            "staleTokenHits": len(stale_hits),
            "retEvidenceHits": ret_evidence_hits,
            "xrefRows": len(xref_rows),
            "instructionRows": len(instruction_rows),
        },
        "targets": target_reports,
        "failures": failures,
        "whatIsProven": [
            "Six selected vector/geometry Ghidra functions have saved names, signatures, and comments matching the checked read-back artifacts.",
            "The tranche hardens Vec3 subtract, scale, and dot helper stack argument signatures.",
            "The tranche corrects the old CMonitor/OID/CSquadNormal owner labels to behavior-scoped vector and matrix helper names.",
            "Read-back xrefs and instruction rows support the helper nature and return arities for the selected functions.",
            "The comments preserve source/layout/tag/runtime proof boundaries.",
        ],
        "notProven": [
            "This does not prove concrete Vec3, FMatrix, or Mat34 layouts.",
            "This does not prove exact Stuart source identity, angle order, translation semantics, tags, local variable names, or type recovery.",
            "This does not prove runtime behavior, launch BEA.exe, patch BEA.exe, or prove rebuild parity.",
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
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        summary = report["summary"]
        print("Ghidra vector/geometry signature tranche probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Targets: {summary['targets']}")
        print(f"Renamed targets: {summary['renamedTargets']}")
        print(f"Signature-hardened targets: {summary['signatureHardenedTargets']}")
        print(f"Param signature hits: {summary['paramSignatureHits']}")
        print(f"Comment overclaims: {summary['commentOverclaims']}")
        print(f"Stale token hits: {summary['staleTokenHits']}")
        print(f"RET evidence hits: {summary['retEvidenceHits']}")
        print(f"Xref rows: {summary['xrefRows']}")
        print(f"Instruction rows: {summary['instructionRows']}")
        for failure in report["failures"]:
            print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
