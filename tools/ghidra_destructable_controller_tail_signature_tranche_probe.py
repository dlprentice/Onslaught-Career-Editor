#!/usr/bin/env python3
"""Validate the saved destructable-controller tail Ghidra signature/comment tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/destructable-controller-tail-wave350/current")
OUTPUT_NAME = "destructable-controller-tail-signature-tranche.json"

COMMON_TAGS = {
    "static-reaudit",
    "destructable-controller-tail-wave350",
    "destructable-segments",
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
    "0x00444450": target(
        "CDestructableSegmentsController__SetSegmentField0CByName",
        "void __thiscall CDestructableSegmentsController__SetSegmentField0CByName(void * this, void * segmentName, float segmentValue)",
        ["Name-dispatch controller helper", "field +0x0c", "float value", "remain unproven"],
        ["segmentName", "segmentValue", "CDestroyableSegment__FindChildByNameI", "0xc"],
        ["name-dispatch", "segment-value", "signature-correction"],
    ),
    "0x004444b0": target(
        "CDestructableSegmentsController__SetSegmentFields0C10ByName",
        "void __thiscall CDestructableSegmentsController__SetSegmentFields0C10ByName(void * this, void * segmentName, float segmentValue)",
        ["fields +0x0c and +0x10", "cached active-value", "RET 0x8", "remain unproven"],
        ["segmentName", "segmentValue", "CDestroyableSegment__FindChildByNameI", "CDestroyableSegment__SumActiveValueRecursive"],
        ["name-dispatch", "segment-value", "cache-refresh", "signature-correction"],
    ),
    "0x00444520": target(
        "CDestructableSegmentsController__FindSegmentByName",
        "void * __thiscall CDestructableSegmentsController__FindSegmentByName(void * this, void * segmentName)",
        ["Name-dispatch controller lookup", "tracked segment array", "fatal warning", "remain unproven"],
        ["segmentName", "CDestroyableSegment__FindChildByNameI", "return"],
        ["name-dispatch", "lookup", "signature-correction"],
    ),
    "0x00444580": target(
        "CDestructableSegmentsController__SetAllSegmentsField0C",
        "void __thiscall CDestructableSegmentsController__SetAllSegmentsField0C(void * this, float segmentValue)",
        ["Bulk controller setter", "field +0x0c", "single float stack argument", "remain unproven"],
        ["segmentValue", "0xc"],
        ["bulk-setter", "segment-value", "signature-correction"],
    ),
    "0x004445b0": target(
        "CDestructableSegmentsController__SetSegmentActiveFlagByName",
        "void __thiscall CDestructableSegmentsController__SetSegmentActiveFlagByName(void * this, void * segmentName, int activeFlag)",
        ["field +0x1c", "cached active-value", "byte/bool-derived flag", "remain unproven"],
        ["segmentName", "activeFlag", "CDestroyableSegment__SumActiveValueRecursive", "0x1c"],
        ["name-dispatch", "active-flag", "cache-refresh", "signature-correction"],
    ),
    "0x00444660": target(
        "CDestructableSegmentsController__Init",
        "void __fastcall CDestructableSegmentsController__Init(void * this)",
        ["CUnit__Init", "tracked segment array", "Stuart's matching controller source body is not present", "remain unproven"],
        ["CDestructableSegmentsController__ProcessNode", "CDestructableSegmentsController__FindMemberByField270", "CDestructableSegment__RegisterChild"],
        ["init", "mesh-walk", "component-link", "signature-correction"],
    ),
    "0x004449c0": target(
        "CDestructableSegmentsController__CreateSegment",
        "void * __thiscall CDestructableSegmentsController__CreateSegment(void * this, int segmentKind, void * meshNode, void * parentSegment, float segmentValue)",
        ["segment factory", "CDestroyableCoreSegment__Init", "vtable variants", "remain unproven"],
        ["segmentKind", "meshNode", "parentSegment", "segmentValue", "PTR_LAB_005db148"],
        ["factory", "mesh-walk", "vtable-selection", "signature-correction"],
    ),
    "0x00444c10": target(
        "CDestructableSegmentsController__ProcessNode",
        "void __thiscall CDestructableSegmentsController__ProcessNode(void * this, void * meshNode, void * parentSegment)",
        ["Recursive controller mesh-node processor", "segmentValue", "recurses over child nodes", "remain unproven"],
        ["meshNode", "parentSegment", "CDestructableSegmentsController__CreateSegment", "DAT_00672768"],
        ["mesh-walk", "recursive", "factory-caller", "signature-correction"],
    ),
}

STALE_TOKENS = [
    "undefined ",
    "param_",
]

OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "source identity proven",
    "exact class layout proven",
    "rebuild parity proven",
]

RET_EVIDENCE = {
    "0x00444450": "0x8",
    "0x004444b0": "0x8",
    "0x00444520": "0x4",
    "0x00444580": "0x4",
    "0x004445b0": "0x8",
    "0x00444660": "",
    "0x004449c0": "0x10",
    "0x00444c10": "0x8",
}

CALLSITE_EVIDENCE = [
    ("0x005354b1", "CALL", "0x00444450"),
    ("0x005354f1", "CALL", "0x004444b0"),
    ("0x0047feff", "CALL", "0x00444520"),
    ("0x00535525", "CALL", "0x00444580"),
    ("0x00534333", "CALL", "0x004445b0"),
    ("0x004f9078", "CALL", "0x00444660"),
    ("0x0044471d", "CALL", "0x00444c10"),
    ("0x00444d2a", "CALL", "0x004449c0"),
    ("0x00444e38", "CALL", "0x004449c0"),
    ("0x00444e98", "CALL", "0x00444c10"),
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
    instructions_path: Path | None = None,
    callsite_instructions_path: Path | None = None,
    decompile_dir: Path | None = None,
    caller_decompile_dir: Path | None = None,
) -> dict[str, object]:
    root = Path(root)
    dry_log_path = dry_log_path or root / "destructable_controller_tail_dry.log"
    apply_log_path = apply_log_path or root / "destructable_controller_tail_apply.log"
    metadata_path = metadata_path or root / "metadata_final.tsv"
    tags_path = tags_path or root / "tags_final.tsv"
    xrefs_path = xrefs_path or root / "xrefs_final.tsv"
    instructions_path = instructions_path or root / "instructions_final.tsv"
    callsite_instructions_path = callsite_instructions_path or root / "callsite_instructions_final.tsv"
    decompile_dir = decompile_dir or root / "decompile_final"
    caller_decompile_dir = caller_decompile_dir or root / "caller_decompile_final"

    failures: list[str] = []
    metadata = read_tsv(metadata_path)
    tags = read_tsv(tags_path)
    xrefs = read_tsv(xrefs_path)
    instructions = read_tsv(instructions_path)
    callsite_instructions = read_tsv(callsite_instructions_path)
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
    stale_hits = 0
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
                stale_hits += 1
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

    xref_targets = {normalize_address(row.get("target_addr", "")) for row in xrefs}
    for address in TARGETS:
        if normalize_address(address) not in xref_targets:
            failures.append(f"missing xref row for {address}")

    ret_hits = 0
    for address, operand in RET_EVIDENCE.items():
        hit = any(
            normalize_address(row.get("function_entry", "")) == normalize_address(address)
            and row.get("mnemonic") == "RET"
            and (row.get("operands") or "") == operand
            for row in instructions
        )
        if hit:
            ret_hits += 1
        else:
            failures.append(f"missing RET {operand or '<empty>'} evidence for {address}")

    callsite_hits = 0
    for target_addr, mnemonic, operand in CALLSITE_EVIDENCE:
        hit = any(
            normalize_address(row.get("target_addr", "")) == normalize_address(target_addr)
            and row.get("role") == "TARGET"
            and row.get("mnemonic") == mnemonic
            and normalize_address(row.get("operands", "")) == normalize_address(operand)
            for row in callsite_instructions
        )
        if hit:
            callsite_hits += 1
        else:
            failures.append(f"missing callsite evidence: {target_addr} {mnemonic} {operand}")

    caller_text = (
        "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in sorted(caller_decompile_dir.glob("*.c")))
        if caller_decompile_dir.is_dir()
        else ""
    )
    for token in [
        "CUnit__Init",
        "CDestructableSegmentsController__Init",
    ]:
        if not token_present(caller_text, token):
            failures.append(f"caller decompile missing token: {token}")

    return {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "summary": {
            "targets": len(TARGETS),
            "metadataRows": len(metadata),
            "tagRows": len(tags),
            "xrefRows": len(xrefs),
            "instructionRows": len(instructions),
            "callsiteInstructionRows": len(callsite_instructions),
            "decompileHits": decompile_hits,
            "retEvidenceHits": ret_hits,
            "callsiteEvidenceHits": callsite_hits,
            "commentOverclaims": comment_overclaims,
            "staleTokenHits": stale_hits,
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
