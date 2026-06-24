#!/usr/bin/env python3
"""Validate the Wave369 feature/monitor boundary recovery tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/feature-monitor-boundary-wave369/current")
OUTPUT_NAME = "feature-monitor-boundary.json"

COMMON_TAGS = {
    "static-reaudit",
    "feature-monitor-boundary-wave369",
    "retail-binary-evidence",
}


def target(name: str, signature: str, comment_tokens: list[str], tags: list[str]) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "tags": tags,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x0044dfb0": target(
        "FenrirEffects__InitBurningAndEngineHandles_0044dfb0",
        "void __thiscall FenrirEffects__InitBurningAndEngineHandles_0044dfb0(void * this, void * initOrContext)",
        ["function boundary", "+0x27c/+0x280", "Fenrir Inside Burning", "Fenrir Engines", "remain unproven"],
        ["function-boundary", "fenrir-effects", "owner-deferred"],
    ),
    "0x0044e4e0": target(
        "PickupSpawn__UpdateAttachedPickupBurst_0044e4e0",
        "void __fastcall PickupSpawn__UpdateAttachedPickupBurst_0044e4e0(void * object)",
        ["function boundary", "PickupSpawn__MaybeSpawnAttachedPickupFromFrame_0044e300", "twice", "remain unproven"],
        ["function-boundary", "pickup-spawn", "owner-deferred"],
    ),
    "0x0044e550": target(
        "GlobalCallback__ClearMatrixBlock006776E8",
        "void __cdecl GlobalCallback__ClearMatrixBlock006776E8(void)",
        ["table 0x00622230", "0x006776e8", "0x006776f0", "remain unproven"],
        ["function-boundary", "global-callback", "matrix-block"],
    ),
    "0x0044e570": target(
        "GlobalCallback__InitMatrixBlock006776B8",
        "void __cdecl GlobalCallback__InitMatrixBlock006776B8(void)",
        ["table 0x00622230", "0x006776b8", "0x006776e4", "matrix-like", "remain unproven"],
        ["function-boundary", "global-callback", "matrix-block"],
    ),
    "0x0044e640": target(
        "ComponentTargeting__ScanListsAndMaybeTriggerAction_0044e640",
        "bool __fastcall ComponentTargeting__ScanListsAndMaybeTriggerAction_0044e640(void * this)",
        ["function boundary", "0x005d96ac", "global list heads", "0x004ffdd0", "remain unproven"],
        ["function-boundary", "component-targeting", "owner-deferred"],
    ),
    "0x0044e9c0": target(
        "GlobalCallback__ClearMatrixBlock00677768",
        "void __cdecl GlobalCallback__ClearMatrixBlock00677768(void)",
        ["table 0x00622230", "0x00677768", "0x00677770", "remain unproven"],
        ["function-boundary", "global-callback", "matrix-block"],
    ),
    "0x0044e9e0": target(
        "GlobalCallback__InitMatrixBlock00677738",
        "void __cdecl GlobalCallback__InitMatrixBlock00677738(void)",
        ["table 0x00622230", "0x00677738", "0x00677764", "matrix-like", "remain unproven"],
        ["function-boundary", "global-callback", "matrix-block"],
    ),
}

VTABLE_EVIDENCE = [
    ("0x005e0440", "5", "0x005e0454", "0x0044dfb0"),
    ("0x005e0590", "7", "0x005e05ac", "0x0044e4e0"),
    ("0x005d96a0", "3", "0x005d96ac", "0x0044e640"),
    ("0x00622230", "2", "0x00622238", "0x0044e550"),
    ("0x00622230", "3", "0x0062223c", "0x0044e570"),
    ("0x00622230", "4", "0x00622240", "0x0044e9c0"),
    ("0x00622230", "5", "0x00622244", "0x0044e9e0"),
]

XREF_EVIDENCE = [
    ("0x0044dfb0", "0x005e0454", "DATA"),
    ("0x0044e4e0", "0x005e05ac", "DATA"),
    ("0x0044e550", "0x00622238", "DATA"),
    ("0x0044e570", "0x0062223c", "DATA"),
    ("0x0044e640", "0x005d96ac", "DATA"),
    ("0x0044e9c0", "0x00622240", "DATA"),
    ("0x0044e9e0", "0x00622244", "DATA"),
]

INSTRUCTION_EVIDENCE = [
    ("0x0044dfb0", "0x0044dfb8", "MOV", "[ESI + 0x27c]"),
    ("0x0044dfb0", "0x0044dfd9", "PUSH", "0x628e4c"),
    ("0x0044dfb0", "0x0044dff6", "PUSH", "0x628e3c"),
    ("0x0044dfb0", "0x0044e012", "RET", "0x4"),
    ("0x0044e4e0", "0x0044e4f1", "CALL", "[EAX + 0x18]"),
    ("0x0044e4e0", "0x0044e536", "CALL", "0x0044e300"),
    ("0x0044e4e0", "0x0044e545", "RET", ""),
    ("0x0044e550", "0x0044e550", "MOV", "0x006776e8"),
    ("0x0044e550", "0x0044e56e", "RET", ""),
    ("0x0044e570", "0x0044e573", "MOV", "0x3f800000"),
    ("0x0044e570", "0x0044e5a7", "MOV", "0x006776b8"),
    ("0x0044e570", "0x0044e632", "RET", ""),
    ("0x0044e640", "0x0044e654", "MOV", "0x855090"),
    ("0x0044e640", "0x0044e97e", "CALL", "0x004ffdd0"),
    ("0x0044e640", "0x0044e9bf", "RET", ""),
    ("0x0044e9c0", "0x0044e9c0", "MOV", "0x00677768"),
    ("0x0044e9c0", "0x0044e9de", "RET", ""),
    ("0x0044e9e0", "0x0044e9e3", "MOV", "0x3f800000"),
    ("0x0044e9e0", "0x0044ea17", "MOV", "0x00677738"),
    ("0x0044e9e0", "0x0044eaa2", "RET", ""),
]

STRING_EVIDENCE = [
    ("string_00628e4c.tsv", "Fenrir Inside Burning"),
    ("string_00628e3c.tsv", "Fenrir Engines"),
]

STALE_TOKENS = ["<none>", "<no_function>", "MISSING", "undefined ", "param_1", "param_2", "unaff_"]
OVERCLAIM_TOKENS = [
    "fully re'ed",
    "100% re",
    "runtime behavior proven",
    "source identity proven",
    "rebuild parity proven",
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
    match = re.search(r"targets=(\d+)\s+changed_or_would_change=(\d+)\s+failed=(\d+)\s+dry=(true|false)", log_text)
    if not match:
        return {}
    return {
        "targets": int(match.group(1)),
        "changed_or_would_change": int(match.group(2)),
        "failed": int(match.group(3)),
        "dry": match.group(4) == "true",
    }


def row_by_addr(rows: list[dict[str, str]], key: str = "address") -> dict[str, dict[str, str]]:
    return {norm_addr(row.get(key, "")): row for row in rows}


def any_row(rows: list[dict[str, str]], predicate) -> bool:
    return any(predicate(row) for row in rows)


def build_report(
    *,
    root: Path = DEFAULT_ROOT,
    dry_log_path: Path | None = None,
    apply_log_path: Path | None = None,
    metadata_path: Path | None = None,
    tags_path: Path | None = None,
    vtable_path: Path | None = None,
    instructions_path: Path | None = None,
    xrefs_path: Path | None = None,
) -> dict[str, object]:
    root = Path(root)
    dry_log_path = dry_log_path or root / "feature_monitor_boundary_dry.log"
    apply_log_path = apply_log_path or root / "feature_monitor_boundary_apply.log"
    metadata_path = metadata_path or root / "metadata_after.tsv"
    tags_path = tags_path or root / "tags_after.tsv"
    vtable_path = vtable_path or root / "vtable_slots_after.tsv"
    instructions_path = instructions_path or root / "instructions_after.tsv"
    xrefs_path = xrefs_path or root / "xrefs_after.tsv"

    failures: list[str] = []
    expected_count = len(TARGETS)
    dry_summary = parse_summary(read_text(dry_log_path))
    apply_summary = parse_summary(read_text(apply_log_path))
    if dry_summary != {"targets": expected_count, "changed_or_would_change": expected_count, "failed": 0, "dry": True}:
        failures.append(f"unexpected dry summary: {dry_summary}")
    if apply_summary != {"targets": expected_count, "changed_or_would_change": expected_count, "failed": 0, "dry": False}:
        failures.append(f"unexpected apply summary: {apply_summary}")

    metadata = row_by_addr(read_tsv(metadata_path, unescape_comment=True))
    tags = row_by_addr(read_tsv(tags_path))
    vtable_rows = read_tsv(vtable_path)
    instruction_rows = read_tsv(instructions_path)
    xref_rows = read_tsv(xrefs_path)

    stale_hits = 0
    overclaim_hits = 0
    for address, spec in TARGETS.items():
        row = metadata.get(norm_addr(address))
        if row is None:
            failures.append(f"missing metadata for {address}")
            continue
        if row.get("status") != "OK":
            failures.append(f"metadata status mismatch for {address}: {row.get('status')}")
        if row.get("name") != spec["name"]:
            failures.append(f"name mismatch for {address}: {row.get('name')} != {spec['name']}")
        if row.get("signature") != spec["signature"]:
            failures.append(f"signature mismatch for {address}: {row.get('signature')} != {spec['signature']}")
        comment = row.get("comment", "")
        for token in spec["commentTokens"]:  # type: ignore[index]
            if not token_present(comment, str(token)):
                failures.append(f"comment token missing for {address}: {token}")
        for token in STALE_TOKENS:
            if token in row.get("signature", ""):
                stale_hits += 1
                failures.append(f"stale signature token for {address}: {token}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                overclaim_hits += 1
                failures.append(f"overclaim token for {address}: {token}")

        tag_row = tags.get(norm_addr(address))
        tag_text = tag_row.get("tags", "") if tag_row else ""
        for tag in sorted(COMMON_TAGS | set(spec["tags"])):  # type: ignore[arg-type]
            if tag not in tag_text:
                failures.append(f"tag missing for {address}: {tag}")

    vtable_hits = 0
    for vtable, slot, slot_addr, pointer in VTABLE_EVIDENCE:
        if any_row(
            vtable_rows,
            lambda row, vtable=vtable, slot=slot, slot_addr=slot_addr, pointer=pointer: (
                norm_addr(row.get("vtable")) == norm_addr(vtable)
                and row.get("slot_index") == slot
                and norm_addr(row.get("slot_addr")) == norm_addr(slot_addr)
                and norm_addr(row.get("pointer_addr")) == norm_addr(pointer)
                and norm_addr(row.get("function_entry")) == norm_addr(pointer)
                and row.get("function_name") == TARGETS[pointer]["name"]
                and row.get("status") == "OK"
            ),
        ):
            vtable_hits += 1
        else:
            failures.append(f"vtable evidence missing: {vtable} slot {slot} -> {pointer}")

    xref_hits = 0
    for target_addr, from_addr, ref_type in XREF_EVIDENCE:
        if any_row(
            xref_rows,
            lambda row, target_addr=target_addr, from_addr=from_addr, ref_type=ref_type: (
                norm_addr(row.get("target_addr")) == norm_addr(target_addr)
                and norm_addr(row.get("from_addr")) == norm_addr(from_addr)
                and row.get("ref_type") == ref_type
            ),
        ):
            xref_hits += 1
        else:
            failures.append(f"xref evidence missing: {target_addr} from {from_addr} {ref_type}")

    instruction_hits = 0
    for target_addr, instr_addr, mnemonic, operand_token in INSTRUCTION_EVIDENCE:
        if any_row(
            instruction_rows,
            lambda row, target_addr=target_addr, instr_addr=instr_addr, mnemonic=mnemonic, operand_token=operand_token: (
                norm_addr(row.get("target_addr")) == norm_addr(target_addr)
                and norm_addr(row.get("instruction_addr")) == norm_addr(instr_addr)
                and row.get("mnemonic") == mnemonic
                and token_present(row.get("operands", ""), operand_token)
                and norm_addr(row.get("function_entry")) == norm_addr(target_addr)
                and row.get("function_name") == TARGETS[target_addr]["name"]
            ),
        ):
            instruction_hits += 1
        else:
            failures.append(f"instruction evidence missing: {target_addr} {instr_addr} {mnemonic} {operand_token}")

    string_hits = 0
    for filename, expected in STRING_EVIDENCE:
        rows = read_tsv(root / filename)
        actual = rows[0].get("cstring", "") if rows else ""
        if actual == expected:
            string_hits += 1
        else:
            failures.append(f"string evidence mismatch: {filename} {actual!r} != {expected!r}")

    status = "PASS" if not failures else "FAIL"
    report: dict[str, object] = {
        "status": status,
        "summary": {
            "targets": expected_count,
            "metadataRows": len(metadata),
            "vtableEvidenceHits": vtable_hits,
            "xrefEvidenceHits": xref_hits,
            "instructionEvidenceHits": instruction_hits,
            "stringEvidenceHits": string_hits,
            "staleHits": stale_hits,
            "overclaimHits": overclaim_hits,
        },
        "failures": failures,
        "inputs": {
            "root": str(root),
            "metadata": str(metadata_path),
            "tags": str(tags_path),
            "vtable": str(vtable_path),
            "instructions": str(instructions_path),
            "xrefs": str(xrefs_path),
        },
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_report(root=args.root)
    out_path = args.out or args.root / OUTPUT_NAME
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"status={report['status']} targets={report['summary']['targets']} output={out_path}")
    if report["status"] != "PASS":
        for failure in report["failures"]:
            print(f"FAIL: {failure}")
        return 1 if args.check else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
