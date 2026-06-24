#!/usr/bin/env python3
"""Validate the saved CDebris Ghidra signature/boundary tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/debris-wave347/current")
OUTPUT_NAME = "debris-signature-boundary-tranche.json"

COMMON_TAGS = {"static-reaudit", "debris-wave347", "debris", "retail-binary-evidence"}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    decompile_tokens: list[str],
    tags: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "decompileTokens": decompile_tokens,
        "tags": tags,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x004411a0": target(
        "CDebris__Init",
        "void __thiscall CDebris__Init(void * this, void * init)",
        ["Initializes CDebris", "grs_tuft1.MSH", "cg_debrisarea", "global debris list", "remain unproven"],
        ["s_grs_tuft1_MSH", "CComplexThing__Init", "CConsole__RegisterVariable", "DAT_0066eb78"],
        ["init", "vtable-slot", "name-correction"],
    ),
    "0x00441320": target(
        "CDebris__dtor_base",
        "void __fastcall CDebris__dtor_base(void * this)",
        ["Destructor body", "global debris list", "CComplexThing__dtor_base", "remain unproven"],
        ["DAT_0066eb78", "CComplexThing__dtor_base"],
        ["destructor", "name-correction"],
    ),
    "0x00441360": target(
        "CDebris__GetClassName",
        "char * __cdecl CDebris__GetClassName(void)",
        ["Recovered function boundary", "class-name string", "CDebris", "remain unproven"],
        ["CDebris"],
        ["function-boundary", "class-metadata"],
    ),
    "0x00441370": target(
        "CDebris__GetClassId",
        "int __cdecl CDebris__GetClassId(void)",
        ["Recovered function boundary", "0x1f", "class/OID id", "remain unproven"],
        ["0x1f"],
        ["function-boundary", "class-metadata"],
    ),
    "0x00441380": target(
        "CDebris__scalar_deleting_dtor",
        "void * __thiscall CDebris__scalar_deleting_dtor(void * this, int flags)",
        ["scalar-deleting destructor wrapper", "CDebris__dtor_base", "OID__FreeObject", "flags bit 0", "remain unproven"],
        ["CDebris__dtor_base", "OID__FreeObject"],
        ["destructor", "vtable-slot", "name-correction"],
    ),
    "0x004413a0": target(
        "CDebris__Render",
        "void __thiscall CDebris__Render(void * this, int renderFlags)",
        ["Recovered function boundary", "debris fade", "render object", "RF alpha", "remain unproven"],
        ["DAT_0063012c", "_DAT_00628300", "_DAT_00628304"],
        ["function-boundary", "render"],
    ),
    "0x00441420": target(
        "CDebris__RenderImposter",
        "void __fastcall CDebris__RenderImposter(void * this)",
        ["Recovered function boundary", "debris fade", "imposter render", "remain unproven"],
        ["DAT_0063012c", "_DAT_00628300", "_DAT_00628304"],
        ["function-boundary", "render", "imposter"],
    ),
}

STALE_TOKENS = ["ctor_like", "VFunc_09_004411a0", "VFunc_01_00441380", "param_"]
OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "source identity proven",
    "exact class layout proven",
    "rebuild parity proven",
]

EXPECTED_VTABLE_SLOTS = [
    ("0x005daf10", "1", "CDebris__scalar_deleting_dtor"),
    ("0x005daf10", "7", "CDebris__GetClassName"),
    ("0x005daf10", "8", "CDebris__GetClassId"),
    ("0x005daf10", "9", "CDebris__Init"),
]


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


def split_tags(value: str) -> set[str]:
    return {tag.strip() for tag in re.split(r"[;,]", value or "") if tag.strip()}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def decompile_file_for(decompile_dir: Path, address: str) -> Path | None:
    if not decompile_dir.is_dir():
        return None
    matches = sorted(decompile_dir.glob(f"{normalize_address(address)[2:]}_*.c"))
    return matches[0] if matches else None


def parse_summary(log_text: str) -> dict[str, int]:
    match = re.search(r"targets=(\d+)\s+changed_or_would_change=(\d+)\s+failed=(\d+)", log_text)
    if not match:
        return {"targets": -1, "changed": -1, "failed": -1}
    return {"targets": int(match.group(1)), "changed": int(match.group(2)), "failed": int(match.group(3))}


def build_report(
    *,
    root: Path = DEFAULT_ROOT,
    dry_log_path: Path | None = None,
    apply_log_path: Path | None = None,
    metadata_path: Path | None = None,
    tags_path: Path | None = None,
    xrefs_path: Path | None = None,
    vtable_slots_path: Path | None = None,
    instructions_path: Path | None = None,
    decompile_dir: Path | None = None,
    string_path: Path | None = None,
) -> dict[str, object]:
    root = Path(root)
    dry_log_path = dry_log_path or root / "debris_dry.log"
    apply_log_path = apply_log_path or root / "debris_apply.log"
    metadata_path = metadata_path or root / "metadata_final.tsv"
    tags_path = tags_path or root / "tags_final.tsv"
    xrefs_path = xrefs_path or root / "xrefs_final.tsv"
    vtable_slots_path = vtable_slots_path or root / "vtable_slots_final.tsv"
    instructions_path = instructions_path or root / "instructions_final.tsv"
    decompile_dir = decompile_dir or root / "decompile_final"
    string_path = string_path or root / "string_006283e0.tsv"

    failures: list[str] = []
    metadata = read_tsv(metadata_path)
    tags = read_tsv(tags_path)
    xrefs = read_tsv(xrefs_path)
    vtable_slots = read_tsv(vtable_slots_path)
    instructions = read_tsv(instructions_path)
    dry_summary = parse_summary(read_text(dry_log_path))
    apply_summary = parse_summary(read_text(apply_log_path))

    if dry_summary["targets"] != len(TARGETS) or dry_summary["failed"] != 0:
        failures.append(f"dry-run summary unexpected: {dry_summary}")
    if apply_summary["targets"] != len(TARGETS) or apply_summary["failed"] != 0:
        failures.append(f"apply summary unexpected: {apply_summary}")

    metadata_by_addr = {normalize_address(row.get("address", "")): row for row in metadata}
    tags_by_addr = {normalize_address(row.get("address", "")): row for row in tags}

    decompile_hits = 0
    comment_overclaims = 0
    for address, spec in TARGETS.items():
        row = metadata_by_addr.get(normalize_address(address))
        if not row:
            failures.append(f"missing metadata row for {address}")
            continue
        if row.get("name") != spec["name"]:
            failures.append(f"{address} name {row.get('name')} != {spec['name']}")
        if row.get("signature") != spec["signature"]:
            failures.append(f"{address} signature mismatch: {row.get('signature')} != {spec['signature']}")
        combined = row.get("name", "") + " " + row.get("signature", "")
        for stale in STALE_TOKENS:
            if stale in combined:
                failures.append(f"{address} stale token remains: {stale}")
        comment = row.get("comment", "")
        for token in spec["commentTokens"]:
            if not token_present(comment, str(token)):
                failures.append(f"{address} comment missing token: {token}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                comment_overclaims += 1
                failures.append(f"{address} comment overclaim token: {token}")

        tag_row = tags_by_addr.get(normalize_address(address))
        if not tag_row:
            failures.append(f"missing tags row for {address}")
        else:
            expected_tags = COMMON_TAGS | set(spec["tags"])
            actual_tags = split_tags(tag_row.get("tags", ""))
            missing = sorted(expected_tags - actual_tags)
            if missing:
                failures.append(f"{address} missing tags: {missing}")

        decompile_path = decompile_file_for(decompile_dir, address)
        if not decompile_path:
            failures.append(f"missing decompile file for {address}")
        else:
            decompile_text = read_text(decompile_path)
            missing = [token for token in spec["decompileTokens"] if not token_present(decompile_text, str(token))]
            if missing:
                failures.append(f"{address} decompile missing tokens: {missing}")
            else:
                decompile_hits += 1

    vtable_hits = 0
    for vtable, slot, name in EXPECTED_VTABLE_SLOTS:
        hit = any(
            normalize_address(row.get("vtable", "")) == normalize_address(vtable)
            and row.get("slot_index") == slot
            and row.get("function_name") == name
            and row.get("status") == "OK"
            for row in vtable_slots
        )
        if hit:
            vtable_hits += 1
        else:
            failures.append(f"missing vtable evidence: {vtable} slot {slot} -> {name}")

    xref_targets = {normalize_address(row.get("target_addr", "")) for row in xrefs}
    for address in ["0x004411a0", "0x00441320", "0x00441380"]:
        if normalize_address(address) not in xref_targets:
            failures.append(f"missing xref row for {address}")

    ret_evidence = {
        "0x004411a0": "0x4",
        "0x00441380": "0x4",
        "0x004413a0": "0x4",
    }
    ret_hits = 0
    for address, operand in ret_evidence.items():
        hit = any(
            normalize_address(row.get("function_entry", "")) == normalize_address(address)
            and row.get("mnemonic") == "RET"
            and row.get("operands") == operand
            for row in instructions
        )
        if hit:
            ret_hits += 1
        else:
            failures.append(f"missing RET {operand} evidence for {address}")

    string_rows = read_tsv(string_path)
    if not any(row.get("cstring") == "CDebris" for row in string_rows):
        failures.append("missing CDebris class-name string read-back")

    return {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "summary": {
            "targets": len(TARGETS),
            "metadataRows": len(metadata),
            "tagRows": len(tags),
            "xrefRows": len(xrefs),
            "instructionRows": len(instructions),
            "decompileHits": decompile_hits,
            "vtableEvidenceHits": vtable_hits,
            "retEvidenceHits": ret_hits,
            "commentOverclaims": comment_overclaims,
            "drySummary": dry_summary,
            "applySummary": apply_summary,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report(root=args.root)
    args.root.mkdir(parents=True, exist_ok=True)
    (args.root / OUTPUT_NAME).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.check and report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
