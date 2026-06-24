#!/usr/bin/env python3
"""Validate the saved cockpit/compass Ghidra signature correction tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "cockpit-compass-queue" / "current"

TARGETS = {
    "0x00405970": {
        "name": "CDXCockpit__scalar_deleting_dtor",
        "signatureTokens": ["void *", "__thiscall", "CDXCockpit__scalar_deleting_dtor", "void * this", "byte flags"],
        "commentTokens": ["scalar-deleting destructor", "CDXCockpit", "OID__FreeObject", "runtime behavior remain unproven"],
        "decompileTokens": ["CDXCockpit__dtor_base_thunk", "OID__FreeObject", "return this"],
    },
    "0x00405990": {
        "name": "CDXCockpit__dtor_base_thunk",
        "signatureTokens": ["void", "__fastcall", "CDXCockpit__dtor_base_thunk", "void * this"],
        "commentTokens": ["jump thunk", "CCockpit__dtor_base", "runtime behavior remain unproven"],
        "decompileTokens": ["CCockpit__dtor_base"],
    },
    "0x00406040": {
        "name": "CDXCompass__GetTrackedPositionX",
        "signatureTokens": ["double", "__fastcall", "CDXCompass__GetTrackedPositionX", "void * context"],
        "commentTokens": ["tracked pointer", "+0x4b0", "+0x1c", "return precision", "remain unproven"],
        "decompileTokens": ["0x4b0", "0x1c"],
    },
    "0x0040c630": {
        "name": "CDXCompass__GetTrackedPositionY",
        "signatureTokens": ["double", "__fastcall", "CDXCompass__GetTrackedPositionY", "void * context"],
        "commentTokens": ["tracked pointer", "+0x4b0", "+0x20", "return precision", "remain unproven"],
        "decompileTokens": ["0x4b0", "0x20"],
    },
    "0x00424710": {
        "name": "CCockpit__scalar_deleting_dtor",
        "signatureTokens": ["void *", "__thiscall", "CCockpit__scalar_deleting_dtor", "void * this", "byte flags"],
        "commentTokens": ["scalar-deleting destructor", "CCockpit__dtor_base", "OID__FreeObject", "runtime behavior remain unproven"],
        "decompileTokens": ["CCockpit__dtor_base", "OID__FreeObject", "return this"],
    },
    "0x00424730": {
        "name": "CCockpit__dtor_base",
        "signatureTokens": ["void", "__fastcall", "CCockpit__dtor_base", "void * this"],
        "commentTokens": ["vtable", "0x005d9524", "0x005d94ac", "CMonitor__Shutdown", "runtime behavior", "remain unproven"],
        "decompileTokens": ["PTR_LAB_005d9524", "PTR_LAB_005d94ac", "CMonitor__Shutdown"],
    },
}

DEFAULT_DRY = BASE / "correction_dry.log"
DEFAULT_APPLY = BASE / "correction_apply.log"
DEFAULT_METADATA = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_VTABLE_TYPES = BASE / "vtable_types.tsv"
DEFAULT_OUT = BASE / "cockpit-compass-signature-correction.json"

STALE_NAME_TOKENS = [
    "VFunc_01_00405970",
    "VFunc_01_00424710",
    "ctor_like_00424730",
]

OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "exact source identity proven",
    "concrete layout proven",
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


def build_report(
    *,
    dry_log_path: Path = DEFAULT_DRY,
    apply_log_path: Path = DEFAULT_APPLY,
    metadata_path: Path = DEFAULT_METADATA,
    decompile_index_path: Path = DEFAULT_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
    vtable_types_path: Path = DEFAULT_VTABLE_TYPES,
) -> dict[str, object]:
    dry_log_path = resolve(dry_log_path)
    apply_log_path = resolve(apply_log_path)
    metadata_path = resolve(metadata_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)
    vtable_types_path = resolve(vtable_types_path)

    failures: list[str] = []
    for label, path in (
        ("dry log", dry_log_path),
        ("apply log", apply_log_path),
        ("metadata", metadata_path),
        ("decompile index", decompile_index_path),
        ("xrefs", xrefs_path),
        ("instructions", instructions_path),
        ("vtable types", vtable_types_path),
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
    vtable_rows = read_tsv(vtable_types_path)

    target_reports: list[dict[str, object]] = []
    stale_name_hits = 0
    param_signature_hits = 0
    comment_overclaims = 0
    for address, expected in TARGETS.items():
        row = find_row(metadata_rows, "address", address)
        index_row = find_row(index_rows, "address", address)
        if row is None:
            failures.append(f"metadata missing {address}")
            continue
        signature = row.get("signature", "")
        comment = row.get("comment", "")
        combined_name_sig = f"{row.get('name', '')} {signature}"
        if row.get("name") != expected["name"] or row.get("status") != "OK":
            failures.append(f"name/status mismatch for {address}")
        for stale in STALE_NAME_TOKENS:
            if stale in combined_name_sig:
                stale_name_hits += 1
                failures.append(f"stale name token remains at {address}: {stale}")
        if "param_" in signature:
            param_signature_hits += 1
            failures.append(f"param_N signature remains at {address}")
        missing_signature_tokens = [token for token in expected["signatureTokens"] if not token_present(signature, token)]
        if missing_signature_tokens:
            failures.append(f"signature tokens missing at {address}: {missing_signature_tokens}")
        missing_comment_tokens = [token for token in expected["commentTokens"] if token not in comment]
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
            missing_decompile_tokens = [token for token in expected["decompileTokens"] if token not in decompile_text]
            if missing_decompile_tokens:
                failures.append(f"decompile tokens missing at {address}: {missing_decompile_tokens}")
        target_reports.append(
            {
                "address": address,
                "name": row.get("name"),
                "signature": signature,
                "commentPresent": bool(comment),
                "xrefRows": sum(1 for xref in xref_rows if normalize_address(xref.get("target_addr", "")) == normalize_address(address)),
            }
        )

    vtable_names = {row.get("demangled_type_name", "") for row in vtable_rows}
    if "CDXCockpit" not in vtable_names:
        failures.append("CDXCockpit vtable type evidence missing")
    if "CCockpit" not in vtable_names:
        failures.append("CCockpit vtable type evidence missing")
    scalar_ret4_rows = [
        row for row in instruction_rows
        if row.get("target_addr") in {"0x00405970", "0x00424710"} and row.get("mnemonic") == "RET" and row.get("operands") == "0x4"
    ]
    if len(scalar_ret4_rows) < 2:
        failures.append("scalar deleting destructor ret 4 instruction evidence missing")

    report = {
        "status": "PASS" if not failures else "FAIL",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "classification": "cockpit-compass-signature-correction-saved" if not failures else "cockpit-compass-signature-correction-invalid",
        "summary": {
            "targets": len(TARGETS),
            "staleNameHits": stale_name_hits,
            "paramSignatureHits": param_signature_hits,
            "commentOverclaims": comment_overclaims,
            "xrefRows": len(xref_rows),
            "instructionRows": len(instruction_rows),
            "vtableTypeRows": len(vtable_rows),
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
            "vtableTypes": relative(vtable_types_path),
        },
        "notProven": [
            "exact Stuart source method identities",
            "concrete CDXCockpit, CCockpit, or CDXCompass layouts",
            "local variable names, tags, and structure types",
            "runtime cockpit or compass behavior",
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

    print("Ghidra cockpit/compass signature correction probe")
    print(f"Status: {report['status']}")
    print(f"Output: {relative(out_path)}")
    print(
        "Targets: {targets}; stale names: {staleNameHits}; param signatures: {paramSignatureHits}; xref rows: {xrefRows}".format(
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
