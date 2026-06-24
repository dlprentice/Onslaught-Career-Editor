#!/usr/bin/env python3
"""Validate Wave548 CUnit constructor / Mat34 Euler helper Ghidra read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave548-cactor-ctor-orientation-004f7e90"
SPECS = {
    "0x004f7e90": {
        "raw": "004f7e90",
        "name": "CUnit__ctor_base",
        "signature": "void * __fastcall CUnit__ctor_base(void * this)",
        "comment_tokens": (
            "CComplexThing__ctor_base",
            "transient CActor vtables",
            "CUnit primary/secondary vtables 0x005df998/0x005df920",
            "Mat34__SetFromEulerDegrees twice",
            "Static retail evidence only",
        ),
        "tags": {"cunit", "constructor", "owner-corrected"},
        "xref_count": 20,
        "xref_tokens": (
            "OID__CreateObject",
            "CGroundUnit__Constructor",
            "CBigAirUnit__ctor_like_0050ed80",
            "CAirUnit__ctor_like_0050f0a0",
            "CWorldPhysicsManager__CreateThingByType",
            "CWorldPhysicsManager__CreateCharacter",
        ),
        "decompile_tokens": (
            "void * __fastcall CUnit__ctor_base(void *this)",
            "CComplexThing__ctor_base(this)",
            "PTR_CActor__HandleEvent_005d844c",
            "PTR_CUnit__HandleEvent_005df998",
            "Mat34__SetFromEulerDegrees",
            "return this",
        ),
        "instruction_tokens": (
            ("004f7eb2", "CALL", "0x004f3e10"),
            ("004f7eb7", "MOV", "dword ptr [ESI], 0x5d844c"),
            ("004f7f3b", "MOV", "dword ptr [ESI], 0x5df998"),
            ("004f7fe4", "CALL", "0x004f8140"),
            ("004f8018", "CALL", "0x004f8140"),
            ("004f8132", "RET", ""),
        ),
    },
    "0x004f8140": {
        "raw": "004f8140",
        "name": "Mat34__SetFromEulerDegrees",
        "signature": "void __thiscall Mat34__SetFromEulerDegrees(void * this, int yaw_deg, int pitch_deg, int roll_deg)",
        "comment_tokens": (
            "owner-neutral Mat34/FMatrix-style helper",
            "integer yaw_deg, pitch_deg, roll_deg",
            "constant 0x005dfb6c",
            "RET 0x0c",
            "previous CActor-specific label too narrow",
            "Static retail evidence only",
        ),
        "tags": {"mat34", "euler", "owner-corrected"},
        "xref_count": 5,
        "xref_tokens": (
            "CUnit__ctor_base",
            "CEquipment__ctor_like_00505e00",
            "CMonitor__UpdateTrackedRenderPair",
            "ProjectileBurst__SpawnFromCurrentPreset",
        ),
        "decompile_tokens": (
            "void __thiscall Mat34__SetFromEulerDegrees",
            "int yaw_deg",
            "int pitch_deg",
            "int roll_deg",
            "_DAT_005dfb6c",
            "Mat34__SetRows",
            "Mat34__MultiplyBasisToOut",
        ),
        "instruction_tokens": (
            ("004f8146", "FILD", "dword ptr [ESP + 0xa4]"),
            ("004f815a", "FMUL", "float ptr [0x005dfb6c]"),
            ("004f82ee", "CALL", "0x00401ec0"),
            ("004f8426", "CALL", "0x00401ec0"),
            ("004f8490", "ADD", "ESP, 0x98"),
            ("004f8496", "RET", "0xc"),
        ),
    },
}
COMMON_TAGS = {
    "static-reaudit",
    "cunit-ctor-matrix-wave548",
    "retail-binary-evidence",
    "name-corrected",
    "signature-corrected",
    "comment-hardened",
}
OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "source identity proven",
    "rebuild parity proven",
    "fully recovered",
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
        r"SUMMARY updated=(\d+) skipped=(\d+) renamed=(\d+) would_rename=(\d+) missing=(\d+) bad=(\d+)",
        text,
    )
    require(match is not None, f"missing summary in {path}")
    keys = ("updated", "skipped", "renamed", "would_rename", "missing", "bad")
    return {key: int(value) for key, value in zip(keys, match.groups())}


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
    require(len(rows) == 25, f"xref row count {len(rows)}")
    by_target: dict[str, list[dict[str, str]]] = {spec["raw"]: [] for spec in SPECS.values()}
    for row in rows:
        target = raw_address(row["target_addr"])
        if target in by_target:
            by_target[target].append(row)
    for spec in SPECS.values():
        target_rows = by_target[spec["raw"]]
        require(len(target_rows) == spec["xref_count"], f"{spec['raw']} xref count mismatch {len(target_rows)}")
        xref_text = "\n".join(row["from_function"] for row in target_rows)
        for token in spec["xref_tokens"]:
            require(token_present(xref_text, token), f"{spec['raw']} xrefs missing {token!r}")


def check_decompile() -> None:
    index = read_tsv(BASE / "post_decomp" / "index.tsv")
    require(len(index) == 2, f"decompile index row count {len(index)}")
    require(all(row["status"] == "OK" for row in index), "decompile index has non-OK row")
    for spec in SPECS.values():
        text = read_text(BASE / "post_decomp" / f"{spec['raw']}_{spec['name']}.c")
        for token in (
            f"/* name: {spec['name']} */",
            f"/* signature: {spec['signature']} */",
            *spec["decompile_tokens"],
        ):
            require(token_present(text, token), f"{spec['raw']} decompile missing {token!r}")
        lowered = text.lower()
        for token in ("param_1", "param_2", "param_3", "CActor__ctor_like_004f7e90", "CActor__BuildOrientationFromEuler"):
            require(token.lower() not in lowered, f"{spec['raw']} decompile still contains stale token {token}")
        for token in OVERCLAIM_TOKENS:
            require(token not in lowered, f"{spec['raw']} decompile contains overclaim token {token}")


def check_instruction_exports() -> None:
    rows = read_tsv(BASE / "post_instructions.tsv")
    require(len(rows) == 858, f"instruction row count {len(rows)}")
    body = {(raw_address(row["instruction_addr"]), row["mnemonic"], row["operands"]) for row in rows}
    for spec in SPECS.values():
        for item in spec["instruction_tokens"]:
            require(item in body, f"instruction export missing {item}")


def check_logs() -> None:
    require(
        parse_summary(BASE / "apply_cunit_ctor_matrix_wave548_apply.log")
        == {"updated": 2, "skipped": 0, "renamed": 2, "would_rename": 0, "missing": 0, "bad": 0},
        "apply summary mismatch",
    )
    require(
        parse_summary(BASE / "apply_cunit_ctor_matrix_wave548_verify_dry.log")
        == {"updated": 0, "skipped": 2, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        "verify dry summary mismatch",
    )
    require("REPORT: Save succeeded" in read_text(BASE / "apply_cunit_ctor_matrix_wave548_apply.log"), "apply log missing save report")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run Wave548 checks")
    args = parser.parse_args()
    if not args.check:
        parser.error("--check is required")

    check_metadata()
    check_tags()
    check_xrefs()
    check_decompile()
    check_instruction_exports()
    check_logs()
    print("Wave548 CUnit constructor / Mat34 Euler probe PASS: name/signature/comment/read-back evidence verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
