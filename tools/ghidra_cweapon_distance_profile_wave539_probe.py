#!/usr/bin/env python3
"""Validate Wave539 CWeapon distance-profile Ghidra read-back."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave539-battleengine-profile-distance-005061f0"
COMMON_TAGS = {
    "static-reaudit",
    "cweapon-distance-profile-wave539",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
    "cweapon",
    "distance-profile",
    "renamed",
}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    tags: list[str],
    decompile_tokens: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "decompileTokens": decompile_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x005061f0": target(
        "CWeapon__DoesTargetMaskMatchDistanceProfile",
        "bool __thiscall CWeapon__DoesTargetMaskMatchDistanceProfile(void * this, void * target_unit)",
        ["RET 0x4", "target_unit", "this+0x60", "DAT_008553ec", "target_unit+0x34"],
        ["target-mask"],
        [
            "ROUND(*(float *)((int)this + 0x60))",
            "*(int *)((int)this + 0xa4)",
            "DAT_008553ec",
            "*(uint *)(iVar3 + 0xa4)",
            "*(uint *)((int)target_unit + 0x34)",
        ],
    ),
    "0x00506350": target(
        "CWeapon__GetDistanceProfileField90",
        "int __fastcall CWeapon__GetDistanceProfileField90(void * this)",
        ["register-only helper", "this+0x60", "this+0xa4", "entry +0x90"],
        ["field-90"],
        [
            "ROUND(*(float *)((int)this + 0x60))",
            "*(int *)((int)this + 0xa4)",
            "DAT_008553ec",
            "return *(int *)(iVar3 + 0x90)",
        ],
    ),
    "0x00506440": target(
        "CWeapon__GetDistanceProfileField94",
        "double __fastcall CWeapon__GetDistanceProfileField94(void * this)",
        ["register-only helper", "CBattleEngine__AddProjectile", "this+0xa4", "float +0x94"],
        ["field-94"],
        [
            "ROUND(*(float *)((int)this + 0x60))",
            "*(int *)((int)this + 0xa4)",
            "DAT_008553ec",
            "return (double)*(float *)(iVar3 + 0x94)",
        ],
    ),
    "0x00506530": target(
        "CWeapon__GetDistanceProfileFieldA8",
        "int __fastcall CWeapon__GetDistanceProfileFieldA8(void * this)",
        ["register-only helper", "firing-mode selector", "this+0xa4", "entry +0xa8"],
        ["field-a8"],
        [
            "ROUND(*(float *)((int)this + 0x60))",
            "*(int *)((int)this + 0xa4)",
            "DAT_008553ec",
            "return *(int *)(iVar3 + 0xa8)",
        ],
    ),
    "0x00506620": target(
        "CWeapon__GetDistanceProfileField98",
        "double __fastcall CWeapon__GetDistanceProfileField98(void * this)",
        ["register-only helper", "cosine facing checks", "this+0xa4", "float +0x98"],
        ["field-98"],
        [
            "ROUND(*(float *)((int)this + 0x60))",
            "*(int *)((int)this + 0xa4)",
            "DAT_008553ec",
            "return (double)*(float *)(iVar3 + 0x98)",
        ],
    ),
    "0x00506710": target(
        "CWeapon__GetDistanceProfileField9C",
        "double __fastcall CWeapon__GetDistanceProfileField9C(void * this)",
        ["register-only helper", "target-search range scale", "this+0xa4", "float +0x9c"],
        ["field-9c"],
        [
            "ROUND(*(float *)((int)this + 0x60))",
            "*(int *)((int)this + 0xa4)",
            "DAT_008553ec",
            "return (double)*(float *)(iVar3 + 0x9c)",
        ],
    ),
    "0x00506800": target(
        "CWeapon__GetDistanceProfileFieldA0",
        "double __fastcall CWeapon__GetDistanceProfileFieldA0(void * this)",
        ["register-only helper", "alternate target-search range scale", "this+0xa4", "float +0xa0"],
        ["field-a0"],
        [
            "ROUND(*(float *)((int)this + 0x60))",
            "*(int *)((int)this + 0xa4)",
            "DAT_008553ec",
            "return (double)*(float *)(iVar3 + 0xa0)",
        ],
    ),
}

EXPECTED_XREFS = {
    ("005061f0", "CWeapon__DoesTargetMaskMatchDistanceProfile", "00406918", "00406560", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
    ("005061f0", "CWeapon__DoesTargetMaskMatchDistanceProfile", "00406b74", "00406560", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
    ("005061f0", "CWeapon__DoesTargetMaskMatchDistanceProfile", "00406dee", "00406da0", "CBattleEngine__SelectNearestForwardTargetFromGlobalSet", "UNCONDITIONAL_CALL"),
    ("00506350", "CWeapon__GetDistanceProfileField90", "004067fc", "00406560", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
    ("00506350", "CWeapon__GetDistanceProfileField90", "00406ad3", "00406560", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
    ("00506440", "CWeapon__GetDistanceProfileField94", "004068cd", "00406560", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
    ("00506440", "CWeapon__GetDistanceProfileField94", "00406a45", "00406560", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
    ("00506440", "CWeapon__GetDistanceProfileField94", "00406aa2", "00406560", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
    ("00506440", "CWeapon__GetDistanceProfileField94", "00406cfa", "00406560", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
    ("00506530", "CWeapon__GetDistanceProfileFieldA8", "00406826", "00406560", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
    ("00506620", "CWeapon__GetDistanceProfileField98", "00406724", "00406560", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
    ("00506620", "CWeapon__GetDistanceProfileField98", "00406a25", "00406560", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
    ("00506620", "CWeapon__GetDistanceProfileField98", "00406ce4", "00406560", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
    ("00506620", "CWeapon__GetDistanceProfileField98", "00406f45", "00406da0", "CBattleEngine__SelectNearestForwardTargetFromGlobalSet", "UNCONDITIONAL_CALL"),
    ("00506710", "CWeapon__GetDistanceProfileField9C", "0040695f", "00406560", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
    ("00506710", "CWeapon__GetDistanceProfileField9C", "00406a63", "00406560", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
    ("00506710", "CWeapon__GetDistanceProfileField9C", "00406ae2", "00406560", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
    ("00506710", "CWeapon__GetDistanceProfileField9C", "00406bce", "00406560", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
    ("00506800", "CWeapon__GetDistanceProfileFieldA0", "00406895", "00406560", "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "UNCONDITIONAL_CALL"),
}

EXPECTED_APPLY = {
    "updated": 7,
    "skipped": 0,
    "renamed": 7,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_VERIFY_DRY = {
    "updated": 0,
    "skipped": 7,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}

CALLER_TOKENS = [
    "CBattleEngineJetPart__GetCurrentWeapon",
    "CBattleEngineWalkerPart__GetCurrentWeapon",
    "CWeapon__DoesTargetMaskMatchDistanceProfile",
    "CWeapon__GetDistanceProfileField90",
    "CWeapon__GetDistanceProfileField94",
    "CWeapon__GetDistanceProfileFieldA8",
    "CWeapon__GetDistanceProfileField98",
    "CWeapon__GetDistanceProfileField9C",
    "CWeapon__GetDistanceProfileFieldA0",
]

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "source identity proven",
    "rebuild parity proven",
    "fully recovered",
)


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if not value or value.startswith("<"):
        return value
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def compact(value: str) -> str:
    return "".join(value.lower().split())


def token_present(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise AssertionError(f"missing TSV: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def parse_summary(path: Path) -> dict[str, int]:
    text = read_text(path)
    match = re.search(
        r"SUMMARY updated=(\d+) skipped=(\d+) renamed=(\d+) would_rename=(\d+) missing=(\d+) bad=(\d+)",
        text,
    )
    require(match is not None, f"missing SUMMARY in {path}")
    keys = ["updated", "skipped", "renamed", "would_rename", "missing", "bad"]
    return {key: int(value) for key, value in zip(keys, match.groups())}


def decompile_text(address: str, expected_name: str) -> str:
    normalized = normalize_address(address)[2:]
    for path in (BASE / "post_decomp").glob(f"{normalized}_*.c"):
        if expected_name in path.name:
            return read_text(path)
    raise AssertionError(f"missing decompile output for {address} {expected_name}")


def check_metadata() -> None:
    rows = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post_metadata.tsv")}
    require(set(rows) == set(TARGETS), f"metadata target mismatch: {sorted(rows)}")
    for address, spec in TARGETS.items():
        row = rows[address]
        require(row["status"] == "OK", f"{address} metadata status {row['status']}")
        require(row["name"] == spec["name"], f"{address} name {row['name']}")
        require(unescape(row["signature"]) == spec["signature"], f"{address} signature {row['signature']}")
        comment = unescape(row["comment"])
        for token in spec["commentTokens"]:  # type: ignore[index]
            require(token_present(comment, token), f"{address} missing comment token {token!r}")
        lowered = comment.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lowered, f"{address} overclaim token in comment: {token}")


def check_tags() -> None:
    rows = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post_tags.tsv")}
    for address, spec in TARGETS.items():
        row = rows.get(address)
        require(row is not None and row["status"] == "OK", f"{address} tag row missing/failed")
        tags = set(filter(None, row["tags"].split(";")))
        expected = set(spec["tags"])  # type: ignore[arg-type]
        require(expected.issubset(tags), f"{address} missing tags {sorted(expected - tags)}")


def check_xrefs() -> None:
    actual = {
        (
            row["target_addr"].lower(),
            row["target_name"],
            row["from_addr"].lower(),
            row["from_function_addr"].lower(),
            row["from_function"],
            row["ref_type"],
        )
        for row in read_tsv(BASE / "post_xrefs.tsv")
    }
    missing = EXPECTED_XREFS - actual
    require(not missing, f"missing expected xrefs: {sorted(missing)}")


def check_decompile() -> None:
    index = read_tsv(BASE / "post_decomp" / "index.tsv")
    ok = {normalize_address(row["address"]) for row in index if row["status"] == "OK"}
    require(ok == set(TARGETS), f"decompile OK mismatch: {sorted(ok)}")
    for address, spec in TARGETS.items():
        text = decompile_text(address, spec["name"])  # type: ignore[arg-type]
        for token in spec["decompileTokens"]:  # type: ignore[index]
            require(token_present(text, token), f"{address} missing decompile token {token!r}")


def check_callers() -> None:
    text = "\n".join(read_text(path) for path in (BASE / "post_caller_decomp").glob("*.c"))
    require(text, "missing post caller decompile text")
    for token in CALLER_TOKENS:
        require(token_present(text, token), f"missing caller token {token!r}")


def check_logs() -> None:
    require(parse_summary(BASE / "apply_cweapon_distance_profile_wave539_apply.log") == EXPECTED_APPLY, "apply summary mismatch")
    require(
        parse_summary(BASE / "apply_cweapon_distance_profile_wave539_verify_dry.log") == EXPECTED_VERIFY_DRY,
        "verify dry summary mismatch",
    )
    apply_text = read_text(BASE / "apply_cweapon_distance_profile_wave539_apply.log")
    require("REPORT: Save succeeded" in apply_text, "apply log missing save report")


def check_docs_when_present() -> None:
    docs = [
        ROOT / "release" / "readiness" / "ghidra_cweapon_distance_profile_wave539_2026-05-18.md",
        ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md",
        ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
        ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "BattleEngine.cpp" / "_index.md",
    ]
    for path in docs:
        if not path.is_file():
            continue
        text = read_text(path)
        if "Wave539" not in text:
            continue
        require("Wave539" in text, f"{path} missing Wave539 marker")
        for address, spec in TARGETS.items():
            require(spec["name"] in text, f"{path} missing {spec['name']}")  # type: ignore[index]
            require(address in text, f"{path} missing {address}")
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lowered, f"{path} contains overclaim token {token}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run Wave539 checks")
    args = parser.parse_args()
    if not args.check:
        parser.error("--check is required")

    check_metadata()
    check_tags()
    check_xrefs()
    check_decompile()
    check_callers()
    check_logs()
    check_docs_when_present()
    print("Wave539 CWeapon distance-profile probe PASS: 7 functions, 19 xrefs, caller/read-back evidence verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
