#!/usr/bin/env python3
"""Validate the CAnimal owner/name/signature correction tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "animal-vfunc-owner-correction" / "current"

TARGETS = {
    "0x00403d30": {
        "name": "CAnimal__Init",
        "signatureTokens": ["void", "__thiscall", "void * this", "void * init"],
        "commentTokens": ["CAnimal init correction", "vtable slot 9", "bird_msh", "CComplexThing__Init", "event 3000"],
        "decompileTokens": ["CAnimal__Init", "CComplexThing__Init", "bird_msh", "CEventManager__AddEvent_AtTime", "3000"],
    },
    "0x00404010": {
        "name": "CAnimal__dtor_base",
        "signatureTokens": ["void", "__fastcall", "void * this"],
        "commentTokens": ["CAnimal destructor-base correction", "vtable 0x005d8698", "DAT_00660130", "CComplexThing__dtor_base"],
        "decompileTokens": ["CAnimal__dtor_base", "PTR_LAB_005d8698", "DAT_00660130", "CComplexThing__dtor_base"],
    },
    "0x004041f0": {
        "name": "CAnimal__scalar_deleting_dtor",
        "signatureTokens": ["void *", "__thiscall", "void * this", "byte flags"],
        "commentTokens": ["CAnimal scalar-deleting destructor", "CAnimal__dtor_base", "flags&1", "optionally frees this"],
        "decompileTokens": ["CAnimal__scalar_deleting_dtor", "CAnimal__dtor_base", "OID__FreeObject"],
    },
}

DEFAULT_APPLY_DRY = BASE / "apply_dry.log"
DEFAULT_APPLY = BASE / "apply.log"
DEFAULT_METADATA = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_VTABLE_TYPES = BASE / "vtable_types.tsv"
DEFAULT_OUT = BASE / "animal-vfunc-owner-correction.json"

STALE_NAME_TOKENS = [
    "CAnimal__VFunc_09_00403d30",
    "CAnimal__VFunc_01_004041f0",
    "CAtmospheric__Destructor",
    "void * param_1",
    "int param_2",
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
    apply_dry_log_path: Path = DEFAULT_APPLY_DRY,
    apply_log_path: Path = DEFAULT_APPLY,
    metadata_path: Path = DEFAULT_METADATA,
    decompile_index_path: Path = DEFAULT_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
    vtable_types_path: Path = DEFAULT_VTABLE_TYPES,
) -> dict[str, object]:
    metadata_rows = read_tsv(metadata_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)
    vtable_type_rows = read_tsv(vtable_types_path)

    failures: list[str] = []
    stale_hits: list[dict[str, str]] = []
    target_reports: dict[str, dict[str, object]] = {}

    apply_dry = parse_update_summary(read_text(apply_dry_log_path))
    apply = parse_update_summary(read_text(apply_log_path))
    if apply_dry != {"updated": 0, "skipped": len(TARGETS), "missing": 0, "bad": 0}:
        failures.append(f"unexpected dry summary {apply_dry}")
    if apply != {"updated": len(TARGETS), "skipped": 0, "missing": 0, "bad": 0}:
        failures.append(f"unexpected apply summary {apply}")

    for address, expected in TARGETS.items():
        metadata = find_row(metadata_rows, "address", address)
        index = find_row(index_rows, "address", address)
        decompile_file = decompile_file_for(decompile_dir, address)
        decompile_text = read_text(decompile_file) if decompile_file else ""
        name_sig = " ".join(
            [
                metadata.get("name", "") if metadata else "",
                metadata.get("signature", "") if metadata else "",
                index.get("name", "") if index else "",
                index.get("signature", "") if index else "",
            ]
        )

        report = {
            "name": metadata.get("name") if metadata else None,
            "signature": metadata.get("signature") if metadata else None,
            "comment": metadata.get("comment") if metadata else None,
            "decompileFile": relative(decompile_file) if decompile_file else None,
        }
        target_reports[address] = report

        if metadata is None:
            failures.append(f"{address} missing metadata row")
            continue
        if metadata.get("name") != expected["name"]:
            failures.append(f"{address} name mismatch: {metadata.get('name')} != {expected['name']}")
        if index is None or index.get("name") != expected["name"]:
            failures.append(f"{address} missing/mismatched decompile index row")

        missing_sig = [token for token in expected["signatureTokens"] if not token_present(metadata.get("signature", ""), token)]
        if missing_sig:
            failures.append(f"{address} signature tokens missing: {missing_sig}")
        missing_comment = [token for token in expected["commentTokens"] if not token_present(metadata.get("comment", ""), token)]
        if missing_comment:
            failures.append(f"{address} comment tokens missing: {missing_comment}")
        missing_decompile = [token for token in expected["decompileTokens"] if not token_present(decompile_text, token)]
        if missing_decompile:
            failures.append(f"{address} decompile tokens missing: {missing_decompile}")

        for token in STALE_NAME_TOKENS:
            if token_present(name_sig, token):
                stale_hits.append({"address": address, "token": token})
                failures.append(f"{address} stale name/signature token retained: {token}")

    type_names = {row.get("demangled_type_name", "") for row in vtable_type_rows}
    if "CAnimal" not in type_names:
        failures.append("missing CAnimal RTTI/vtable type row")

    xref_target_count = len({normalize_address(row.get("target_addr", "")) for row in xref_rows if row.get("target_addr")})
    instruction_target_count = len({normalize_address(row.get("target_addr", "")) for row in instruction_rows if row.get("target_addr")})
    if xref_target_count < 2:
        failures.append(f"expected xrefs for at least 2 vtable-referenced targets, got {xref_target_count}")
    if instruction_target_count < len(TARGETS) - 1:
        failures.append(f"expected instruction rows for tranche targets, got {instruction_target_count}")

    summary = {
        "targets": len(TARGETS),
        "metadataRows": len(metadata_rows),
        "decompileRows": len(index_rows),
        "xrefRows": len(xref_rows),
        "instructionRows": len(instruction_rows),
        "vtableTypeRows": len(vtable_type_rows),
        "staleNameTokenHits": len(stale_hits),
        "applyDry": apply_dry,
        "apply": apply,
    }

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-animal-vfunc-owner-correction.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "summary": summary,
        "inputs": {
            "applyDryLog": relative(apply_dry_log_path),
            "applyLog": relative(apply_log_path),
            "metadata": relative(metadata_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
            "vtableTypes": relative(vtable_types_path),
        },
        "targets": target_reports,
        "staleNameTokenHits": stale_hits,
        "failures": failures,
        "nonClaims": [
            "Does not prove exact Stuart-source virtual method names.",
            "Does not prove concrete CAnimal/CAnimalInitThing/CResourceDescriptor layouts.",
            "Does not prove runtime animal spawning, scheduling, model loading, or destructor side effects.",
            "Does not add tags, local variable names, or structure types.",
            "Does not launch, patch, or mutate BEA.exe.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Exit non-zero if the report fails.")
    parser.add_argument("--apply-dry-log", type=Path, default=DEFAULT_APPLY_DRY)
    parser.add_argument("--apply-log", type=Path, default=DEFAULT_APPLY)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--instructions", type=Path, default=DEFAULT_INSTRUCTIONS)
    parser.add_argument("--vtable-types", type=Path, default=DEFAULT_VTABLE_TYPES)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    report = build_report(
        apply_dry_log_path=resolve(args.apply_dry_log),
        apply_log_path=resolve(args.apply_log),
        metadata_path=resolve(args.metadata),
        decompile_index_path=resolve(args.decompile_index),
        decompile_dir=resolve(args.decompile_dir),
        xrefs_path=resolve(args.xrefs),
        instructions_path=resolve(args.instructions),
        vtable_types_path=resolve(args.vtable_types),
    )

    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"Status: {report['status']}")
    print(f"Targets: {report['summary']['targets']}")
    print(f"Stale name token hits: {report['summary']['staleNameTokenHits']}")
    print(f"Report: {relative(out_path)}")
    if args.check and report["status"] != "PASS":
        for failure in report["failures"]:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
