#!/usr/bin/env python3
"""Validate the saved GeneralVolume / ChangeWeapon Ghidra signature tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "general-volume-changeweapon-signature-tranche" / "current"

TARGETS = {
    "0x00409e80": {
        "name": "CGeneralVolume__SetParam2CC_ToOne",
        "signatureTokens": ["void", "__fastcall", "CGeneralVolume__SetParam2CC_ToOne", "void * generalVolume"],
        "forbiddenSignatureTokens": ["int param_1", "param_1"],
        "commentTokens": ["Signature hardening", "float 1.0", "generalVolume +0x2cc", "CCockpit__CycleToNextUsableWeapon", "runtime behavior", "remain unproven"],
        "decompileTokens": ["generalVolume", "+0x2cc", "0x3f800000"],
        "instructionRet": "",
    },
    "0x00409e90": {
        "name": "CGeneralVolume__SetParam2CC_ToOne_IfCurrentState1",
        "signatureTokens": ["void", "__fastcall", "CGeneralVolume__SetParam2CC_ToOne_IfCurrentState1", "void * generalVolume"],
        "forbiddenSignatureTokens": ["param_1"],
        "commentTokens": ["Signature hardening", "+0x1d4 vcall", "float 1.0", "nested state +0x34", "runtime behavior", "remain unproven"],
        "decompileTokens": ["generalVolume", "+0x1d4", "+0x34", "+0x2cc", "0x3f800000"],
        "instructionRet": "",
    },
    "0x00409ec0": {
        "name": "CGeneralVolume__SetParam2CC_ToPoint4_IfCurrentState1",
        "signatureTokens": ["void", "__fastcall", "CGeneralVolume__SetParam2CC_ToPoint4_IfCurrentState1", "void * generalVolume"],
        "forbiddenSignatureTokens": ["param_1"],
        "commentTokens": ["Signature hardening", "+0x1d4 vcall", "float 0.4", "nested state +0x34", "runtime behavior", "remain unproven"],
        "decompileTokens": ["generalVolume", "+0x1d4", "+0x34", "+0x2cc", "0x3ecccccd"],
        "instructionRet": "",
    },
    "0x00409ef0": {
        "name": "CGeneralVolume__DispatchModeSpecificReset_13CF0_or_11BF0",
        "signatureTokens": ["void", "__fastcall", "CGeneralVolume__DispatchModeSpecificReset_13CF0_or_11BF0", "void * generalVolume"],
        "forbiddenSignatureTokens": ["int param_1", "param_1"],
        "commentTokens": ["Signature hardening", "mode +0x260", "mode-2", "+0x578", "mode-3", "+0x57c", "runtime behavior", "remain unproven"],
        "decompileTokens": ["generalVolume", "+0x260", "+0x578", "+0x57c", "CGeneralVolume__UpdateCurrentEntryProgressAndRefresh", "CGeneralVolume__DispatchMode3BurstProgressAndSpawn"],
        "instructionRet": "",
    },
    "0x00409f20": {
        "name": "CGeneralVolume__Reset588AndDispatchModeSpecific_13CC0_or_11B90",
        "signatureTokens": ["void", "__fastcall", "CGeneralVolume__Reset588AndDispatchModeSpecific_13CC0_or_11B90", "void * generalVolume"],
        "forbiddenSignatureTokens": ["int param_1", "param_1"],
        "commentTokens": ["Signature hardening", "clears generalVolume +0x588", "+0x2b4", "+0x2a0", "+0x2b0", "selected-burst", "runtime behavior", "remain unproven"],
        "decompileTokens": ["generalVolume", "+0x588", "+0x2b4", "+0x2a0", "+0x2b0", "CGeneralVolume__ResetState588AndRefreshCurrentEntry", "CGeneralVolume__DispatchSelectedBurstPreset"],
        "instructionRet": "",
    },
    "0x00409f70": {
        "name": "CBattleEngine__ChangeWeapon",
        "signatureTokens": ["void", "__fastcall", "CBattleEngine__ChangeWeapon", "void * battleEngine"],
        "forbiddenSignatureTokens": ["int param_1", "param_1"],
        "commentTokens": ["Signature hardening/source bridge", "counts active weapons", "mode +0x260", "+0x588", "+0x584", "Stuart CBattleEngine::ChangeWeapon", "runtime behavior", "remain unproven"],
        "decompileTokens": ["battleEngine", "LinkedObjectList__CountFlag9C", "CGeneralVolume__SelectNextEnabledEntry", "CCockpit__CycleToNextUsableWeapon", "DAT_00672fd0", "s_Vulcan_Cannon", "s_Rail_Gun", "CBattleEngine__AttachHudSoundEventListener"],
        "instructionRet": "",
    },
}

DEFAULT_DRY = BASE / "signature_dry.log"
DEFAULT_APPLY = BASE / "signature_apply.log"
DEFAULT_METADATA = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_OUT = BASE / "general-volume-changeweapon-signature-tranche.json"

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

        ret_rows = matching_ret_rows(instruction_rows, address, expected.get("instructionRet"))
        if expected.get("instructionRet") is not None:
            if ret_rows:
                ret_evidence_hits += 1
            else:
                failures.append(f"RET evidence missing at {address}: {expected.get('instructionRet')!r}")

        target_reports.append({
            "address": address,
            "name": row.get("name"),
            "signature": signature,
            "commented": bool(comment.strip()),
            "xrefs": len([xref for xref in xref_rows if normalize_address(xref.get("target_addr", "")) == normalize_address(address)]),
            "retEvidenceRows": len(ret_rows),
            "decompile": relative(decompile_file),
        })

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-general-volume-changeweapon-signature-tranche.v1",
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
            "targets": len(TARGETS),
            "paramSignatureHits": param_signature_hits,
            "commentOverclaims": comment_overclaims,
            "retEvidenceHits": ret_evidence_hits,
            "xrefRows": len(xref_rows),
            "instructionRows": len(instruction_rows),
        },
        "targets": target_reports,
        "failures": failures,
        "whatIsProven": [
            "Six saved Ghidra GeneralVolume / ChangeWeapon-adjacent functions have current signatures/comments matching the selected read-back artifacts.",
            "CBattleEngine__ChangeWeapon has source-bridge evidence from mode-gated weapon cycling, timestamp, and HUD weapon sample string flow.",
            "The checked comments preserve runtime/source/layout/tag proof boundaries.",
        ],
        "notProven": [
            "This does not prove concrete CGeneralVolume or CBattleEngine layouts.",
            "This does not prove runtime weapon cycling, HUD audio playback, tags, exact source identity for the CGeneralVolume helpers, or rebuild parity.",
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
        print("Ghidra GeneralVolume / ChangeWeapon signature tranche probe")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Targets: {summary['targets']}")
        print(f"Param signature hits: {summary['paramSignatureHits']}")
        print(f"Comment overclaims: {summary['commentOverclaims']}")
        print(f"RET evidence hits: {summary['retEvidenceHits']}")
        print(f"Xref rows: {summary['xrefRows']}")
        print(f"Instruction rows: {summary['instructionRows']}")
        for failure in report["failures"]:
            print(f"- {failure}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
