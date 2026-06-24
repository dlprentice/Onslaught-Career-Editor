#!/usr/bin/env python3
"""Validate the saved actor/complex-thing Ghidra correction tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "signature-debt-tranche7" / "current"

TARGETS = {
    "0x004011e0": {
        "name": "CActor__Init",
        "signatureTokens": ["void", "__thiscall", "CActor__Init", "void * this", "void * init"],
        "commentTokens": ["Actor source-parity", "last-ground/water/object", "CComplexThing__Init", "Not runtime proof"],
        "decompileTokens": ["0xc2c80000", "CComplexThing__Init", "CEventManager__AddEvent_AtTime"],
        "instructionTokens": ["RET", "0x4"],
    },
    "0x004013d0": {
        "name": "CActor__dtor_base",
        "signatureTokens": ["void", "__fastcall", "CActor__dtor_base", "void * this"],
        "commentTokens": ["destructor-base correction", "CComplexThing__dtor_base", "Not constructor evidence"],
        "decompileTokens": ["CComplexThing__dtor_base"],
        "instructionTokens": ["0x5d844c", "0x004f3f00"],
    },
    "0x004015c0": {
        "name": "CActor__scalar_deleting_dtor",
        "signatureTokens": ["void *", "__thiscall", "CActor__scalar_deleting_dtor", "void * this", "byte flags"],
        "commentTokens": ["scalar-deleting destructor", "CActor__dtor_base", "flags&1"],
        "decompileTokens": ["CActor__dtor_base", "OID__FreeObject", "return this"],
        "instructionTokens": ["RET", "0x4"],
    },
    "0x004015e0": {
        "name": "CActor__Move",
        "signatureTokens": ["void", "__fastcall", "CActor__Move", "void * this"],
        "commentTokens": ["Actor source-parity", "velocity integration", "map-entry update", "Not runtime movement claim"],
        "decompileTokens": ["CMapWhoEntry__UpdatePosition", "CStaticShadows__SampleShadowHeightBilinear", "DAT_00672fd0"],
        "instructionTokens": ["RET"],
    },
    "0x004019b0": {
        "name": "CActor__TeleportOrientation",
        "signatureTokens": ["void", "__thiscall", "CActor__TeleportOrientation", "void * this", "void * orientation"],
        "commentTokens": ["Actor source-parity", "old-orientation", "CComplexThing__TeleportOrientation", "Not FMatrix layout claim"],
        "decompileTokens": ["CComplexThing__TeleportOrientation"],
        "instructionTokens": ["MOVSD.REP", "RET", "0x4"],
    },
    "0x004019e0": {
        "name": "CActor__HandleEvent",
        "signatureTokens": ["void", "__thiscall", "CActor__HandleEvent", "void * this", "void * event"],
        "commentTokens": ["Actor source-parity", "MOVE 3000", "0xbb9", "Not runtime scheduler claim"],
        "decompileTokens": ["3000", "0xbb9", "CComplexThing__HandleEvent", "CEventManager__AddEvent_AtTime"],
        "instructionTokens": ["RET", "0x4"],
    },
    "0x004f3ee0": {
        "name": "CComplexThing__scalar_deleting_dtor",
        "signatureTokens": ["void *", "__thiscall", "CComplexThing__scalar_deleting_dtor", "void * this", "byte flags"],
        "commentTokens": ["scalar-deleting destructor", "CComplexThing__dtor_base", "flags&1"],
        "decompileTokens": ["CComplexThing__dtor_base", "OID__FreeObject", "return this"],
        "instructionTokens": ["RET", "0x4"],
    },
    "0x004f3f00": {
        "name": "CComplexThing__dtor_base",
        "signatureTokens": ["void", "__fastcall", "CComplexThing__dtor_base", "void * this"],
        "commentTokens": ["destructor-base correction", "script/animation/motion", "Not constructor evidence"],
        "decompileTokens": ["CMapWhoEntry__RemoveFromMap", "CMonitor__Shutdown"],
        "instructionTokens": ["RET"],
    },
    "0x004f3fd0": {
        "name": "CComplexThing__Init",
        "signatureTokens": ["void", "__thiscall", "CComplexThing__Init", "void * this", "void * init"],
        "commentTokens": ["ComplexThing source-parity", "orientation from init", "CThing__Init"],
        "decompileTokens": ["CThing__SetSound", "CThing__VFunc_09_004f34a0"],
        "instructionTokens": ["RET", "0x4"],
    },
    "0x004f4300": {
        "name": "CComplexThing__HandleEvent",
        "signatureTokens": ["void", "__thiscall", "CComplexThing__HandleEvent", "void * this", "void * event"],
        "commentTokens": ["ComplexThing source-parity", "shutdown/init-script/ready-script", "Not runtime script proof"],
        "decompileTokens": ["IScript__CallEvent0AndRegisterNestedListeners", "CEventManager__AddEvent_AtTime"],
        "instructionTokens": ["RET", "0x4"],
    },
    "0x004f4460": {
        "name": "CComplexThing__TeleportOrientation",
        "signatureTokens": ["void", "__thiscall", "CComplexThing__TeleportOrientation", "void * this", "void * orientation"],
        "commentTokens": ["ComplexThing source-parity", "12 dwords", "Not FMatrix layout proof"],
        "decompileTokens": ["0xc", "+ 0x3c"],
        "instructionTokens": ["MOVSD.REP", "RET", "0x4"],
    },
}

DEFAULT_RENAME_DRY = BASE / "rename_dry.log"
DEFAULT_RENAME_APPLY = BASE / "rename_apply.log"
DEFAULT_SIGNATURE_DRY = BASE / "signature_dry.log"
DEFAULT_SIGNATURE_APPLY = BASE / "signature_apply.log"
DEFAULT_COMMENTS_DRY = BASE / "comments_dry.log"
DEFAULT_COMMENTS_APPLY = BASE / "comments_apply.log"
DEFAULT_METADATA = BASE / "metadata_readback.tsv"
DEFAULT_INDEX = BASE / "decompile_readback" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_readback"
DEFAULT_XREFS = BASE / "xrefs_readback.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_readback.tsv"
DEFAULT_OUT = BASE / "actor-complex-signature-tranche.json"

OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "exact source identity proven",
    "class layout proven",
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


def parse_rename_summary(log_text: str) -> dict[str, int]:
    match = re.search(r"applied=(\d+)\s+skipped=(\d+)\s+missing=(\d+)\s+bad=(\d+)", log_text)
    if not match:
        return {"applied": -1, "skipped": -1, "missing": -1, "bad": -1}
    return {
        "applied": int(match.group(1)),
        "skipped": int(match.group(2)),
        "missing": int(match.group(3)),
        "bad": int(match.group(4)),
    }


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


def instruction_text_for(rows: list[dict[str, str]], address: str) -> str:
    wanted = normalize_address(address)
    chunks: list[str] = []
    for row in rows:
        if normalize_address(row.get("target_addr", "")) == wanted:
            chunks.append(
                " ".join(
                    [
                        row.get("instruction_addr", ""),
                        row.get("function_name", ""),
                        row.get("mnemonic", ""),
                        row.get("operands", ""),
                    ]
                )
            )
    return "\n".join(chunks)


def build_report(
    *,
    rename_dry_log_path: Path = DEFAULT_RENAME_DRY,
    rename_apply_log_path: Path = DEFAULT_RENAME_APPLY,
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
    rename_dry_log_path = resolve(rename_dry_log_path)
    rename_apply_log_path = resolve(rename_apply_log_path)
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
        ("rename dry log", rename_dry_log_path),
        ("rename apply log", rename_apply_log_path),
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

    target_count = len(TARGETS)
    rename_dry_summary = parse_rename_summary(read_text(rename_dry_log_path))
    rename_apply_summary = parse_rename_summary(read_text(rename_apply_log_path))
    signature_dry_summary = parse_update_summary(read_text(signature_dry_log_path))
    signature_apply_summary = parse_update_summary(read_text(signature_apply_log_path))
    comments_dry_summary = parse_rename_summary(read_text(comments_dry_log_path))
    comments_apply_summary = parse_rename_summary(read_text(comments_apply_log_path))

    if rename_dry_summary != {"applied": 0, "skipped": target_count, "missing": 0, "bad": 0}:
        failures.append("rename dry summary is not clean")
    if rename_apply_summary != {"applied": target_count, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append("rename apply summary is not clean")
    if signature_dry_summary != {"updated": 0, "skipped": target_count, "missing": 0, "bad": 0}:
        failures.append("signature dry summary is not clean")
    if signature_apply_summary != {"updated": target_count, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append("signature apply summary is not clean")
    if comments_dry_summary != {"applied": 0, "skipped": target_count, "missing": 0, "bad": 0}:
        failures.append("comment dry summary is not clean")
    if comments_apply_summary != {"applied": target_count, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append("comment apply summary is not clean")

    metadata_rows = read_tsv(metadata_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)

    target_reports: list[dict[str, object]] = []
    renamed = 0
    signature_hardened = 0
    comment_overclaims = 0
    for address, expected in TARGETS.items():
        row = find_row(metadata_rows, "address", address)
        index_row = find_row(index_rows, "address", address)
        if row is None:
            failures.append(f"metadata missing {address}")
            continue

        name = row.get("name", "")
        signature = row.get("signature", "")
        comment = row.get("comment", "")
        if name != expected["name"] or row.get("status") != "OK":
            failures.append(f"metadata name/status mismatch for {address}")
        else:
            renamed += 1

        missing_signature_tokens = [token for token in expected["signatureTokens"] if not token_present(signature, token)]
        if missing_signature_tokens:
            failures.append(f"signature tokens missing at {address}: {missing_signature_tokens}")
        else:
            signature_hardened += 1

        missing_comment_tokens = [token for token in expected["commentTokens"] if not token_present(comment, token)]
        if missing_comment_tokens:
            failures.append(f"comment tokens missing at {address}: {missing_comment_tokens}")
        lowered_comment = comment.lower()
        if any(token in lowered_comment for token in OVERCLAIM_TOKENS):
            comment_overclaims += 1
            failures.append(f"runtime/source overclaim in comment at {address}")

        if index_row is None or index_row.get("name") != expected["name"] or index_row.get("status") != "OK":
            failures.append(f"decompile index mismatch for {address}")

        decompile_file = decompile_file_for(decompile_dir, address)
        decompile_text = read_text(decompile_file) if decompile_file else ""
        missing_decompile_tokens = [token for token in expected["decompileTokens"] if not token_present(decompile_text, token)]
        if not decompile_file:
            failures.append(f"missing decompile file for {address}")
        elif missing_decompile_tokens:
            failures.append(f"decompile tokens missing at {address}: {missing_decompile_tokens}")

        instruction_text = instruction_text_for(instruction_rows, address)
        missing_instruction_tokens = [token for token in expected["instructionTokens"] if not token_present(instruction_text, token)]
        if missing_instruction_tokens:
            failures.append(f"instruction tokens missing at {address}: {missing_instruction_tokens}")

        target_reports.append(
            {
                "address": address,
                "name": name,
                "signature": signature,
                "comment": comment,
                "decompileFile": relative(decompile_file) if decompile_file else None,
                "missingSignatureTokens": missing_signature_tokens,
                "missingCommentTokens": missing_comment_tokens,
                "missingDecompileTokens": missing_decompile_tokens,
                "missingInstructionTokens": missing_instruction_tokens,
            }
        )

    report = {
        "status": "PASS" if not failures else "FAIL",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "targets": target_count,
            "renamedTargets": renamed,
            "signatureHardenedTargets": signature_hardened,
            "commentOverclaims": comment_overclaims,
            "xrefRows": len(xref_rows),
            "instructionRows": len(instruction_rows),
            "renameDry": rename_dry_summary,
            "renameApply": rename_apply_summary,
            "signatureDry": signature_dry_summary,
            "signatureApply": signature_apply_summary,
            "commentsDry": comments_dry_summary,
            "commentsApply": comments_apply_summary,
        },
        "inputs": {
            "renameDryLog": relative(rename_dry_log_path),
            "renameApplyLog": relative(rename_apply_log_path),
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
        "targets": target_reports,
        "failures": failures,
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="exit non-zero when validation fails")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="JSON report path")
    args = parser.parse_args()

    report = build_report()
    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"Actor/ComplexThing signature tranche: {report['status']}")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    if report["failures"]:
        for failure in report["failures"]:
            print(f"- {failure}")
    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
