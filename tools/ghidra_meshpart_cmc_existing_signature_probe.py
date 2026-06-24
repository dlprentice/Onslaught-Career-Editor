#!/usr/bin/env python3
"""Validate the saved MeshPart/CMC existing-function signature tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/meshpart-cmc-wave356/current")
OUTPUT_NAME = "meshpart-cmc-existing-signature.json"

COMMON_TAGS = {
    "static-reaudit",
    "meshpart-cmc-wave356",
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
    "0x004956a0": target(
        "Mat34__Add",
        "void __thiscall Mat34__Add(void * this, void * outMatrix, void * rhsMatrix)",
        ["Mat34 add", "ret 0x8", "remain unproven"],
        ["outMatrix", "rhsMatrix"],
        ["math", "signature-hardened", "mat34"],
    ),
    "0x004957d0": target(
        "CMeshPart__AnySubPartNameIsTurretOrStartsWithBarrel",
        "bool __cdecl CMeshPart__AnySubPartNameIsTurretOrStartsWithBarrel(void * partContainer)",
        ["turret", "barrel", "+0x15c/+0x160", "remain unproven"],
        ["partContainer", "turret", "barrel"],
        ["meshpart", "signature-hardened", "token-predicate"],
    ),
    "0x00495930": target(
        "CMCComponent__Ctor",
        "void * __thiscall CMCComponent__Ctor(void * this, void * ownerField8)",
        ["constructor-style", "vtable 0x005dc2d8", "remain unproven"],
        ["ownerField8", "CMotionController__ctor_like_004bae30", "0xc479c000"],
        ["cmccomponent", "constructor", "signature-hardened"],
    ),
    "0x00495960": target(
        "CMCComponent__ScalarDeletingDestructor",
        "void * __thiscall CMCComponent__ScalarDeletingDestructor(void * this, uint flags)",
        ["scalar deleting destructor", "flags bit 0", "CMCComponent__Dtor", "remain unproven"],
        ["flags", "CMCComponent__Dtor", "OID__FreeObject"],
        ["cmccomponent", "destructor", "scalar-deleting", "signature-hardened"],
    ),
    "0x00495980": target(
        "CMCComponent__Dtor",
        "void __thiscall CMCComponent__Dtor(void * this)",
        ["destructor body", "field +0x08", "base destructor", "remain unproven"],
        ["this", "CMotionController__ctor_like_004bae50"],
        ["cmccomponent", "destructor", "signature-hardened"],
    ),
    "0x00495e00": target(
        "Mat34__Subtract",
        "void __thiscall Mat34__Subtract(void * this, void * outMatrix, void * rhsMatrix)",
        ["Mat34 subtract", "ret 0x8", "remain unproven"],
        ["outMatrix", "rhsMatrix"],
        ["math", "signature-hardened", "mat34"],
    ),
    "0x00495ed0": target(
        "Mat34__ScaleByScalar",
        "void __thiscall Mat34__ScaleByScalar(void * this, void * outMatrix, float scalar)",
        ["matrix scale helper", "ret 0x8", "remain unproven"],
        ["outMatrix", "scalar"],
        ["math", "signature-hardened", "mat34"],
    ),
    "0x00496090": target(
        "CMCDropship__Ctor",
        "void * __thiscall CMCDropship__Ctor(void * this, void * ownerField8)",
        ["constructor-style", "vtable 0x005dc304", "remain unproven"],
        ["ownerField8", "CMotionController__ctor_like_004bae30", "0xc479c000"],
        ["cmcdropship", "constructor", "signature-hardened"],
    ),
    "0x004960c0": target(
        "CMCDropship__ScalarDeletingDestructor",
        "void * __thiscall CMCDropship__ScalarDeletingDestructor(void * this, uint flags)",
        ["scalar deleting destructor", "flags bit 0", "CMCDropship__Dtor", "remain unproven"],
        ["flags", "CMCDropship__Dtor", "OID__FreeObject"],
        ["cmcdropship", "destructor", "scalar-deleting", "signature-hardened"],
    ),
    "0x004960e0": target(
        "CMCDropship__Dtor",
        "void __thiscall CMCDropship__Dtor(void * this)",
        ["destructor body", "field +0x08", "base destructor", "remain unproven"],
        ["this", "CMotionController__ctor_like_004bae50"],
        ["cmcdropship", "destructor", "signature-hardened"],
    ),
    "0x00496250": target(
        "CMeshPart__NameDoesNotStartWithDoor",
        "bool __cdecl CMeshPart__NameDoesNotStartWithDoor(void * meshPart)",
        ["Door", "negated result", "remain unproven"],
        ["meshPart", "Door"],
        ["meshpart", "signature-hardened", "token-predicate"],
    ),
    "0x00496270": target(
        "CMeshPart__HasDoorOpeningOrClosingAnimation",
        "bool __cdecl CMeshPart__HasDoorOpeningOrClosingAnimation(void * animationSet)",
        ["DoorOpening", "DoorClosing", "FindAnimationIndex", "remain unproven"],
        ["animationSet", "FindAnimationIndex", "DoorOpening", "DoorClosing"],
        ["meshpart", "signature-hardened", "animation-token"],
    ),
}

XREF_EVIDENCE = [
    ("0x004956a0", "0x0049561b", "UNCONDITIONAL_CALL"),
    ("0x004957d0", "0x004baec0", "UNCONDITIONAL_CALL"),
    ("0x004957d0", "0x004bb090", "UNCONDITIONAL_CALL"),
    ("0x00495930", "0x00427d16", "UNCONDITIONAL_CALL"),
    ("0x00495960", "0x005dc2dc", "DATA"),
    ("0x00495980", "0x00495963", "UNCONDITIONAL_CALL"),
    ("0x00495e00", "0x00495d9e", "UNCONDITIONAL_CALL"),
    ("0x00495ed0", "0x0049ba1a", "UNCONDITIONAL_CALL"),
    ("0x00496090", "0x00446e96", "UNCONDITIONAL_CALL"),
    ("0x004960c0", "0x005dc308", "DATA"),
    ("0x004960e0", "0x004960c3", "UNCONDITIONAL_CALL"),
    ("0x00496250", "0x004baf11", "UNCONDITIONAL_CALL"),
    ("0x00496270", "0x004baf04", "UNCONDITIONAL_CALL"),
]

VTABLE_EVIDENCE = [
    ("0x005dc2d8", "1", "0x005dc2dc", "0x00495960"),
    ("0x005dc304", "1", "0x005dc308", "0x004960c0"),
]

INSTRUCTION_EVIDENCE = [
    ("0x004956a0", "0x00495761", "RET", "0x8"),
    ("0x004957d0", "0x004957e8", "PUSH", "0x62dd20"),
    ("0x004957d0", "0x0049580a", "PUSH", "0x62dd18"),
    ("0x00495930", "0x00495953", "RET", "0x4"),
    ("0x00495960", "0x00495963", "CALL", "0x00495980"),
    ("0x00495980", "0x0049598d", "JMP", "0x004bae50"),
    ("0x00495e00", "0x00495ec1", "RET", "0x8"),
    ("0x00495ed0", "0x00495f97", "RET", "0x8"),
    ("0x00496090", "0x004960b6", "RET", "0x4"),
    ("0x004960c0", "0x004960c3", "CALL", "0x004960e0"),
    ("0x004960e0", "0x004960ed", "JMP", "0x004bae50"),
    ("0x00496250", "0x0049625b", "PUSH", "0x62dd74"),
    ("0x00496270", "0x00496275", "PUSH", "0x62dd88"),
    ("0x00496270", "0x0049628d", "PUSH", "0x62dd7c"),
]

STRING_EVIDENCE = [
    ("string_0062dd20.tsv", "turret"),
    ("string_0062dd74.tsv", "Door"),
    ("string_0062dd7c.tsv", "DoorClosing"),
    ("string_0062dd88.tsv", "DoorOpening"),
]

STALE_SIGNATURE_TOKENS = ["<none>", "<no_function>", "MISSING", "undefined ", "param_1", "param_2", "param_3"]
STALE_DECOMPILE_TOKENS = ["<no_function>", "MISSING", "param_1", "param_2", "param_3"]
OVERCLAIM_TOKENS = ["runtime behavior proven", "source identity proven", "layout proven"]


def norm_addr(value: object) -> str:
    text = str(value or "").strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    if not text or text.startswith("<"):
        return text
    return "0x" + text.zfill(8)


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def parse_summary(log_text: str) -> dict[str, object]:
    result: dict[str, object] = {}
    match = re.search(r"targets=(\d+)\s+changed_or_would_change=(\d+)\s+failed=(\d+)\s+dry=(true|false)", log_text)
    if match:
        result["targets"] = int(match.group(1))
        result["changedOrWouldChange"] = int(match.group(2))
        result["failed"] = int(match.group(3))
        result["dry"] = match.group(4) == "true"
    return result


def row_by_addr(rows: list[dict[str, str]], key: str = "address") -> dict[str, dict[str, str]]:
    return {norm_addr(row.get(key, "")): row for row in rows}


def any_row(rows: list[dict[str, str]], predicate) -> bool:
    return any(predicate(row) for row in rows)


def decompile_for(decompile_dir: Path, address: str, name: str) -> str:
    exact = decompile_dir / f"{address[2:]}_{name}.c"
    if exact.exists():
        return read_text(exact)
    matches = sorted(decompile_dir.glob(f"{address[2:]}_*.c"))
    return "\n".join(read_text(path) for path in matches)


def string_value(path: Path) -> str:
    rows = read_tsv(path)
    if not rows:
        return ""
    return rows[0].get("cstring", "")


def build_report(
    *,
    root: Path = DEFAULT_ROOT,
    dry_log_path: Path | None = None,
    apply_log_path: Path | None = None,
    metadata_path: Path | None = None,
    tags_path: Path | None = None,
    xrefs_path: Path | None = None,
    instructions_path: Path | None = None,
    vtable_path: Path | None = None,
    decompile_dir: Path | None = None,
) -> dict[str, object]:
    dry_log_path = dry_log_path or root / "meshpart_cmc_existing_signature_dry.log"
    apply_log_path = apply_log_path or root / "meshpart_cmc_existing_signature_apply.log"
    metadata_path = metadata_path or root / "metadata_after.tsv"
    tags_path = tags_path or root / "tags_after.tsv"
    xrefs_path = xrefs_path or root / "xrefs_after.tsv"
    instructions_path = instructions_path or root / "instructions_after.tsv"
    vtable_path = vtable_path or root / "vtable_slots_after.tsv"
    decompile_dir = decompile_dir or root / "decompile_after"

    failures: list[str] = []
    metadata = row_by_addr(read_tsv(metadata_path))
    tags = row_by_addr(read_tsv(tags_path))
    xrefs = read_tsv(xrefs_path)
    instructions = read_tsv(instructions_path)
    vtables = read_tsv(vtable_path)

    dry_summary = parse_summary(read_text(dry_log_path))
    apply_summary = parse_summary(read_text(apply_log_path))
    if dry_summary.get("targets") != len(TARGETS) or dry_summary.get("failed") != 0 or dry_summary.get("dry") is not True:
        failures.append(f"dry summary mismatch: {dry_summary}")
    if apply_summary.get("targets") != len(TARGETS) or apply_summary.get("failed") != 0 or apply_summary.get("dry") is not False:
        failures.append(f"apply summary mismatch: {apply_summary}")

    for address, spec in TARGETS.items():
        row = metadata.get(address)
        if not row:
            failures.append(f"{address} metadata missing")
            continue
        if row.get("name") != spec["name"]:
            failures.append(f"{address} name mismatch: {row.get('name')} != {spec['name']}")
        signature = row.get("signature", "")
        if signature != spec["signature"]:
            failures.append(f"{address} signature mismatch: {signature} != {spec['signature']}")
        if any(token in signature for token in STALE_SIGNATURE_TOKENS):
            failures.append(f"{address} stale signature token in {signature!r}")
        comment = row.get("comment", "")
        for token in spec["commentTokens"]:
            if str(token) not in comment:
                failures.append(f"{address} missing comment token {token!r}")
        lower_comment = comment.lower()
        if any(token in lower_comment for token in OVERCLAIM_TOKENS):
            failures.append(f"{address} comment overclaim: {comment}")

        tag_row = tags.get(address, {})
        tag_set = set(filter(None, tag_row.get("tags", "").split(";")))
        expected_tags = COMMON_TAGS | set(spec["tags"])
        missing_tags = sorted(expected_tags - tag_set)
        if missing_tags:
            failures.append(f"{address} missing tags {missing_tags}")

        decompile = decompile_for(decompile_dir, address, str(spec["name"]))
        for token in spec["decompileTokens"]:
            if str(token) not in decompile:
                failures.append(f"{address} missing decompile token {token!r}")
        if any(token in decompile for token in STALE_DECOMPILE_TOKENS):
            failures.append(f"{address} stale decompile token observed")

    xref_hits = 0
    for target_addr, from_addr, ref_type in XREF_EVIDENCE:
        if any_row(
            xrefs,
            lambda row, target_addr=target_addr, from_addr=from_addr, ref_type=ref_type: (
                norm_addr(row.get("target_addr")) == target_addr
                and norm_addr(row.get("from_addr")) == from_addr
                and row.get("ref_type") == ref_type
            ),
        ):
            xref_hits += 1
        else:
            failures.append(f"missing xref evidence {from_addr}->{target_addr} {ref_type}")

    instruction_hits = 0
    for target_addr, instruction_addr, mnemonic, operand_token in INSTRUCTION_EVIDENCE:
        if any_row(
            instructions,
            lambda row, target_addr=target_addr, instruction_addr=instruction_addr, mnemonic=mnemonic, operand_token=operand_token: (
                norm_addr(row.get("target_addr")) == target_addr
                and norm_addr(row.get("instruction_addr")) == instruction_addr
                and row.get("mnemonic") == mnemonic
                and operand_token in row.get("operands", "")
            ),
        ):
            instruction_hits += 1
        else:
            failures.append(f"missing instruction evidence {instruction_addr} {mnemonic} {operand_token}")

    vtable_hits = 0
    for vtable, slot, slot_addr, pointer in VTABLE_EVIDENCE:
        if any_row(
            vtables,
            lambda row, vtable=vtable, slot=slot, slot_addr=slot_addr, pointer=pointer: (
                norm_addr(row.get("vtable")) == vtable
                and row.get("slot_index") == slot
                and norm_addr(row.get("slot_addr")) == slot_addr
                and norm_addr(row.get("pointer_addr")) == pointer
            ),
        ):
            vtable_hits += 1
        else:
            failures.append(f"missing vtable evidence {vtable} slot {slot} -> {pointer}")

    string_hits = 0
    for filename, expected in STRING_EVIDENCE:
        actual = string_value(root / filename)
        if actual == expected:
            string_hits += 1
        else:
            failures.append(f"string evidence mismatch for {filename}: {actual!r} != {expected!r}")

    status = "PASS" if not failures else "FAIL"
    return {
        "schema": "ghidra-meshpart-cmc-existing-signature-v1",
        "status": status,
        "summary": {
            "targets": len(TARGETS),
            "xrefEvidenceHits": xref_hits,
            "instructionEvidenceHits": instruction_hits,
            "vtableEvidenceHits": vtable_hits,
            "stringEvidenceHits": string_hits,
            "failures": len(failures),
        },
        "drySummary": dry_summary,
        "applySummary": apply_summary,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_report(root=args.root)
    args.root.mkdir(parents=True, exist_ok=True)
    out_path = args.root / OUTPUT_NAME
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{report['status']}: wrote {out_path}")
    if args.check and report["status"] != "PASS":
        for failure in report["failures"]:
            print(f"FAIL: {failure}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
