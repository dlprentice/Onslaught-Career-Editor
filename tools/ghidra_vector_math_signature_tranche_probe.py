#!/usr/bin/env python3
"""Validate the saved vector/math signature-hardening tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "signature-debt-tranche5" / "current"

TARGETS = {
    "0x00401b50": {
        "name": "CMCMine__ComputeClampedScaleFactor",
        "signatureTokens": ["double", "__fastcall", "CMCMine__ComputeClampedScaleFactor", "void * this"],
        "commentTokens": ["Signature hardening", "vfunc +0x60", "+0xd8", "Not exact class layout"],
        "instructionTokens": ["ECX", "+ 0x60", "+ 0xd8"],
        "decompileTokens": ["CMCMine__ComputeClampedScaleFactor", "+ 0xd8"],
    },
    "0x00401ec0": {
        "name": "Vec3__SetXYZ",
        "signatureTokens": ["void", "__thiscall", "Vec3__SetXYZ", "void * this", "float x", "float y", "float z"],
        "commentTokens": ["Signature hardening", "Vec3 setter", "ret 0xc", "Not concrete FVector"],
        "instructionTokens": ["[ESP + 0x4]", "[ESP + 0x8]", "[ESP + 0xc]", "RET", "0xc"],
        "decompileTokens": ["Vec3__SetXYZ", "float x", "float y", "float z"],
    },
    "0x00401ee0": {
        "name": "Vec3__Add",
        "signatureTokens": ["void", "__thiscall", "Vec3__Add", "void * this", "void * outVec", "void * rhs"],
        "commentTokens": ["Signature hardening", "Vec3 add", "ret 0x8", "Not exact source identity"],
        "instructionTokens": ["[ESP + 0x4]", "[ESP + 0x8]", "RET", "0x8"],
        "decompileTokens": ["Vec3__Add", "outVec", "rhs"],
    },
    "0x00401f10": {
        "name": "Mat34__SetRows",
        "signatureTokens": ["void", "__thiscall", "Mat34__SetRows", "void * this", "void * row0", "void * row1", "void * row2"],
        "commentTokens": ["Signature hardening", "Mat34 row setter", "ret 0xc", "Not concrete matrix layout"],
        "instructionTokens": ["[ESP + 0x8]", "[ESP + 0xc]", "[ESP + 0x10]", "RET", "0xc"],
        "decompileTokens": ["Mat34__SetRows", "row0", "row1", "row2"],
    },
    "0x00401fa0": {
        "name": "HeightDelta__Below025_D0",
        "signatureTokens": ["bool", "__fastcall", "HeightDelta__Below025_D0", "void * this"],
        "commentTokens": ["Signature hardening", "height-delta predicate", "ECX+0xd0", "Not exact owner"],
        "instructionTokens": ["[ECX + 0xd0]", "MOV", "0x1"],
        "decompileTokens": ["HeightDelta__Below025_D0", "+ 0xd0"],
    },
    "0x00401fd0": {
        "name": "HeightDelta__Below015_D4",
        "signatureTokens": ["bool", "__fastcall", "HeightDelta__Below015_D4", "void * this"],
        "commentTokens": ["Signature hardening", "height-delta predicate", "ECX+0xd4", "Not exact owner"],
        "instructionTokens": ["[ECX + 0xd4]", "MOV", "0x1"],
        "decompileTokens": ["HeightDelta__Below015_D4", "+ 0xd4"],
    },
}

DEFAULT_SIGNATURE_DRY = BASE / "signature_dry.log"
DEFAULT_SIGNATURE_APPLY = BASE / "signature_apply.log"
DEFAULT_COMMENTS_DRY = BASE / "comments_dry.log"
DEFAULT_COMMENTS_APPLY = BASE / "comments_apply.log"
DEFAULT_METADATA = BASE / "metadata_readback.tsv"
DEFAULT_INDEX = BASE / "decompile_readback" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_readback"
DEFAULT_XREFS = BASE / "xrefs.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions.tsv"
DEFAULT_OUT = BASE / "vector-math-signature-tranche.json"

OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "source identity proven",
    "exact source identity proven",
    "class layout proven",
    "matrix layout proven",
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


def read_text(path: Path) -> str:
    if not path.is_file():
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


def parse_comment_summary(log_text: str) -> dict[str, int]:
    match = re.search(r"applied=(\d+)\s+skipped=(\d+)\s+missing=(\d+)\s+bad=(\d+)", log_text)
    if not match:
        return {"applied": -1, "skipped": -1, "missing": -1, "bad": -1}
    return {
        "applied": int(match.group(1)),
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


def instruction_rows_for(rows: list[dict[str, str]], address: str) -> list[dict[str, str]]:
    wanted = normalize_address(address)
    return [row for row in rows if normalize_address(row.get("target_addr", "")) == wanted]


def build_report(
    *,
    signature_dry_log_path: Path = DEFAULT_SIGNATURE_DRY,
    signature_apply_log_path: Path = DEFAULT_SIGNATURE_APPLY,
    comments_dry_log_path: Path = DEFAULT_COMMENTS_DRY,
    comments_apply_log_path: Path = DEFAULT_COMMENTS_APPLY,
    metadata_path: Path = DEFAULT_METADATA,
    decompile_index_path: Path = DEFAULT_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
) -> dict[str, object]:
    signature_dry_log_path = resolve(signature_dry_log_path)
    signature_apply_log_path = resolve(signature_apply_log_path)
    comments_dry_log_path = resolve(comments_dry_log_path)
    comments_apply_log_path = resolve(comments_apply_log_path)
    metadata_path = resolve(metadata_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)

    failures: list[str] = []
    for label, path in (
        ("signature dry log", signature_dry_log_path),
        ("signature apply log", signature_apply_log_path),
        ("comment dry log", comments_dry_log_path),
        ("comment apply log", comments_apply_log_path),
        ("metadata read-back", metadata_path),
        ("decompile index", decompile_index_path),
        ("xref read-back", xrefs_path),
        ("instruction read-back", instructions_path),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")
    if not decompile_dir.is_dir():
        failures.append(f"missing decompile dir: {relative(decompile_dir)}")

    signature_dry = read_text(signature_dry_log_path)
    signature_apply = read_text(signature_apply_log_path)
    comments_dry = read_text(comments_dry_log_path)
    comments_apply = read_text(comments_apply_log_path)
    metadata_rows = read_tsv(metadata_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)

    dry_summary = parse_update_summary(signature_dry)
    apply_summary = parse_update_summary(signature_apply)
    comments_dry_summary = parse_comment_summary(comments_dry)
    comments_apply_summary = parse_comment_summary(comments_apply)
    if dry_summary != {"updated": 0, "skipped": 6, "missing": 0, "bad": 0}:
        failures.append("signature dry summary is not clean")
    if apply_summary != {"updated": 6, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append("signature apply summary is not clean")
    if comments_dry_summary != {"applied": 0, "skipped": 6, "missing": 0, "bad": 0}:
        failures.append("comment dry summary is not clean")
    if comments_apply_summary != {"applied": 6, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append("comment apply summary is not clean")

    target_reports: list[dict[str, object]] = []
    signature_hardened = 0
    comment_overclaims = 0
    for address, expected in TARGETS.items():
        row = find_row(metadata_rows, "address", address)
        index_row = find_row(index_rows, "address", address)
        if row is None:
            failures.append(f"metadata missing {address}")
            continue
        signature = row.get("signature", "")
        comment = row.get("comment", "")
        if row.get("name") != expected["name"] or row.get("status") != "OK":
            failures.append(f"metadata name/status mismatch for {address}")
        missing_signature_tokens = [token for token in expected["signatureTokens"] if not token_present(signature, token)]
        if missing_signature_tokens:
            failures.append(f"signature tokens missing at {address}: {missing_signature_tokens}")
        else:
            signature_hardened += 1
        missing_comment_tokens = [token for token in expected["commentTokens"] if not token_present(comment, token)]
        if missing_comment_tokens:
            failures.append(f"comment tokens missing at {address}: {missing_comment_tokens}")
        if any(token in comment.lower() for token in OVERCLAIM_TOKENS):
            comment_overclaims += 1
            failures.append(f"runtime/source overclaim in comment at {address}")
        if index_row is None or index_row.get("name") != expected["name"] or index_row.get("status") != "OK":
            failures.append(f"decompile index mismatch for {address}")
        decompile_file = decompile_file_for(decompile_dir, address)
        decompile_text = read_text(decompile_file) if decompile_file else ""
        if not decompile_file:
            failures.append(f"missing decompile file for {address}")
        else:
            missing_decompile_tokens = [
                token for token in expected["decompileTokens"] if not token_present(decompile_text, token)
            ]
            if missing_decompile_tokens:
                failures.append(f"decompile tokens missing at {address}: {missing_decompile_tokens}")
        ins_rows = instruction_rows_for(instruction_rows, address)
        instruction_text = "\n".join(
            f"{row.get('mnemonic', '')} {row.get('operands', '')}" for row in ins_rows
        )
        missing_instruction_tokens = [
            token for token in expected["instructionTokens"] if not token_present(instruction_text, token)
        ]
        if missing_instruction_tokens:
            failures.append(f"instruction tokens missing at {address}: {missing_instruction_tokens}")
        target_reports.append(
            {
                "address": address,
                "name": row.get("name", ""),
                "signature": signature,
                "commented": bool(comment.strip()),
                "instructionRows": len(ins_rows),
                "decompileFile": relative(decompile_file),
            }
        )

    report = {
        "schema": "ghidra-vector-math-signature-tranche.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "inputs": {
            "signatureDryLog": relative(signature_dry_log_path),
            "signatureApplyLog": relative(signature_apply_log_path),
            "commentsDryLog": relative(comments_dry_log_path),
            "commentsApplyLog": relative(comments_apply_log_path),
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
        },
        "summary": {
            "targets": len(TARGETS),
            "signatureHardenedTargets": signature_hardened,
            "xrefRows": len(xref_rows),
            "instructionRows": len(instruction_rows),
            "commentOverclaims": comment_overclaims,
        },
        "targets": target_reports,
        "failures": failures,
    }
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Exit non-zero if the report fails.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output JSON report path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report()
    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("Ghidra vector/math signature tranche probe")
    print(f"Status: {report['status']}")
    print(f"Output: {relative(out_path)}")
    summary = report["summary"]
    print(
        f"Targets: {summary['targets']}; hardened: {summary['signatureHardenedTargets']}; "
        f"xref rows: {summary['xrefRows']}; instruction rows: {summary['instructionRows']}"
    )
    if report["failures"]:
        print("Failures:")
        for failure in report["failures"]:
            print(f"- {failure}")
    if args.check and report["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
