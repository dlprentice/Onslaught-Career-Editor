#!/usr/bin/env python3
"""Validate the saved Atmospherics lifecycle signature/comment tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "atmospherics-lifecycle-signature-tranche" / "current"

TARGETS = {
    "0x004046d0": {
        "name": "CAtmospheric__Constructor",
        "signatureTokens": ["void *", "__thiscall", "CAtmospheric__Constructor", "void * this", "void * ownerThing"],
        "forbiddenSignatureTokens": ["float param_1", "param_"],
        "commentTokens": ["correction", "prior float parameter", "CThing__AddTrail", "+0x20", "event 3000", "runtime behavior remain unproven"],
        "decompileTokens": ["ownerThing", "+ 0x20", "CEventManager__AddEvent_AtTime", "3000"],
        "xrefTokens": ["CThing__AddTrail"],
        "retOperand": "0x4",
    },
    "0x00404a00": {
        "name": "Atmospherics__Init",
        "signatureTokens": ["void", "__cdecl", "Atmospherics__Init"],
        "forbiddenSignatureTokens": ["param_"],
        "commentTokens": ["global Atmospherics init", "snow layer texture", "ListAtmospherics", "atm_* console variables", "runtime behavior remain unproven"],
        "decompileTokens": ["CTexture__FindTexture", "SnowLayer", "CAtmosphericsProfile__ctor", "CConsole__RegisterVariable"],
        "xrefTokens": ["CGame__PostLoadProcess"],
        "retOperand": None,
    },
    "0x00404b90": {
        "name": "Atmospherics__ResetAndUpdate",
        "signatureTokens": ["void", "__cdecl", "Atmospherics__ResetAndUpdate"],
        "forbiddenSignatureTokens": ["param_"],
        "commentTokens": ["reset/update", "prevailing wind vector", "DAT_006601a8", "+0xc virtual slot", "runtime behavior remain unproven"],
        "decompileTokens": ["DAT_00660198", "DAT_006601a8", "+ 0xc"],
        "xrefTokens": ["CGame__PostLoadProcess"],
        "retOperand": "",
    },
    "0x00404bd0": {
        "name": "Atmospherics__UpdateAll",
        "signatureTokens": ["void", "__cdecl", "Atmospherics__UpdateAll"],
        "forbiddenSignatureTokens": ["param_"],
        "commentTokens": ["update-all", "DAT_006601a8", "+0x8 virtual slot", "runtime behavior remain unproven"],
        "decompileTokens": ["DAT_006601a8", "+ 8"],
        "xrefTokens": ["CDXEngine__Render"],
        "retOperand": "",
    },
    "0x00404bf0": {
        "name": "Atmospherics__RenderAll",
        "signatureTokens": ["void", "__cdecl", "Atmospherics__RenderAll"],
        "forbiddenSignatureTokens": ["param_"],
        "commentTokens": ["render-all", "DAT_006601a8", "+0x4 virtual slot", "runtime behavior remain unproven"],
        "decompileTokens": ["DAT_006601a8", "+ 4"],
        "xrefTokens": ["CGame__Update"],
        "retOperand": "",
    },
    "0x00404c10": {
        "name": "Atmospherics__Shutdown",
        "signatureTokens": ["void", "__cdecl", "Atmospherics__Shutdown"],
        "forbiddenSignatureTokens": ["param_"],
        "commentTokens": ["global Atmospherics shutdown", "cached snow texture", "DAT_006601a8", "+0x10 virtual slot", "frees objects", "runtime behavior remain unproven"],
        "decompileTokens": ["CHud__DecrementCounter9C", "DAT_006601ac", "OID__FreeObject", "+ 0x10"],
        "xrefTokens": ["CGame__ShutdownRestartLoop", "CGame__RestartLoopRunLevel"],
        "retOperand": "",
    },
    "0x00404c90": {
        "name": "Atmospherics__NotifyAll",
        "signatureTokens": ["void", "__cdecl", "Atmospherics__NotifyAll", "int eventCode"],
        "forbiddenSignatureTokens": ["event_code", "param_"],
        "commentTokens": ["notify helper", "DAT_006601a8", "+0x14 virtual slot", "eventCode", "runtime behavior remain unproven"],
        "decompileTokens": ["eventCode", "DAT_006601a8", "+ 0x14"],
        "xrefTokens": ["CDXEngine__UpdateAtmosphericsAndLightMatrices"],
        "retOperand": "",
    },
    "0x004f44a0": {
        "name": "CThing__AddTrail",
        "signatureTokens": ["void", "__thiscall", "CThing__AddTrail", "void * this", "int samplerIndex", "int resetBlendPosition", "int blendMode"],
        "forbiddenSignatureTokens": ["undefined", "float param_1", "param_"],
        "commentTokens": ["CThing trail setup", "this+0x6c", "CAtmospheric__Constructor", "CAtmospheric__ConfigureTrail", "ret 0xc", "runtime trail behavior remain unproven"],
        "decompileTokens": ["samplerIndex", "resetBlendPosition", "blendMode", "CAtmospheric__Constructor", "CAtmospheric__ConfigureTrail"],
        "xrefTokens": ["DATA", "UNCONDITIONAL_CALL"],
        "retOperand": "0xc",
    },
}

DEFAULT_DRY = BASE / "signature_dry.log"
DEFAULT_APPLY = BASE / "signature_apply.log"
DEFAULT_METADATA = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_OUT = BASE / "atmospherics-lifecycle-signature-tranche.json"

OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "exact source identity proven",
    "concrete layout proven",
    "rebuild parity proven",
]


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def relative(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def normalize_address(value: str) -> str:
    value = (value or "").strip().lower()
    if value in {"", "<none>", "<no_function>"}:
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def compact(value: str) -> str:
    return "".join((value or "").lower().split())


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


def matching_ret_rows(instruction_rows: list[dict[str, str]], address: str, operand: str | None) -> list[dict[str, str]]:
    if operand is None:
        return []
    wanted = normalize_address(address)
    return [
        row
        for row in instruction_rows
        if normalize_address(row.get("target_addr", "")) == wanted
        and row.get("mnemonic", "").upper() == "RET"
        and row.get("operands", "") == operand
    ]


def xref_rows_for(xref_rows: list[dict[str, str]], address: str, tokens: list[str]) -> list[dict[str, str]]:
    wanted = normalize_address(address)
    hits = []
    for row in xref_rows:
        if normalize_address(row.get("target_addr", "")) != wanted:
            continue
        row_text = " ".join(row.values())
        if any(token_present(row_text, token) for token in tokens):
            hits.append(row)
    return hits


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
    if not (
        dry_summary.get("updated") == 0
        and dry_summary.get("skipped") == len(TARGETS)
        and dry_summary.get("missing") == 0
        and dry_summary.get("bad") == 0
    ):
        failures.append("dry summary is not clean")
    if not (
        apply_summary.get("updated") == len(TARGETS)
        and apply_summary.get("skipped") == 0
        and apply_summary.get("missing") == 0
        and apply_summary.get("bad") == 0
    ):
        failures.append("apply summary is not clean")

    metadata_rows = read_tsv(metadata_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)

    target_reports: list[dict[str, object]] = []
    stale_signature_hits = 0
    comment_overclaims = 0
    ret_evidence_hits = 0
    xref_evidence_hits = 0

    for address, expected in TARGETS.items():
        row = find_row(metadata_rows, "address", address)
        index_row = find_row(index_rows, "address", address)
        if row is None:
            failures.append(f"metadata missing {address}")
            continue
        if index_row is None or index_row.get("name") != expected["name"] or index_row.get("status") != "OK":
            failures.append(f"decompile index mismatch for {address}")

        signature = row.get("signature", "")
        comment = row.get("comment", "")
        if row.get("name") != expected["name"] or row.get("status") != "OK":
            failures.append(f"name/status mismatch for {address}")
        if not comment.strip():
            failures.append(f"comment remains blank at {address}")
        for forbidden in expected["forbiddenSignatureTokens"]:
            if token_present(signature, forbidden):
                stale_signature_hits += 1
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

        decompile_file = decompile_file_for(decompile_dir, address)
        decompile_text = read_text(decompile_file)
        if not decompile_file:
            failures.append(f"missing decompile file for {address}")
        missing_decompile_tokens = [token for token in expected["decompileTokens"] if not token_present(decompile_text, token)]
        if missing_decompile_tokens:
            failures.append(f"decompile tokens missing at {address}: {missing_decompile_tokens}")

        ret_rows = matching_ret_rows(instruction_rows, address, expected.get("retOperand"))
        if ret_rows:
            ret_evidence_hits += 1
        elif expected.get("retOperand") is not None:
            failures.append(f"missing ret evidence at {address}: {expected.get('retOperand')!r}")

        xref_hits = xref_rows_for(xref_rows, address, expected["xrefTokens"])
        if xref_hits:
            xref_evidence_hits += 1
        else:
            failures.append(f"missing xref/data evidence at {address}")

        target_reports.append(
            {
                "address": address,
                "name": expected["name"],
                "signature": signature,
                "commentLength": len(comment),
                "retEvidenceRows": len(ret_rows),
                "xrefEvidenceRows": len(xref_hits),
                "decompile": relative(decompile_file),
            }
        )

    return {
        "schema": "ghidra.atmospherics_lifecycle_signature_tranche.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "classification": "atmospherics-lifecycle-signature-comment-correction" if not failures else "atmospherics-lifecycle-signature-comment-invalid",
        "summary": {
            "targets": len(TARGETS),
            "dry": dry_summary,
            "apply": apply_summary,
            "staleSignatureHits": stale_signature_hits,
            "commentOverclaims": comment_overclaims,
            "retEvidenceHits": ret_evidence_hits,
            "xrefEvidenceHits": xref_evidence_hits,
            "instructionRows": len(instruction_rows),
            "xrefRows": len(xref_rows),
        },
        "targets": target_reports,
        "files": {
            "dryLog": relative(dry_log_path),
            "applyLog": relative(apply_log_path),
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
        },
        "notProven": [
            "Concrete CAtmospheric or CThing structure layout",
            "Exact Stuart-source identity because Atmospherics.cpp is absent from the checked corpus",
            "Concrete virtual slot names for the atmospheric list walkers",
            "Runtime weather/trail behavior",
            "Rebuild parity",
        ],
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="write JSON and return non-zero on failure")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    report = build_report()
    out = resolve(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Atmospherics lifecycle signature tranche: {report['status']}")
    print(f"Targets: {report['summary']['targets']}")
    print(f"Stale signature hits: {report['summary']['staleSignatureHits']}")
    print(f"Comment overclaims: {report['summary']['commentOverclaims']}")
    print(f"Xref rows: {report['summary']['xrefRows']}")
    print(f"Instruction rows: {report['summary']['instructionRows']}")
    print(f"Wrote {relative(out)}")
    if report["failures"]:
        print("Failures:")
        for failure in report["failures"]:
            print(f"- {failure}")
    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
