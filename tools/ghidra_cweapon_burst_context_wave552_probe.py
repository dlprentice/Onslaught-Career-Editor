#!/usr/bin/env python3
"""Validate Wave552 CWeapon/burst-context Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave552-cengine-burst-context"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cweapon_burst_context_wave552_2026-05-18.md"
GHIDRA_REF = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
STATIC_CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
WORLD_PHYSICS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "WorldPhysicsManager.cpp" / "_index.md"
WALKER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngineWalkerPart.cpp" / "_index.md"

TARGETS = {
    "0x005068f0": {
        "raw": "005068f0",
        "name": "CWeapon__AdvanceChargeProgressIfAnySlotAssigned",
        "signature": "void __fastcall CWeapon__AdvanceChargeProgressIfAnySlotAssigned(void * weapon)",
        "tags": {
            "charge-progress",
            "comment-hardened",
            "cweapon",
            "cweapon-burst-context-wave552",
            "retail-binary-evidence",
            "signature-corrected",
            "slot-scan",
            "stale-owner-corrected",
            "static-reaudit",
            "weapon-data",
        },
        "comment_tokens": (
            "CWeapon/current-entry object",
            "not the core CEngine",
            "CGeneralVolume__DispatchMode3BurstProgressAndSpawn",
            "CBattleEngineWalkerPart__ChargeWeapon",
            "weapon +0xa4",
            "+0x10..+0x1c",
            "DAT_005db358",
            "weapon-data +0x08",
            "runtime charge/fire behavior",
            "remain unproven",
        ),
        "decompile_tokens": (
            "void __fastcall CWeapon__AdvanceChargeProgressIfAnySlotAssigned(void *weapon)",
            "*(int *)((int)weapon + 0xa4)",
            "weapon + 0x60",
            "_DAT_005db358",
        ),
        "xref_functions": (
            "CGeneralVolume__DispatchMode3BurstProgressAndSpawn",
            "CBattleEngineWalkerPart__ChargeWeapon",
        ),
    },
    "0x005078b0": {
        "raw": "005078b0",
        "name": "ProjectileBurstPreset__GetListEntryIdByIndex",
        "signature": "int __thiscall ProjectileBurstPreset__GetListEntryIdByIndex(void * this, int entry_index)",
        "tags": {
            "comment-hardened",
            "cweapon-burst-context-wave552",
            "phantom-param-removed",
            "preset-list",
            "projectile-burst",
            "retail-binary-evidence",
            "signature-corrected",
            "stale-owner-corrected",
            "static-reaudit",
        },
        "comment_tokens": (
            "projectile-burst preset/list object",
            "not the core CEngine",
            "RET 0x4",
            "one explicit stack argument",
            "older second stack parameter was a Ghidra artifact",
            "this +0x4c",
            "entry_index",
            "runtime projectile behavior",
            "remain unproven",
        ),
        "decompile_tokens": (
            "int __thiscall ProjectileBurstPreset__GetListEntryIdByIndex(void *this,int entry_index)",
            "this + 0x4c",
            "entry_index",
            "return *piVar2",
        ),
        "xref_functions": (
            "ProjectileBurst__SpawnFromCurrentPreset",
        ),
    },
}

DOC_TOKENS = {
    PUBLIC_NOTE: (
        "Wave552",
        "CWeapon__AdvanceChargeProgressIfAnySlotAssigned",
        "ProjectileBurstPreset__GetListEntryIdByIndex",
        "updated=2",
        "renamed=2",
        "runtime charge/fire behavior",
    ),
    GHIDRA_REF: (
        "Wave552",
        "CWeapon__AdvanceChargeProgressIfAnySlotAssigned",
        "ProjectileBurstPreset__GetListEntryIdByIndex",
    ),
    STATIC_CAMPAIGN: (
        "Wave 552: CWeapon/Burst Context Stale-Owner Cleanup",
        "updated=2",
        "renamed=2",
        "strict comment-plus-clean-signature proxy",
    ),
    FUNCTION_INDEX: (
        "Wave552",
        "CWeapon__AdvanceChargeProgressIfAnySlotAssigned",
        "ProjectileBurstPreset__GetListEntryIdByIndex",
    ),
    WORLD_PHYSICS_DOC: (
        "Wave552",
        "CWeapon__AdvanceChargeProgressIfAnySlotAssigned",
    ),
    WALKER_DOC: (
        "Wave552",
        "CWeapon__AdvanceChargeProgressIfAnySlotAssigned",
    ),
}

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "source identity proven",
    "exact source identity proven",
    "runtime projectile behavior proven",
    "runtime charge/fire behavior proven",
    "complete cweapon system",
    "fully recovered",
    "concrete layout proven",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_text(path: Path) -> str:
    require(path.exists(), f"missing file: {path}")
    return path.read_text(encoding="utf-8", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    require(path.exists(), f"missing file: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def compact(value: str) -> str:
    return "".join(" ".join((value or "").replace("`", "").split()).lower().split())


def token_present(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def row_for(rows: list[dict[str, str]], key: str, address: str) -> dict[str, str]:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(key, "")) == wanted:
            return row
    raise AssertionError(f"missing row for {address} in {key}")


def parse_summary(path: Path) -> dict[str, int]:
    text = read_text(path)
    match = re.search(
        r"SUMMARY: mode=(dry|apply) updated=(\d+) skipped=(\d+) renamed=(\d+) would_rename=(\d+) missing=(\d+) bad=(\d+)",
        text,
    )
    require(match is not None, f"missing summary in {path}")
    keys = ("updated", "skipped", "renamed", "would_rename", "missing", "bad")
    return {key: int(value) for key, value in zip(keys, match.groups()[1:])}


def check_logs() -> None:
    dry = parse_summary(BASE / "wave552_dry.log")
    apply = parse_summary(BASE / "wave552_apply.log")
    verify = parse_summary(BASE / "wave552_verify_dry.log")
    require(dry == {"updated": 0, "skipped": 2, "renamed": 0, "would_rename": 2, "missing": 0, "bad": 0}, f"dry summary mismatch {dry}")
    require(apply == {"updated": 2, "skipped": 0, "renamed": 2, "would_rename": 0, "missing": 0, "bad": 0}, f"apply summary mismatch {apply}")
    require(verify == {"updated": 0, "skipped": 2, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, f"verify summary mismatch {verify}")
    for path in (BASE / "wave552_dry.log", BASE / "wave552_apply.log", BASE / "wave552_verify_dry.log"):
        text = read_text(path)
        require("REPORT: Save succeeded" in text, f"{path.name} missing save success")
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:"):
            require(bad not in text, f"{path.name} contains {bad}")


def check_metadata() -> None:
    rows = read_tsv(BASE / "post_metadata.tsv")
    require(len(rows) == 2, f"expected 2 metadata rows, got {len(rows)}")
    for address, expected in TARGETS.items():
        row = row_for(rows, "address", address)
        require(row["name"] == expected["name"], f"{address} name mismatch {row['name']}")
        require(row["signature"] == expected["signature"], f"{address} signature mismatch {row['signature']}")
        require(row["status"] == "OK", f"{address} metadata status mismatch {row['status']}")
        for token in expected["comment_tokens"]:
            require(token_present(row["comment"], token), f"{address} comment missing {token!r}")
        lowered = row["comment"].lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lowered, f"{address} comment contains overclaim token {token}")


def check_tags() -> None:
    rows = read_tsv(BASE / "post_tags.tsv")
    require(len(rows) == 2, f"expected 2 tag rows, got {len(rows)}")
    for address, expected in TARGETS.items():
        row = row_for(rows, "address", address)
        tags = set(filter(None, row["tags"].split(";")))
        require(expected["tags"].issubset(tags), f"{address} missing tags {sorted(expected['tags'] - tags)}")


def check_xrefs() -> None:
    rows = read_tsv(BASE / "post_xrefs.tsv")
    require(len(rows) == 3, f"expected 3 xref rows, got {len(rows)}")
    for address, expected in TARGETS.items():
        callers = {
            row["from_function"]
            for row in rows
            if normalize_address(row["target_addr"]) == normalize_address(address)
        }
        require(set(expected["xref_functions"]).issubset(callers), f"{address} xref callers mismatch {callers}")
        for row in rows:
            if normalize_address(row["target_addr"]) == normalize_address(address):
                require(row["target_name"] == expected["name"], f"{address} xref target name mismatch")
                require(row["ref_type"] == "UNCONDITIONAL_CALL", f"{address} xref type mismatch {row['ref_type']}")


def check_decompile() -> None:
    index_rows = read_tsv(BASE / "post_decomp" / "index.tsv")
    require(len(index_rows) == 2, f"expected 2 decompile index rows, got {len(index_rows)}")
    for address, expected in TARGETS.items():
        row = row_for(index_rows, "address", address)
        require(row["name"] == expected["name"], f"{address} decompile index name mismatch")
        require(row["signature"] == expected["signature"], f"{address} decompile index signature mismatch")
        matches = list((BASE / "post_decomp").glob(f"{expected['raw']}_*.c"))
        require(len(matches) == 1, f"{address} expected one decompile export, got {len(matches)}")
        require(expected["name"] in matches[0].name, f"{address} decompile filename mismatch {matches[0].name}")
        text = read_text(matches[0])
        for token in expected["decompile_tokens"]:
            require(token_present(text, token), f"{address} decompile missing {token!r}")

    caller_text = "\n".join(read_text(path) for path in (BASE / "post_caller_decomp").glob("*.c"))
    require(token_present(caller_text, "CWeapon__AdvanceChargeProgressIfAnySlotAssigned(pvVar3);"), "caller decompile missing GeneralVolume renamed call")
    require(token_present(caller_text, "CWeapon__AdvanceChargeProgressIfAnySlotAssigned(pvVar2);"), "caller decompile missing WalkerPart renamed call")
    require(token_present(caller_text, "ProjectileBurstPreset__GetListEntryIdByIndex"), "caller decompile missing preset list renamed call")
    require(not token_present(caller_text, "CEngine__AdvanceProgressIfAnySlotAssigned("), "caller decompile still has old advance-progress name")
    require(not token_present(caller_text, "CEngine__GetListEntryIdByIndex("), "caller decompile still has old list-id name")


def check_instructions() -> None:
    target_rows = read_tsv(BASE / "post_instructions.tsv")
    require(len(target_rows) == 162, f"expected 162 target instruction rows, got {len(target_rows)}")
    target_text = "\n".join("\t".join(row.values()) for row in target_rows)
    for token in (
        "0x005068f1",
        "MOV\tESI, dword ptr [ECX + 0xa4]",
        "CMP\tdword ptr [EDX], -0x1",
        "FLD\tfloat ptr [ECX + 0x60]",
        "FADD\tfloat ptr [ECX + 0x60]",
        "RET\t",
        "0x005078c4",
        "MOV\tESI, dword ptr [ESP + 0x8]",
        "RET\t0x4",
    ):
        require(token_present(target_text, token), f"target instructions missing {token!r}")

    callsite_rows = read_tsv(BASE / "post_callsite_instructions.tsv")
    require(len(callsite_rows) == 45, f"expected 45 callsite rows, got {len(callsite_rows)}")
    callsite_text = "\n".join("\t".join(row.values()) for row in callsite_rows)
    for token in (
        "0x00411d4b",
        "CGeneralVolume__DispatchMode3BurstProgressAndSpawn",
        "CALL\t0x005068f0",
        "0x00413e04",
        "CBattleEngineWalkerPart__ChargeWeapon",
        "CALL\t0x005068f0",
        "0x00506b74",
        "PUSH\tEDX",
        "0x00506b75",
        "ProjectileBurst__SpawnFromCurrentPreset",
        "CALL\t0x005078b0",
    ):
        require(token_present(callsite_text, token), f"callsite instructions missing {token!r}")


def check_docs() -> None:
    for path, tokens in DOC_TOKENS.items():
        text = read_text(path)
        for token in tokens:
            require(token_present(text, token), f"{path}: missing token {token}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    check_logs()
    check_metadata()
    check_tags()
    check_xrefs()
    check_decompile()
    check_instructions()
    check_docs()
    print("Wave552 CWeapon/burst-context probe PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
