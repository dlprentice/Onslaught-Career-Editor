#!/usr/bin/env python3
"""Validate the saved early-helper Ghidra signature tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "early-helper-signature-tranche" / "current"

TARGETS = {
    "0x004062d0": {
        "name": "CSquadNormal__BuildOrientationMatrixFromEuler",
        "signatureTokens": [
            "void",
            "__thiscall",
            "CSquadNormal__BuildOrientationMatrixFromEuler",
            "void * this",
            "float angle0",
            "float angle1",
            "float angle2",
        ],
        "forbiddenSignatureTokens": ["void * outMatrix"],
        "commentTokens": ["Signature hardening", "ret 0xc", "matrix rows", "this/outMatrix", "+0x28", "source identity", "remain unproven"],
        "decompileTokens": ["this", "angle0", "angle1", "angle2", "fcos", "fsin"],
        "instructionRet": "0xc",
    },
    "0x00406d50": {
        "name": "Vec3__NormalizeInPlace",
        "signatureTokens": ["void", "__fastcall", "Vec3__NormalizeInPlace", "void * vec"],
        "commentTokens": ["Signature hardening", "normalizes", "+0x0/+0x4/+0x8", "zero-length", "runtime behavior", "remain unproven"],
        "decompileTokens": ["vec", "SQRT", "_DAT_005d8568"],
        "instructionRet": None,
        "forbiddenSignatureTokens": [],
    },
    "0x00407060": {
        "name": "CEngine__MoveBurstReaderToCooldownSet",
        "signatureTokens": ["void", "__thiscall", "CEngine__MoveBurstReaderToCooldownSet", "void * this", "int readerId"],
        "commentTokens": ["Signature hardening", "ret 0x4", "active set +0x294", "cooldown set +0x2a4", "reader layout", "remain unproven"],
        "decompileTokens": ["readerId", "CSPtrSet__Remove", "CSPtrSet__AddToHead", "CGenericActiveReader__dtor", "OID__FreeObject"],
        "instructionRet": "0x4",
        "forbiddenSignatureTokens": [],
    },
    "0x00407140": {
        "name": "CMonitor__RemoveActiveReaderById",
        "signatureTokens": ["void", "__thiscall", "CMonitor__RemoveActiveReaderById", "void * this", "int readerId"],
        "commentTokens": ["Signature hardening", "ret 0x4", "cooldown set +0x2a4", "CGenericActiveReader__dtor", "runtime behavior", "remain unproven"],
        "decompileTokens": ["readerId", "CSPtrSet__Remove", "CGenericActiveReader__dtor", "OID__FreeObject"],
        "instructionRet": "0x4",
        "forbiddenSignatureTokens": [],
    },
    "0x00407310": {
        "name": "CBattleEngine__IsCurrentResolvedEntry",
        "signatureTokens": ["bool", "__thiscall", "CBattleEngine__IsCurrentResolvedEntry", "void * this", "void * expectedEntry"],
        "commentTokens": ["Signature hardening", "ret 0x4", "current resolved entry", "+0x57c", "+0x578", "entry type", "remain unproven"],
        "decompileTokens": ["expectedEntry", "CBattleEngine__GetIndexedEntry", "CGeneralVolume__ResolveCurrentOrFallbackEntry"],
        "instructionRet": "0x4",
        "forbiddenSignatureTokens": [],
    },
    "0x00407540": {
        "name": "CGame__UpdateMouseLookAngles",
        "signatureTokens": ["void", "__fastcall", "CGame__UpdateMouseLookAngles", "void * battleEngine"],
        "commentTokens": ["Signature hardening", "historical behavior label", "mouse-look", "g_MouseSensitivity", "runtime behavior", "remain unproven"],
        "decompileTokens": [
            "battleEngine",
            "g_MouseSensitivity",
            "PLATFORM__GetWindowWidth",
            "CSquadNormal__BuildOrientationMatrixFromEuler",
            "Vec3__NormalizeInPlace",
        ],
        "instructionRet": None,
        "forbiddenSignatureTokens": [],
    },
}

DEFAULT_DRY = BASE / "signature_dry.log"
DEFAULT_APPLY = BASE / "signature_apply.log"
DEFAULT_METADATA = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_OUT = BASE / "early-helper-signature-tranche.json"

OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "exact source identity proven",
    "concrete layout proven",
    "entry type proven",
    "reader layout proven",
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
        and row.get("mnemonic") == "RET"
        and row.get("operands") == operand
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
    if not clean_dry_summary(dry_summary, len(TARGETS)):
        failures.append("dry summary is not clean")
    if not clean_apply_summary(apply_summary, len(TARGETS)):
        failures.append("apply summary is not clean")

    metadata_rows = read_tsv(metadata_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)

    target_reports: list[dict[str, object]] = []
    param_signature_hits = 0
    comment_overclaims = 0
    ret_evidence_hits = 0

    for address, expected in TARGETS.items():
        row = find_row(metadata_rows, "address", address)
        index_row = find_row(index_rows, "address", address)
        if row is None:
            failures.append(f"metadata missing {address}")
            continue

        signature = row.get("signature", "")
        comment = row.get("comment", "")
        if row.get("name") != expected["name"] or row.get("status") != "OK":
            failures.append(f"name/status mismatch for {address}")
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

        if any(token in comment.lower() for token in OVERCLAIM_TOKENS):
            comment_overclaims += 1
            failures.append(f"runtime/source overclaim in comment at {address}")

        if index_row is None or index_row.get("name") != expected["name"] or index_row.get("status") != "OK":
            failures.append(f"decompile index mismatch for {address}")

        decompile_file = decompile_file_for(decompile_dir, address)
        decompile_text = read_text(decompile_file)
        if not decompile_file:
            failures.append(f"missing decompile file for {address}")
        else:
            missing_decompile_tokens = [token for token in expected["decompileTokens"] if not token_present(decompile_text, token)]
            if missing_decompile_tokens:
                failures.append(f"decompile tokens missing at {address}: {missing_decompile_tokens}")

        ret_operand = expected.get("instructionRet")
        if ret_operand:
            rows = matching_ret_rows(instruction_rows, address, str(ret_operand))
            if rows:
                ret_evidence_hits += 1
            else:
                failures.append(f"RET {ret_operand} evidence missing for {address}")

        target_reports.append(
            {
                "address": address,
                "name": row.get("name"),
                "signature": signature,
                "commentPresent": bool(comment),
                "xrefRows": sum(1 for xref in xref_rows if normalize_address(xref.get("target_addr", "")) == normalize_address(address)),
            }
        )

    report = {
        "status": "PASS" if not failures else "FAIL",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "classification": "early-helper-signature-tranche-saved" if not failures else "early-helper-signature-tranche-invalid",
        "summary": {
            "targets": len(TARGETS),
            "paramSignatureHits": param_signature_hits,
            "commentOverclaims": comment_overclaims,
            "xrefRows": len(xref_rows),
            "instructionRows": len(instruction_rows),
            "retEvidenceHits": ret_evidence_hits,
        },
        "summaries": {
            "dry": dry_summary,
            "apply": apply_summary,
        },
        "targets": target_reports,
        "files": {
            "dryLog": relative(dry_log_path),
            "applyLog": relative(apply_log_path),
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
        },
        "notProven": [
            "exact Stuart source method identities for the helper tranche",
            "concrete object, entry, reader, or matrix structure layouts",
            "local variable names, tags, and full type recovery",
            "runtime mouse-look, projectile-reader, or entry-resolution behavior",
            "rebuild parity",
        ],
        "failures": failures,
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Exit non-zero when validation fails.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Write report JSON to this path.")
    args = parser.parse_args()

    report = build_report()
    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("Ghidra early-helper signature tranche probe")
    print(f"Status: {report['status']}")
    print(f"Output: {relative(out_path)}")
    print(
        "Targets: {targets}; param signatures: {paramSignatureHits}; xref rows: {xrefRows}; RET evidence hits: {retEvidenceHits}".format(
            **report["summary"]
        )
    )
    if report["failures"]:
        print("Failures:")
        for failure in report["failures"]:
            print(f"- {failure}")

    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
