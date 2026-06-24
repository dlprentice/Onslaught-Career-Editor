#!/usr/bin/env python3
"""Validate the saved CActor render name/signature correction tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "actor-render-signature-correction" / "current"

TARGETS = {
    "0x00401b50": {
        "name": "CActor__GetFractionTime",
        "signatureTokens": [
            "float",
            "__thiscall",
            "CActor__GetFractionTime",
            "void * this",
        ],
        "commentTokens": [
            "CActor::GetFractionTime",
            "GetMoveMultiplier",
            "this+0xd8",
            "prior CMCMine scale-helper label",
            "not a concrete CActor layout",
        ],
        "decompileTokens": [
            "CActor__GetFractionTime",
            "this",
            "0xd8",
            "005d8568",
            "005d856c",
        ],
    },
    "0x00401be0": {
        "name": "CActor__GetRenderPos",
        "signatureTokens": [
            "void",
            "__thiscall",
            "CActor__GetRenderPos",
            "void * this",
            "void * outRenderPos",
        ],
        "commentTokens": [
            "CActor::GetRenderPos",
            "hidden-return FVector",
            "frame render fraction",
            "subclass vtable xrefs",
            "not a concrete FVector layout",
        ],
        "decompileTokens": [
            "CActor__GetRenderPos",
            "outRenderPos",
            "0x14",
            "0x84",
            "0x88",
            "0x8c",
        ],
    },
    "0x00401c50": {
        "name": "CActor__GetRenderOrientation",
        "signatureTokens": [
            "void",
            "__thiscall",
            "CActor__GetRenderOrientation",
            "void * this",
            "void * outRenderOrientation",
        ],
        "commentTokens": [
            "CActor::GetRenderOrientation",
            "hidden-return FMatrix",
            "GetFractionTime-like clamp path",
            "row-copy helpers",
            "not a concrete FMatrix layout",
        ],
        "decompileTokens": [
            "CActor__GetRenderOrientation",
            "outRenderOrientation",
            "Vec3__SetXYZ",
            "Mat34__SetRows",
            "0x94",
            "0xa4",
            "0xb4",
        ],
    },
}

DEFAULT_RENAME_DRY = BASE / "rename_dry.log"
DEFAULT_RENAME_APPLY = BASE / "rename_apply.log"
DEFAULT_SIGNATURE_DRY = BASE / "signature_dry.log"
DEFAULT_SIGNATURE_APPLY = BASE / "signature_apply.log"
DEFAULT_COMMENTS_DRY = BASE / "comments_dry.log"
DEFAULT_COMMENTS_APPLY = BASE / "comments_apply.log"
DEFAULT_METADATA = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_OUT = BASE / "actor-render-signature-correction.json"

STALE_TOKENS = [
    "CMCMine__ComputeClampedScaleFactor",
    "VFuncSlot_00_00401be0",
    "VFuncSlot_01_00401c50",
    "param_1",
    "param_2",
    "param_3",
    "unaff_",
]

OVERCLAIM_TOKENS = [
    "runtime render behavior proven",
    "proves runtime render behavior",
    "concrete cactor layout proven",
    "concrete fvector layout proven",
    "concrete fmatrix layout proven",
    "exact retail class layout proven",
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


def parse_apply_summary(log_text: str) -> dict[str, int]:
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


def rows_for(rows: list[dict[str, str]], address: str) -> list[dict[str, str]]:
    wanted = normalize_address(address)
    return [row for row in rows if normalize_address(row.get("target_addr", "")) == wanted]


def decompile_file_for(decompile_dir: Path, address: str) -> Path | None:
    if not decompile_dir.is_dir():
        return None
    matches = sorted(decompile_dir.glob(f"{normalize_address(address)[2:]}_*.c"))
    return matches[0] if matches else None


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
    metadata_rows = read_tsv(metadata_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)

    failures: list[str] = []
    stale_hits: list[dict[str, str]] = []
    overclaim_hits: list[dict[str, str]] = []
    target_reports: dict[str, dict[str, object]] = {}

    rename_dry = parse_apply_summary(read_text(rename_dry_log_path))
    rename_apply = parse_apply_summary(read_text(rename_apply_log_path))
    signature_dry = parse_update_summary(read_text(signature_dry_log_path))
    signature_apply = parse_update_summary(read_text(signature_apply_log_path))
    comments_dry = parse_apply_summary(read_text(comments_dry_log_path))
    comments_apply = parse_apply_summary(read_text(comments_apply_log_path))

    if rename_dry != {"applied": 0, "skipped": len(TARGETS), "missing": 0, "bad": 0}:
        failures.append(f"unexpected rename dry summary {rename_dry}")
    if rename_apply != {"applied": len(TARGETS), "skipped": 0, "missing": 0, "bad": 0}:
        failures.append(f"unexpected rename apply summary {rename_apply}")
    if signature_dry != {"updated": 0, "skipped": len(TARGETS), "missing": 0, "bad": 0}:
        failures.append(f"unexpected signature dry summary {signature_dry}")
    if signature_apply != {"updated": len(TARGETS), "skipped": 0, "missing": 0, "bad": 0}:
        failures.append(f"unexpected signature apply summary {signature_apply}")
    if comments_dry != {"applied": 0, "skipped": len(TARGETS), "missing": 0, "bad": 0}:
        failures.append(f"unexpected comments dry summary {comments_dry}")
    if comments_apply != {"applied": len(TARGETS), "skipped": 0, "missing": 0, "bad": 0}:
        failures.append(f"unexpected comments apply summary {comments_apply}")

    for address, expected in TARGETS.items():
        normalized = normalize_address(address)
        metadata = find_row(metadata_rows, "address", normalized)
        index = find_row(index_rows, "address", normalized)
        decompile_file = decompile_file_for(decompile_dir, normalized)
        decompile_text = read_text(decompile_file) if decompile_file else ""
        xrefs = rows_for(xref_rows, normalized)
        instructions = rows_for(instruction_rows, normalized)

        if metadata is None:
            failures.append(f"{normalized} missing metadata row")
            metadata = {}
        if index is None:
            failures.append(f"{normalized} missing decompile index row")
            index = {}
        if decompile_file is None:
            failures.append(f"{normalized} missing decompile output")
        if not xrefs:
            failures.append(f"{normalized} missing xref rows")
        if not instructions:
            failures.append(f"{normalized} missing instruction rows")

        actual_name = metadata.get("name", "")
        actual_signature = metadata.get("signature", "")
        actual_comment = metadata.get("comment", "")
        checked_text = "\n".join([actual_name, actual_signature, actual_comment, decompile_text])

        if actual_name != expected["name"]:
            failures.append(f"{normalized} name mismatch: {actual_name!r} != {expected['name']!r}")
        missing_signature_tokens = [
            token for token in expected["signatureTokens"] if not token_present(actual_signature, token)
        ]
        if missing_signature_tokens:
            failures.append(f"{normalized} signature tokens missing: {missing_signature_tokens}")
        missing_comment_tokens = [
            token for token in expected["commentTokens"] if not token_present(actual_comment, token)
        ]
        if missing_comment_tokens:
            failures.append(f"{normalized} comment tokens missing: {missing_comment_tokens}")
        missing_decompile_tokens = [
            token for token in expected["decompileTokens"] if not token_present(decompile_text, token)
        ]
        if missing_decompile_tokens:
            failures.append(f"{normalized} decompile tokens missing: {missing_decompile_tokens}")

        for token in STALE_TOKENS:
            if token_present(checked_text, token):
                stale_hits.append({"address": normalized, "token": token})
                failures.append(f"{normalized} stale token present: {token}")
        for token in OVERCLAIM_TOKENS:
            if token_present(checked_text, token):
                overclaim_hits.append({"address": normalized, "token": token})
                failures.append(f"{normalized} overclaim token present: {token}")

        target_reports[normalized] = {
            "expectedName": expected["name"],
            "actualName": actual_name,
            "signature": actual_signature,
            "commented": bool(actual_comment.strip()),
            "decompileFile": relative(decompile_file),
            "xrefRows": len(xrefs),
            "instructionRows": len(instructions),
        }

    report = {
        "status": "PASS" if not failures else "FAIL",
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "targets": len(TARGETS),
            "renamedTargets": rename_apply.get("applied", -1),
            "signatureHardenedTargets": signature_apply.get("updated", -1),
            "commentedTargets": comments_apply.get("applied", -1),
            "metadataRows": len(metadata_rows),
            "decompileIndexRows": len(index_rows),
            "xrefRows": len(xref_rows),
            "instructionRows": len(instruction_rows),
            "staleTokenHits": len(stale_hits),
            "overclaimHits": len(overclaim_hits),
        },
        "targets": target_reports,
        "logs": {
            "renameDry": relative(rename_dry_log_path),
            "renameApply": relative(rename_apply_log_path),
            "signatureDry": relative(signature_dry_log_path),
            "signatureApply": relative(signature_apply_log_path),
            "commentsDry": relative(comments_dry_log_path),
            "commentsApply": relative(comments_apply_log_path),
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
        },
        "staleTokenHits": stale_hits,
        "overclaimHits": overclaim_hits,
        "failures": failures,
    }
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="exit non-zero if validation fails")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="JSON report path")
    args = parser.parse_args(argv)

    report = build_report()
    out = resolve(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"Status: {report['status']}")
    print(f"Targets: {report['summary']['targets']}")
    print(f"Renamed targets: {report['summary']['renamedTargets']}")
    print(f"Signature-hardened targets: {report['summary']['signatureHardenedTargets']}")
    print(f"Commented targets: {report['summary']['commentedTargets']}")
    print(f"Stale token hits: {report['summary']['staleTokenHits']}")
    print(f"Overclaim hits: {report['summary']['overclaimHits']}")
    print(f"Wrote: {relative(out)}")
    if report["failures"]:
        print("Failures:")
        for failure in report["failures"]:
            print(f"- {failure}")
    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
