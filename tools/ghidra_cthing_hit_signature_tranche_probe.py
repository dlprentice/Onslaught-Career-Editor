#!/usr/bin/env python3
"""Validate the saved CThing hit signature tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "cthing-hit-signature-tranche" / "current"

TARGETS = {
    "0x00403ba0": {
        "name": "CThing__Hit_TriggerDieOnUnitOrTypeMask02100000",
        "signatureTokens": [
            "void",
            "__thiscall",
            "CThing__Hit_TriggerDieOnUnitOrTypeMask02100000",
            "void * this",
            "void * otherThing",
            "void * collisionReport",
        ],
        "commentTokens": ["0x10", "0x02100000", "CThing::Hit(CThing*, CCollisionReport*)", "inferred"],
        "decompileTokens": [
            "CThing__Hit_TriggerDieOnUnitOrTypeMask02100000",
            "otherThing",
            "collisionReport",
            "CThing__CreateHitRefEvaluateImpulseAndDispatchHit",
            "0x2100000",
        ],
    },
    "0x00403bf0": {
        "name": "CThing__Hit_TriggerDieOnTypeMask00100000",
        "signatureTokens": [
            "void",
            "__thiscall",
            "CThing__Hit_TriggerDieOnTypeMask00100000",
            "void * this",
            "void * otherThing",
            "void * collisionReport",
        ],
        "commentTokens": ["0x00100000", "CThing::Hit(CThing*, CCollisionReport*)", "unresolved"],
        "decompileTokens": [
            "CThing__Hit_TriggerDieOnTypeMask00100000",
            "otherThing",
            "collisionReport",
            "CThing__CreateHitRefEvaluateImpulseAndDispatchHit",
            "0x100000",
        ],
    },
    "0x004fcc30": {
        "name": "CThing__CreateHitRefEvaluateImpulseAndDispatchHit",
        "signatureTokens": [
            "void",
            "__thiscall",
            "CThing__CreateHitRefEvaluateImpulseAndDispatchHit",
            "void * this",
            "void * otherThing",
            "void * collisionReport",
        ],
        "commentTokens": ["this+0x248", "collisionReport", "0x00100000", "not a full CCollisionReport layout proof"],
        "decompileTokens": [
            "CThing__CreateHitRefEvaluateImpulseAndDispatchHit",
            "otherThing",
            "collisionReport",
            "CThing__CreateThingRefWithSquad",
            "CComplexThing__Hit",
        ],
    },
    "0x004e6640": {
        "name": "CThing__CreateThingRefWithSquad",
        "signatureTokens": [
            "void",
            "__thiscall",
            "CThing__CreateThingRefWithSquad",
            "void * this",
            "void * ownerThing",
            "void * otherThing",
        ],
        "commentTokens": ["ownerThing", "otherThing", "two stack arguments", "does not prove the full referred-object layout"],
        "decompileTokens": ["CThing__CreateThingRefWithSquad", "ownerThing", "otherThing"],
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
DEFAULT_OUT = BASE / "cthing-hit-signature-tranche.json"

STALE_TOKENS = [
    "DamageMask",
    "param_1",
    "param_2",
    "param_3",
    "unaff_EDI",
    "CThing__Hit_TriggerDieOnDamageMaskA",
    "CThing__Hit_TriggerDieOnDamageMaskB",
]

OVERCLAIM_TOKENS = [
    "full referred-object layout proof",
    "this is a full ccollisionreport layout proof",
    "proves full ccollisionreport layout",
    "runtime behavior proven",
    "source identity proven",
    "exact retail type-bit label proven",
    "exact retail class owner proven",
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
    metadata_rows = read_tsv(metadata_path)
    decompile_index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)

    rename_dry = parse_apply_summary(read_text(rename_dry_log_path))
    rename_apply = parse_apply_summary(read_text(rename_apply_log_path))
    signature_dry = parse_update_summary(read_text(signature_dry_log_path))
    signature_apply = parse_update_summary(read_text(signature_apply_log_path))
    comments_dry = parse_apply_summary(read_text(comments_dry_log_path))
    comments_apply = parse_apply_summary(read_text(comments_apply_log_path))

    expected_count = len(TARGETS)
    if rename_dry != {"applied": 0, "skipped": 2, "missing": 0, "bad": 0}:
        failures.append(f"rename dry summary mismatch: {rename_dry}")
    if rename_apply != {"applied": 2, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append(f"rename apply summary mismatch: {rename_apply}")
    if signature_dry != {"updated": 0, "skipped": expected_count, "missing": 0, "bad": 0}:
        failures.append(f"signature dry summary mismatch: {signature_dry}")
    if signature_apply != {"updated": expected_count, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append(f"signature apply summary mismatch: {signature_apply}")
    if comments_dry != {"applied": 0, "skipped": expected_count, "missing": 0, "bad": 0}:
        failures.append(f"comments dry summary mismatch: {comments_dry}")
    if comments_apply != {"applied": expected_count, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append(f"comments apply summary mismatch: {comments_apply}")

    stale_hits: list[str] = []
    overclaim_hits: list[str] = []
    for address, spec in TARGETS.items():
        meta = find_row(metadata_rows, "address", address)
        index = find_row(decompile_index_rows, "address", address)
        decompile_path = decompile_file_for(decompile_dir, address)
        decompile_text = read_text(decompile_path) if decompile_path is not None else ""

        if meta is None:
            failures.append(f"{address} missing metadata row")
            continue
        if index is None:
            failures.append(f"{address} missing decompile index row")
        if decompile_path is None:
            failures.append(f"{address} missing decompile file")

        if meta.get("name") != spec["name"]:
            failures.append(f"{address} name mismatch: {meta.get('name')} != {spec['name']}")
        signature = meta.get("signature", "")
        missing_signature = [token for token in spec["signatureTokens"] if not token_present(signature, token)]
        if missing_signature:
            failures.append(f"{address} signature tokens missing: {missing_signature}")
        comment = meta.get("comment", "")
        missing_comment = [token for token in spec["commentTokens"] if not token_present(comment, token)]
        if missing_comment:
            failures.append(f"{address} comment tokens missing: {missing_comment}")
        missing_decompile = [token for token in spec["decompileTokens"] if not token_present(decompile_text, token)]
        if missing_decompile:
            failures.append(f"{address} decompile tokens missing: {missing_decompile}")
        if not rows_for(xref_rows, address):
            failures.append(f"{address} has no xref rows")
        if not rows_for(instruction_rows, address):
            failures.append(f"{address} has no instruction rows")

        combined = "\n".join([meta.get("name", ""), signature, comment, decompile_text])
        for token in STALE_TOKENS:
            if token_present(combined, token):
                stale_hits.append(f"{address}:{token}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                overclaim_hits.append(f"{address}:{token}")

    for hit in stale_hits:
        failures.append(f"stale token observed: {hit}")
    for hit in overclaim_hits:
        failures.append(f"overclaim token observed: {hit}")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-cthing-hit-signature-tranche.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "inputs": {
            "renameDryLog": relative(rename_dry_log_path),
            "renameApplyLog": relative(rename_apply_log_path),
            "signatureDryLog": relative(signature_dry_log_path),
            "signatureApplyLog": relative(signature_apply_log_path),
            "commentsDryLog": relative(comments_dry_log_path),
            "commentsApplyLog": relative(comments_apply_log_path),
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
        },
        "summary": {
            "targets": expected_count,
            "renamedTargets": rename_apply["applied"],
            "signatureHardenedTargets": signature_apply["updated"],
            "commentedTargets": comments_apply["applied"],
            "metadataRows": len(metadata_rows),
            "decompileRows": len(decompile_index_rows),
            "xrefRows": len(xref_rows),
            "instructionRows": len(instruction_rows),
            "staleTokenHits": len(stale_hits),
            "overclaimHits": len(overclaim_hits),
        },
        "whatIsProven": [
            "The saved Ghidra database has two CThing hit helper names corrected from DamageMask wording to type-mask wording.",
            "The saved signatures for the two hit helpers, the shared hit dispatcher, and the thing-ref helper use the observed two-stack-argument call shapes.",
            "Read-back decompile for the tranche no longer contains param_N, DamageMask, or unaff_EDI artifacts.",
        ],
        "notProven": [
            "This does not prove full CThing, referred-object, or CCollisionReport layouts.",
            "This does not prove exact retail labels for every type bit in the masks.",
            "This does not prove runtime collision behavior or source-to-retail identity beyond the documented static evidence.",
            "This does not mutate or run BEA.exe.",
        ],
        "privacy": "Report stores repo-relative paths, public addresses/names, aggregate counts, and summary status only; raw decompile remains ignored under subagents/.",
        "failures": failures,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
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

    report = build_report()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        summary = report["summary"]
        print("Ghidra CThing hit signature tranche")
        print(f"Status: {report['status']}")
        print(f"Output: {relative(out)}")
        print(f"Targets: {summary['targets']}")
        print(f"Renamed targets: {summary['renamedTargets']}")
        print(f"Signature-hardened targets: {summary['signatureHardenedTargets']}")
        print(f"Commented targets: {summary['commentedTargets']}")
        print(f"Stale token hits: {summary['staleTokenHits']}")
        print(f"Overclaim hits: {summary['overclaimHits']}")
        for failure in report["failures"]:
            print(f"FAIL: {failure}", file=sys.stderr)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
