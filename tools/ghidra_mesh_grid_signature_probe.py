#!/usr/bin/env python3
"""Validate the Wave366 mesh/fear-grid Ghidra signature tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/mesh-grid-wave366/current")
OUTPUT_NAME = "mesh-grid-signature.json"

COMMON_TAGS = {
    "static-reaudit",
    "mesh-grid-wave366",
    "retail-binary-evidence",
}


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
    "0x0044c1c0": target(
        "CMesh__DeserializeTripletDwords",
        "void __thiscall CMesh__DeserializeTripletDwords(void * this, void * mem_buffer)",
        ["three dwords", "CDXMemBuffer__Read", "ret 0x4", "mem_buffer", "remain unproven"],
        ["CMesh__DeserializeTripletDwords", "mem_buffer", "CDXMemBuffer__Read"],
        ["mesh", "serializer", "signature-hardened"],
    ),
    "0x0044c210": target(
        "CMesh__DeserializeNineDwords",
        "void __thiscall CMesh__DeserializeNineDwords(void * this, void * mem_buffer)",
        ["nine dwords", "CDXMemBuffer__Read", "ret 0x4", "mem_buffer", "remain unproven"],
        ["CMesh__DeserializeNineDwords", "mem_buffer", "CDXMemBuffer__Read"],
        ["mesh", "serializer", "signature-hardened"],
    ),
    "0x0044c3d0": target(
        "CFearGrid__ctor_base",
        "void * __thiscall CFearGrid__ctor_base(void * this, int grid_id)",
        ["constructor-style", "vtable", "0x8008", "grid_id", "remain unproven"],
        ["CFearGrid__ctor_base", "grid_id", "CFearGrid__RebuildOccupancyAndScheduleTick"],
        ["fear-grid", "constructor", "owner-corrected"],
    ),
    "0x0044c440": target(
        "CFearGrid__RebuildOccupancyAndScheduleTick",
        "void __thiscall CFearGrid__RebuildOccupancyAndScheduleTick(void * this)",
        ["occupancy plane", "clearance plane", "0x8008", "1000", "remain unproven"],
        ["CFearGrid__RebuildOccupancyAndScheduleTick", "CFearGrid__LookupFearWeightByArchetype", "CEventManager__AddEvent_AtTime"],
        ["fear-grid", "grid-refresh", "comment-hardened"],
    ),
    "0x0044c720": target(
        "CFearGrid__GetOccupancyAtWorldVector",
        "int __thiscall CFearGrid__GetOccupancyAtWorldVector(void * this, float vector_x, float vector_y, float vector_z, float vector_w)",
        ["owner/name/signature correction", "16-byte by-value vector", "occupancy plane", "ret 0x10", "remain unproven"],
        ["CFearGrid__GetOccupancyAtWorldVector", "vector_x", "vector_y", "+ 8"],
        ["fear-grid", "occupancy", "owner-corrected", "signature-hardened"],
    ),
    "0x0044c780": target(
        "CFearGrid__ReadClearanceAtWorldVectorIfAboveTerrainDelta",
        "int __thiscall CFearGrid__ReadClearanceAtWorldVectorIfAboveTerrainDelta(void * this, float vector_x, float vector_y, float vector_z, float vector_w)",
        ["owner/name/signature correction", "CStaticShadows__SampleShadowHeightBilinear", "clearance plane", "ret 0x10", "remain unproven"],
        [
            "CFearGrid__ReadClearanceAtWorldVectorIfAboveTerrainDelta",
            "CStaticShadows__SampleShadowHeightBilinear",
            "+ 0x4008",
        ],
        ["fear-grid", "clearance", "owner-corrected", "signature-hardened"],
    ),
    "0x0044c810": target(
        "CFearGrid__FindNearestFreeCellSpiral",
        "void __thiscall CFearGrid__FindNearestFreeCellSpiral(void * this, void * inout_world_vector)",
        ["owner/name/signature correction", "spiral", "inout_world_vector", "ret 0x4", "remain unproven"],
        ["CFearGrid__FindNearestFreeCellSpiral", "inout_world_vector", "_DAT_005d8c44"],
        ["fear-grid", "occupancy", "owner-corrected", "signature-hardened"],
    ),
}

XREF_EVIDENCE = [
    ("0x0044c1c0", "0x004a660a", "CMesh__Load", "UNCONDITIONAL_CALL"),
    ("0x0044c210", "0x004a8c89", "CMesh__Load", "UNCONDITIONAL_CALL"),
    ("0x0044c3d0", "0x0046c634", "CGame__InitRestartLoop", "UNCONDITIONAL_CALL"),
    ("0x0044c3d0", "0x0046c671", "CGame__InitRestartLoop", "UNCONDITIONAL_CALL"),
    ("0x0044c440", "0x0044c406", "CFearGrid__ctor_base", "UNCONDITIONAL_CALL"),
    ("0x0044c720", "0x0040ddf3", "CUnitAI__RefreshGridCooldownFromOccupiedCells", "UNCONDITIONAL_CALL"),
    ("0x0044c720", "0x004e751d", "CSquadNormal__Process", "UNCONDITIONAL_CALL"),
    ("0x0044c780", "0x00507b5b", "OID__CanFireAtTarget_BallisticArcA", "UNCONDITIONAL_CALL"),
    ("0x0044c810", "0x004e752d", "CSquadNormal__Process", "UNCONDITIONAL_CALL"),
]

INSTRUCTION_EVIDENCE = [
    ("0x0044c1c0", "0x0044c208", "RET", "0x4"),
    ("0x0044c210", "0x0044c2d6", "RET", "0x4"),
    ("0x0044c3d0", "0x0044c406", "CALL", "0x0044c440"),
    ("0x0044c3d0", "0x0044c41c", "RET", "0x4"),
    ("0x0044c440", "0x0044c452", "LEA", "[EDI + 0x4008]"),
    ("0x0044c440", "0x0044c4af", "CALL", "0x004daff0"),
    ("0x0044c720", "0x0044c767", "MOV", "+ 0x8"),
    ("0x0044c720", "0x0044c76f", "RET", "0x10"),
    ("0x0044c780", "0x0044c78f", "CALL", "0x0047eb80"),
    ("0x0044c780", "0x0044c7e8", "MOV", "+ 0x4008"),
    ("0x0044c780", "0x0044c7f3", "RET", "0x10"),
    ("0x0044c810", "0x0044c923", "FSTP", "[EAX]"),
    ("0x0044c810", "0x0044c939", "RET", "0x4"),
]

CALLSITE_EVIDENCE = [
    ("0x004a660a", "0x004a6607", "PUSH", "EBP", "CMesh__Load"),
    ("0x004a8c89", "0x004a8c86", "PUSH", "EBP", "CMesh__Load"),
    ("0x0046c634", "0x0046c631", "PUSH", "EBX", "CGame__InitRestartLoop"),
    ("0x0046c671", "0x0046c66e", "PUSH", "EDI", "CGame__InitRestartLoop"),
    ("0x0040ddf3", "0x0040ddd0", "SUB", "ESP, 0x10", "CUnitAI__RefreshGridCooldownFromOccupiedCells"),
    ("0x004e751d", "0x004e7503", "SUB", "ESP, 0x10", "CSquadNormal__Process"),
    ("0x00507b5b", "0x00507b40", "SUB", "ESP, 0x10", "OID__CanFireAtTarget_BallisticArcA"),
    ("0x004e752d", "0x004e752c", "PUSH", "EDX", "CSquadNormal__Process"),
]

STALE_SIGNATURE_TOKENS = ["undefined ", "param_1", "param_2", "param_3", "param_4", "unaff_"]
STALE_NAME_TOKENS = [
    "CFearGrid__ctor_like_0044c3d0",
    "CSquadNormal__GetCellValueAtWorldXY",
    "CSquadNormal__FindNearestFreeCellSpiral",
    "OID__ReadHazardGridIfAboveTerrainDelta",
]
OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "source identity proven",
    "fully re'ed",
    "100% re",
    "layout proven",
]


def norm_addr(value: object) -> str:
    text = str(value or "").strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    if not text or text.startswith("<"):
        return text
    return "0x" + text.zfill(8)


def compact(value: str) -> str:
    return "".join(value.lower().split())


def token_present(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def unescape_tsv(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path, *, unescape_comment: bool = False) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if unescape_comment:
        for row in rows:
            row["comment"] = unescape_tsv(row.get("comment", ""))
    return rows


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def parse_summary(log_text: str) -> dict[str, object]:
    match = re.search(r"targets=(\d+)\s+updated=(\d+)\s+skipped=(\d+)\s+failed=(\d+)\s+dry=(true|false)", log_text)
    if not match:
        return {}
    return {
        "targets": int(match.group(1)),
        "updated": int(match.group(2)),
        "skipped": int(match.group(3)),
        "failed": int(match.group(4)),
        "dry": match.group(5) == "true",
    }


def row_by_addr(rows: list[dict[str, str]], key: str = "address") -> dict[str, dict[str, str]]:
    return {norm_addr(row.get(key, "")): row for row in rows}


def decompile_for(decompile_dir: Path, address: str) -> str:
    matches = sorted(decompile_dir.glob(f"{norm_addr(address)[2:]}_*.c"))
    return "\n".join(read_text(path) for path in matches)


def any_row(rows: list[dict[str, str]], predicate) -> bool:
    return any(predicate(row) for row in rows)


def build_report(
    *,
    root: Path = DEFAULT_ROOT,
    dry_log_path: Path | None = None,
    apply_log_path: Path | None = None,
    metadata_path: Path | None = None,
    tags_path: Path | None = None,
    xrefs_path: Path | None = None,
    instructions_path: Path | None = None,
    callsite_instructions_path: Path | None = None,
    decompile_dir: Path | None = None,
) -> dict[str, object]:
    root = Path(root)
    dry_log_path = dry_log_path or root / "mesh_grid_signature_dry.log"
    apply_log_path = apply_log_path or root / "mesh_grid_signature_apply.log"
    metadata_path = metadata_path or root / "metadata_after.tsv"
    tags_path = tags_path or root / "tags_after.tsv"
    xrefs_path = xrefs_path or root / "xrefs_after.tsv"
    instructions_path = instructions_path or root / "instructions_after.tsv"
    callsite_instructions_path = callsite_instructions_path or root / "callsite_instructions_after.tsv"
    decompile_dir = decompile_dir or root / "decompile_after"

    failures: list[str] = []
    metadata = row_by_addr(read_tsv(metadata_path, unescape_comment=True))
    tags = row_by_addr(read_tsv(tags_path))
    xrefs = read_tsv(xrefs_path)
    instructions = read_tsv(instructions_path)
    callsites = read_tsv(callsite_instructions_path)

    expected_count = len(TARGETS)
    dry_summary = parse_summary(read_text(dry_log_path))
    apply_summary = parse_summary(read_text(apply_log_path))
    if dry_summary != {"targets": expected_count, "updated": 0, "skipped": expected_count, "failed": 0, "dry": True}:
        failures.append(f"unexpected dry summary: {dry_summary}")
    if apply_summary != {"targets": expected_count, "updated": expected_count, "skipped": 0, "failed": 0, "dry": False}:
        failures.append(f"unexpected apply summary: {apply_summary}")

    stale_name_hits = 0
    stale_signature_hits = 0
    xref_hits = 0
    instruction_hits = 0
    callsite_hits = 0

    for address, spec in TARGETS.items():
        row = metadata.get(norm_addr(address))
        if row is None:
            failures.append(f"missing metadata for {address}")
            continue

        expected_name = str(spec["name"])
        expected_signature = str(spec["signature"])
        if row.get("name") != expected_name:
            failures.append(f"name mismatch for {address}: {row.get('name')} != {expected_name}")
        if row.get("signature") != expected_signature:
            failures.append(f"signature mismatch for {address}: {row.get('signature')} != {expected_signature}")

        comment = row.get("comment", "")
        for token in spec["commentTokens"]:
            if not token_present(comment, str(token)):
                failures.append(f"missing comment token for {address}: {token}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                failures.append(f"overclaim token in comment for {address}: {token}")

        signature = row.get("signature", "")
        for token in STALE_SIGNATURE_TOKENS:
            if token_present(signature, token):
                stale_signature_hits += 1
                failures.append(f"stale signature token for {address}: {token}")
        name = row.get("name", "")
        for token in STALE_NAME_TOKENS:
            if token_present(name, token):
                stale_name_hits += 1
                failures.append(f"stale name token for {address}: {token}")

        tag_row = tags.get(norm_addr(address), {})
        tag_values = set(filter(None, tag_row.get("tags", "").split(";")))
        missing_tags = (COMMON_TAGS | set(spec["tags"])) - tag_values
        if missing_tags:
            failures.append(f"missing tags for {address}: {sorted(missing_tags)}")

        decompile_text = decompile_for(decompile_dir, address)
        for token in spec["decompileTokens"]:
            if not token_present(decompile_text, str(token)):
                failures.append(f"missing decompile token for {address}: {token}")
        for token in STALE_NAME_TOKENS:
            if token_present(decompile_text, token):
                stale_name_hits += 1
                failures.append(f"stale name token in decompile for {address}: {token}")

    for target, source, from_name, ref_type in XREF_EVIDENCE:
        if any_row(
            xrefs,
            lambda row, target=target, source=source, from_name=from_name, ref_type=ref_type: norm_addr(row.get("target_addr"))
            == norm_addr(target)
            and norm_addr(row.get("from_addr")) == norm_addr(source)
            and row.get("from_function") == from_name
            and row.get("ref_type") == ref_type,
        ):
            xref_hits += 1
        else:
            failures.append(f"missing xref evidence: {target} <- {source} {from_name} {ref_type}")

    for target, addr, mnemonic, operand_token in INSTRUCTION_EVIDENCE:
        if any_row(
            instructions,
            lambda row, target=target, addr=addr, mnemonic=mnemonic, operand_token=operand_token: norm_addr(row.get("target_addr"))
            == norm_addr(target)
            and norm_addr(row.get("instruction_addr")) == norm_addr(addr)
            and row.get("mnemonic") == mnemonic
            and token_present(row.get("operands", ""), operand_token),
        ):
            instruction_hits += 1
        else:
            failures.append(f"missing instruction evidence: {target} {addr} {mnemonic} {operand_token}")

    for target, addr, mnemonic, operand_token, from_name in CALLSITE_EVIDENCE:
        if any_row(
            callsites,
            lambda row, target=target, addr=addr, mnemonic=mnemonic, operand_token=operand_token, from_name=from_name: norm_addr(
                row.get("target_addr")
            )
            == norm_addr(target)
            and norm_addr(row.get("instruction_addr")) == norm_addr(addr)
            and row.get("mnemonic") == mnemonic
            and token_present(row.get("operands", ""), operand_token)
            and row.get("function_name") == from_name,
        ):
            callsite_hits += 1
        else:
            failures.append(f"missing callsite evidence: {target} {addr} {mnemonic} {operand_token} {from_name}")

    return {
        "status": "PASS" if not failures else "FAIL",
        "summary": {
            "targets": expected_count,
            "xrefEvidenceHits": xref_hits,
            "instructionEvidenceHits": instruction_hits,
            "callsiteEvidenceHits": callsite_hits,
            "staleNameHits": stale_name_hits,
            "staleSignatureHits": stale_signature_hits,
        },
        "failures": failures,
        "inputs": {
            "root": str(root),
            "metadata": str(metadata_path),
            "tags": str(tags_path),
            "xrefs": str(xrefs_path),
            "instructions": str(instructions_path),
            "callsiteInstructions": str(callsite_instructions_path),
            "decompileDir": str(decompile_dir),
            "dryLog": str(dry_log_path),
            "applyLog": str(apply_log_path),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    report = build_report(root=args.root)
    out_path = args.out or args.root / OUTPUT_NAME
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"status={report['status']} targets={report['summary']['targets']} out={out_path}")
    print(
        "evidence: "
        f"xrefs={report['summary']['xrefEvidenceHits']}/{len(XREF_EVIDENCE)} "
        f"instructions={report['summary']['instructionEvidenceHits']}/{len(INSTRUCTION_EVIDENCE)} "
        f"callsites={report['summary']['callsiteEvidenceHits']}/{len(CALLSITE_EVIDENCE)}"
    )
    if report["failures"]:
        for failure in report["failures"][:20]:
            print(f"FAIL: {failure}")
        if len(report["failures"]) > 20:
            print(f"FAIL: ... {len(report['failures']) - 20} more")
    if args.check and report["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
