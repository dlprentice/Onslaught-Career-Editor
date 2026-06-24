#!/usr/bin/env python3
"""Validate Wave550 CWeapon construction/teardown Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave550-equipment-weapon-lifecycle-00505e00"
SPECS = {
    "0x00505e00": {
        "raw": "00505e00",
        "name": "CWeapon__ctor_base",
        "signature": "void * __thiscall CWeapon__ctor_base(void * this, void * weapon_data, int create_context)",
        "comment_tokens": (
            "CWorldPhysicsManager__CreateWeaponByIndex allocates 0xb0 bytes",
            "CWeapon table 0x005dfc94",
            "RET 0x8 proves two explicit stack arguments",
            "+0xa4",
            "+0xa8",
            "DAT_008553ec profile entry",
            "Static retail evidence only",
        ),
        "tags": {"cweapon", "constructor", "name-corrected", "owner-corrected"},
        "xref_tokens": ("CWorldPhysicsManager__CreateWeaponByIndex",),
        "decompile_tokens": (
            "void * __thiscall CWeapon__ctor_base(void *this,void *weapon_data,int create_context)",
            "PTR_CWeapon__HandleFireBurstEvent_005dfc94",
            "weapon_data",
            "create_context",
            "Mat34__SetFromEulerDegrees",
            "DAT_008553ec",
            "return this",
        ),
        "instruction_tokens": (
            ("00505e27", "MOV", "0x5d8824"),
            ("00505e54", "MOV", "[EBX + 0xa8]"),
            ("00505e68", "MOV", "0x5dfc94"),
            ("00505e8a", "MOV", "[EBX + 0xa4]"),
            ("00505e90", "CALL", "0x004f8140"),
            ("00505efd", "MOV", "0x008553ec"),
            ("00505f5e", "RET", "0x8"),
        ),
    },
    "0x00505f90": {
        "raw": "00505f90",
        "name": "CWeapon__DetachFromSetAndShutdownMonitor",
        "signature": "void __fastcall CWeapon__DetachFromSetAndShutdownMonitor(void * this)",
        "comment_tokens": (
            "ECX carries CWeapon this",
            "CWeapon__scalar_deleting_dtor",
            "+0x2c",
            "CSPtrSet__Remove",
            "+0x14 global-list nodes",
            "CMonitor__Shutdown(this)",
            "Static retail evidence only",
        ),
        "tags": {"cweapon", "teardown", "dtor-helper"},
        "xref_tokens": ("CWeapon__scalar_deleting_dtor",),
        "decompile_tokens": (
            "void __fastcall CWeapon__DetachFromSetAndShutdownMonitor(void *this)",
            "CSPtrSet__Remove",
            "CParticleManager__RemoveFromGlobalList_Thunk",
            "CMonitor__Shutdown(this)",
        ),
        "instruction_tokens": (
            ("00505fa7", "MOV", "ESI, ECX"),
            ("00505fad", "MOV", "[ESI + 0x2c]"),
            ("00505fc9", "CALL", "0x004e5bd0"),
            ("00505fe0", "CALL", "0x0055db0a"),
            ("00505fef", "CALL", "0x004bac40"),
            ("00506003", "RET", ""),
        ),
    },
}
COMMON_TAGS = {
    "static-reaudit",
    "equipment-weapon-lifecycle-wave550",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
}
OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "source identity proven",
    "rebuild parity proven",
    "fully recovered",
    "complete weapon system",
    "concrete layout proven",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def raw_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return value.zfill(8)


def normalize_address(value: str) -> str:
    return "0x" + raw_address(value)


def token_present(text: str, token: str) -> bool:
    return token.lower() in text.lower()


def parse_summary(path: Path) -> dict[str, int]:
    text = read_text(path)
    match = re.search(
        r"SUMMARY: mode=(dry|apply) updated=(\d+) skipped=(\d+) renamed=(\d+) would_rename=(\d+) missing=(\d+) bad=(\d+)",
        text,
    )
    require(match is not None, f"missing summary in {path}")
    keys = ("updated", "skipped", "renamed", "would_rename", "missing", "bad")
    return {key: int(value) for key, value in zip(keys, match.groups()[1:])}


def check_apply_logs() -> None:
    dry = parse_summary(BASE / "wave550_dry.log")
    apply = parse_summary(BASE / "wave550_apply.log")
    verify = parse_summary(BASE / "wave550_verify_dry.log")
    require(dry == {"updated": 0, "skipped": 2, "renamed": 0, "would_rename": 1, "missing": 0, "bad": 0}, f"dry summary mismatch {dry}")
    require(apply == {"updated": 2, "skipped": 0, "renamed": 1, "would_rename": 0, "missing": 0, "bad": 0}, f"apply summary mismatch {apply}")
    require(verify == {"updated": 0, "skipped": 2, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}, f"verify summary mismatch {verify}")


def check_metadata() -> None:
    rows = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post_metadata.tsv")}
    require(set(rows) == set(SPECS), f"metadata addresses mismatch {sorted(rows)}")
    for address, spec in SPECS.items():
        row = rows[address]
        require(row["name"] == spec["name"], f"{address} metadata name mismatch {row['name']}")
        require(row["signature"] == spec["signature"], f"{address} signature mismatch {row['signature']}")
        require(row["status"] == "OK", f"{address} metadata status {row['status']}")
        for token in spec["comment_tokens"]:
            require(token_present(row["comment"], token), f"{address} comment missing {token!r}")
        lowered = row["comment"].lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lowered, f"{address} comment contains overclaim token {token}")


def check_tags() -> None:
    rows = {raw_address(row["address"]): row for row in read_tsv(BASE / "post_tags.tsv")}
    for spec in SPECS.values():
        row = rows.get(spec["raw"])
        require(row is not None, f"missing tag row for {spec['raw']}")
        tags = set(filter(None, row["tags"].split(";")))
        expected = COMMON_TAGS | spec["tags"]
        require(expected.issubset(tags), f"{spec['raw']} missing tags {sorted(expected - tags)}")


def check_xrefs() -> None:
    rows = read_tsv(BASE / "post_xrefs.tsv")
    by_target: dict[str, list[dict[str, str]]] = {spec["raw"]: [] for spec in SPECS.values()}
    for row in rows:
        target = raw_address(row["target_addr"])
        if target in by_target:
            by_target[target].append(row)
    for spec in SPECS.values():
        target_rows = by_target[spec["raw"]]
        require(target_rows, f"missing xrefs for {spec['raw']}")
        haystack = "\n".join("\t".join(row.values()) for row in target_rows)
        for token in spec["xref_tokens"]:
            require(token in haystack, f"{spec['raw']} xrefs missing {token}")


def check_decompile() -> None:
    for spec in SPECS.values():
        matches = list((BASE / "post_decomp").glob(f"{spec['raw']}_*.c"))
        require(len(matches) == 1, f"expected one decompile for {spec['raw']}, got {len(matches)}")
        text = read_text(matches[0])
        for token in spec["decompile_tokens"]:
            require(token_present(text, token), f"{spec['raw']} decompile missing {token!r}")


def check_instructions() -> None:
    rows = read_tsv(BASE / "post_instructions.tsv")
    haystack = "\n".join(
        "\t".join((row.get("instruction_addr", ""), row.get("mnemonic", ""), row.get("operands", "")))
        for row in rows
    )
    for spec in SPECS.values():
        for addr, mnemonic, operand in spec["instruction_tokens"]:
            require(addr in haystack and mnemonic in haystack and operand.lower() in haystack.lower(),
                    f"{spec['raw']} instruction token missing {(addr, mnemonic, operand)}")


def check_caller_instructions() -> None:
    text = "\n".join("\t".join(row.values()) for row in read_tsv(BASE / "post_caller_instructions.tsv"))
    for token in (
        "0050f77e",
        "PUSH\tECX",
        "0050f77f",
        "PUSH\tESI",
        "0050f780",
        "MOV\tECX, EAX",
        "0050f782",
        "CALL\t0x00505e00",
        "00505f73",
        "CALL\t0x00505f90",
        "00505f8d",
        "RET\t0x4",
    ):
        require(token in text, f"caller instruction export missing {token}")


def check_vtable() -> None:
    rows = read_tsv(BASE / "post_vtable_005dfc94_4.tsv")
    by_slot = {row["slot"]: row for row in rows}
    require(by_slot["0"]["ptr"] == "00506930", "slot 0 pointer mismatch")
    require(by_slot["0"]["ptr_name"] == "CWeapon__HandleFireBurstEvent", "slot 0 name mismatch")
    require(by_slot["1"]["ptr"] == "00505f70", "slot 1 pointer mismatch")
    require(by_slot["1"]["ptr_name"] == "CWeapon__scalar_deleting_dtor", "slot 1 name mismatch")
    require(by_slot["2"]["ptr_name"] == "CMonitor__Shutdown_Core", "slot 2 monitor name mismatch")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        parser.error("expected --check")

    check_apply_logs()
    check_metadata()
    check_tags()
    check_xrefs()
    check_decompile()
    check_instructions()
    check_caller_instructions()
    check_vtable()
    print("Wave550 equipment/weapon lifecycle probe PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
