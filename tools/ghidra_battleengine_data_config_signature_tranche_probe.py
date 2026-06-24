#!/usr/bin/env python3
"""Validate the saved BattleEngineData/configuration Ghidra signature tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "battleengine-data-config-signature-tranche" / "current"

TARGETS = {
    "0x0040f140": {
        "name": "BattleEngineConfigurations__ShutDown",
        "signatureTokens": ["void", "__cdecl", "BattleEngineConfigurations__ShutDown"],
        "commentTokens": ["Signature hardening", "0x00660250", "0x00660200", "CWorld__ShutdownAndClear", "runtime behavior", "remain unproven"],
        "decompileTokens": ["BattleEngineConfigurations__ShutDown", "DAT_00660250", "DAT_00660200", "OID__FreeObject"],
    },
    "0x0040f180": {
        "name": "BattleEngineConfigurations__Load",
        "signatureTokens": ["void", "__cdecl", "BattleEngineConfigurations__Load", "void * memBuffer"],
        "commentTokens": ["CMEMBUFFER", "CWorld__LoadWorldHeader", "caller-cleans", "ADD ESP,0x4", "DXMemBuffer__ReadBytes", "allocated names"],
        "decompileTokens": ["memBuffer", "DAT_00660250", "DAT_00660200", "DXMemBuffer__ReadBytes", "OID__AllocObject"],
    },
    "0x0040f260": {
        "name": "BattleEngineConfigurations__Skip",
        "signatureTokens": ["void", "__cdecl", "BattleEngineConfigurations__Skip", "void * memBuffer"],
        "commentTokens": ["CMEMBUFFER", "CWorld__LoadWorldHeader", "caller-cleans", "length-prefixed strings", "frees them", "global table"],
        "decompileTokens": ["memBuffer", "DXMemBuffer__ReadBytes", "OID__AllocObject", "OID__FreeObject"],
    },
    "0x0040f520": {
        "name": "CBattleEngineData__ctor",
        "signatureTokens": ["void *", "__thiscall", "CBattleEngineData__ctor", "void * this"],
        "commentTokens": ["constructor", "ECX is this", "CSPtrSet", "+0x40/+0x50", "returns this", "runtime behavior"],
        "decompileTokens": ["this", "CSPtrSet__Init", "+0x40", "+0x50", "return this"],
    },
    "0x0040f590": {
        "name": "CBattleEngineData__Initialise",
        "signatureTokens": ["void", "__fastcall", "CBattleEngineData__Initialise", "void * battleEngineData"],
        "commentTokens": ["Initialise", "ECX is battleEngineData", "Standard", "Vulcan Cannon 1", "stealth zero", "runtime profile behavior"],
        "decompileTokens": ["battleEngineData", "s_Standard", "s_Vulcan_Cannon_1", "s_cockpit2_msh"],
    },
    "0x0040f890": {
        "name": "CBattleEngineData__Shutdown",
        "signatureTokens": ["void", "__fastcall", "CBattleEngineData__Shutdown", "void * battleEngineData"],
        "commentTokens": ["Shutdown", "ECX is battleEngineData", "mConfigurationName", "CSPtrSet__Remove", "OID__FreeObject", "runtime behavior"],
        "decompileTokens": ["battleEngineData", "+0xa8", "CSPtrSet__Remove", "OID__FreeObject"],
    },
    "0x0040f980": {
        "name": "CBattleEngineData__LoadFromMemBuffer",
        "signatureTokens": ["void", "__thiscall", "CBattleEngineData__LoadFromMemBuffer", "void * this", "void * memBuffer"],
        "commentTokens": ["Load(CMEMBUFFER&)", "RET 0x4", "versioned", "DXMemBuffer__ReadBytes", "weapon-list", "runtime profile behavior"],
        "decompileTokens": ["this", "memBuffer", "CBattleEngineData__Shutdown", "DXMemBuffer__ReadBytes", "local_108"],
    },
}

DEFAULT_DRY = BASE / "signature_dry.log"
DEFAULT_APPLY = BASE / "signature_apply.log"
DEFAULT_METADATA = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_CALLSITES = BASE / "callsite_instructions.tsv"
DEFAULT_LOAD_FULL = BASE / "instructions_load_full.tsv"
DEFAULT_OUT = BASE / "battleengine-data-config-signature-tranche.json"

OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "exact source identity proven",
    "concrete layout proven",
    "rebuild parity proven",
    "100% re",
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


def has_callsite_cleanup(rows: list[dict[str, str]], target_addr: str, call_operand: str) -> bool:
    target = normalize_address(target_addr)
    saw_call = False
    saw_cleanup = False
    for row in rows:
        if normalize_address(row.get("target_addr", "")) != target:
            continue
        if row.get("role") == "TARGET" and row.get("mnemonic", "").upper() == "CALL" and call_operand in row.get("operands", ""):
            saw_call = True
        if row.get("role") == "AFTER" and row.get("mnemonic", "").upper() == "ADD" and "ESP, 0x4" in row.get("operands", ""):
            saw_cleanup = True
    return saw_call and saw_cleanup


def build_report(
    *,
    dry_log_path: Path = DEFAULT_DRY,
    apply_log_path: Path = DEFAULT_APPLY,
    metadata_path: Path = DEFAULT_METADATA,
    decompile_index_path: Path = DEFAULT_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
    callsites_path: Path = DEFAULT_CALLSITES,
    load_full_path: Path = DEFAULT_LOAD_FULL,
) -> dict[str, object]:
    dry_log_path = resolve(dry_log_path)
    apply_log_path = resolve(apply_log_path)
    metadata_path = resolve(metadata_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)
    callsites_path = resolve(callsites_path)
    load_full_path = resolve(load_full_path)

    failures: list[str] = []
    for label, path in (
        ("dry log", dry_log_path),
        ("apply log", apply_log_path),
        ("metadata", metadata_path),
        ("decompile index", decompile_index_path),
        ("xrefs", xrefs_path),
        ("instructions", instructions_path),
        ("callsite instructions", callsites_path),
        ("full load instructions", load_full_path),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")
    if not decompile_dir.is_dir():
        failures.append(f"missing decompile dir: {relative(decompile_dir)}")

    dry_summary = parse_update_summary(read_text(dry_log_path))
    apply_summary = parse_update_summary(read_text(apply_log_path))
    if not (dry_summary.get("updated") == 0 and dry_summary.get("skipped") >= len(TARGETS) and dry_summary.get("missing") == 0 and dry_summary.get("bad") == 0):
        failures.append("dry summary is not clean")
    if not (apply_summary.get("updated", -1) + apply_summary.get("skipped", -1) >= len(TARGETS) and apply_summary.get("missing") == 0 and apply_summary.get("bad") == 0):
        failures.append("apply summary is not clean")

    metadata_rows = read_tsv(metadata_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)
    callsite_rows = read_tsv(callsites_path)
    load_full_rows = read_tsv(load_full_path)

    target_reports: list[dict[str, object]] = []
    param_signature_hits = 0
    undefined_signature_hits = 0
    comment_overclaims = 0
    decompile_token_failures = 0

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
        if signature.lower().startswith("undefined"):
            undefined_signature_hits += 1
            failures.append(f"undefined signature remains at {address}")

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

        decompile_path = decompile_file_for(decompile_dir, address)
        decompile_text = read_text(decompile_path)
        missing_decompile_tokens = [token for token in expected["decompileTokens"] if not token_present(decompile_text, token)]
        if missing_decompile_tokens:
            decompile_token_failures += 1
            failures.append(f"decompile tokens missing at {address}: {missing_decompile_tokens}")

        target_reports.append({
            "address": address,
            "name": row.get("name"),
            "signature": signature,
            "comment": comment,
            "decompile": relative(decompile_path),
        })

    xref_target_count = len({normalize_address(row.get("target_addr", "")) for row in xref_rows})
    if xref_target_count < len(TARGETS):
        failures.append(f"xref export target coverage too low: {xref_target_count}/{len(TARGETS)}")

    instruction_target_count = len({normalize_address(row.get("target_addr", "")) for row in instruction_rows})
    if instruction_target_count < len(TARGETS):
        failures.append(f"instruction export target coverage too low: {instruction_target_count}/{len(TARGETS)}")

    if not has_callsite_cleanup(callsite_rows, "0x0050d506", "0x0040f180"):
        failures.append("Load callsite cleanup evidence missing")
    if not has_callsite_cleanup(callsite_rows, "0x0050d4ff", "0x0040f260"):
        failures.append("Skip callsite cleanup evidence missing")

    load_ret_rows = [
        row for row in load_full_rows
        if normalize_address(row.get("function_entry", "")) == "0x0040f980"
        and row.get("mnemonic", "").upper() == "RET"
        and row.get("operands", "") == "0x4"
    ]
    if len(load_ret_rows) < 2:
        failures.append("LoadFromMemBuffer RET 0x4 evidence missing")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-battleengine-data-config-signature-tranche.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "target_count": len(TARGETS),
        "dry_summary": dry_summary,
        "apply_summary": apply_summary,
        "metadata": relative(metadata_path),
        "decompile_index": relative(decompile_index_path),
        "decompile_dir": relative(decompile_dir),
        "xrefs": relative(xrefs_path),
        "xref_rows": len(xref_rows),
        "instructions": relative(instructions_path),
        "instruction_rows": len(instruction_rows),
        "callsite_instructions": relative(callsites_path),
        "callsite_rows": len(callsite_rows),
        "load_ret_0x4_hits": len(load_ret_rows),
        "param_signature_hits": param_signature_hits,
        "undefined_signature_hits": undefined_signature_hits,
        "comment_overclaims": comment_overclaims,
        "decompile_token_failures": decompile_token_failures,
        "targets": target_reports,
        "failures": failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Return non-zero when validation fails.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    report = build_report()
    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"Status: {report['status']}")
    print(
        "Targets: {target_count} | param_N signatures: {param_signature_hits} | "
        "undefined signatures: {undefined_signature_hits} | load RET 0x4 hits: {load_ret_0x4_hits}".format(**report)
    )
    print(f"Evidence: {relative(out_path)}")
    if report["failures"]:
        for failure in report["failures"]:
            print(f"FAIL: {failure}", file=sys.stderr)
    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
