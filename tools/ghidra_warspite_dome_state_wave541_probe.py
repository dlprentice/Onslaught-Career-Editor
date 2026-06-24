#!/usr/bin/env python3
"""Validate Wave541 WarspiteDome state-tail Ghidra read-back."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave541-cvbuftexture-state-tail-00504a50"

COMMON_TAGS = {
    "static-reaudit",
    "warspite-dome-state-wave541",
    "retail-binary-evidence",
    "owner-corrected",
    "signature-corrected",
    "comment-hardened",
}

TARGETS = {
    "0x00504a50": {
        "name": "CWarspiteDome__UpdatePitchStateAndBlendTracks",
        "signature": "void __fastcall CWarspiteDome__UpdatePitchStateAndBlendTracks(void * this)",
        "comment_tokens": ("vtable 0x005e02c0 slot 9", "CWarspiteDome__Init", "CVBufTexture owner prefix as stale", "+0x260/+0x280/+0x284", "+0x268/+0x288"),
        "tags": {"warspite-dome", "state-update", "blend-tracks", "renamed"},
        "decompile_tokens": ("CGroundUnit__UpdateLinkedEffectsByHeightClearance", "CWarspiteDome__UpdateTrackedPitchWithClamp", "this + 0x214", "iVar3 = 6"),
    },
    "0x00504b40": {
        "name": "CWarspiteDome__UpdateTrackedPitchWithClamp",
        "signature": "void __fastcall CWarspiteDome__UpdateTrackedPitchWithClamp(void * this)",
        "comment_tokens": ("flag bit +0x2c bit 2", "OID__SolveBallisticPitchToTarget", "timer +0x20c", "clamps +0xec"),
        "tags": {"warspite-dome", "pitch-clamp", "ballistic-context", "renamed"},
        "decompile_tokens": ("OID__SolveBallisticPitchToTarget", "this + 0x20c", "this + 0xec", "DAT_00672fd0"),
    },
    "0x00504cf0": {
        "name": "CWarspiteDome__ShouldSkipUpdateByStateFlags",
        "signature": "bool __fastcall CWarspiteDome__ShouldSkipUpdateByStateFlags(void * this)",
        "comment_tokens": ("vtable 0x005e02c0 slot 19", "CUnit__HasAnyLinkedUnitBeforeTargetTimeout", "state +0x168", "flag bit +0x2c bit 2"),
        "tags": {"warspite-dome", "state-gate", "linked-timeout", "renamed"},
        "decompile_tokens": ("CUnit__HasAnyLinkedUnitBeforeTargetTimeout", "this + 0x168", "this + 0x214", "return false"),
    },
    "0x00504d30": {
        "name": "CWarspiteDome__IsTransitionAllowedByState",
        "signature": "bool __fastcall CWarspiteDome__IsTransitionAllowedByState(void * this)",
        "comment_tokens": ("vtable 0x005e0380 slot 4", "CUnit__HasAnyLinkedUnitBeforeTargetTimeout", "state field +0x168"),
        "tags": {"warspite-dome", "transition-gate", "linked-timeout", "renamed"},
        "decompile_tokens": ("CUnit__HasAnyLinkedUnitBeforeTargetTimeout", "this + 0x168", "return true"),
    },
}

EXPECTED_XREFS = {
    ("00504a50", "CWarspiteDome__UpdatePitchStateAndBlendTracks", "005e02e4", "<none>", "<no_function>", "DATA"),
    ("00504b40", "CWarspiteDome__UpdateTrackedPitchWithClamp", "00504a5a", "00504a50", "CWarspiteDome__UpdatePitchStateAndBlendTracks", "UNCONDITIONAL_CALL"),
    ("00504cf0", "CWarspiteDome__ShouldSkipUpdateByStateFlags", "005e030c", "<none>", "<no_function>", "DATA"),
    ("00504d30", "CWarspiteDome__IsTransitionAllowedByState", "005e0390", "<none>", "<no_function>", "DATA"),
}

EXPECTED_VTABLE_ROWS = {
    ("005e02c0", "9", "005e02e4", "00504a50", "CWarspiteDome__UpdatePitchStateAndBlendTracks", "OK"),
    ("005e02c0", "19", "005e030c", "00504cf0", "CWarspiteDome__ShouldSkipUpdateByStateFlags", "OK"),
    ("005e0380", "4", "005e0390", "00504d30", "CWarspiteDome__IsTransitionAllowedByState", "OK"),
}

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


def raw_address(value: str) -> str:
    value = value.strip().lower()
    if not value or value.startswith("<"):
        return value
    if value.startswith("0x"):
        value = value[2:]
    return value.zfill(8)


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
        for token in spec["comment_tokens"]:
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
        expected = COMMON_TAGS | set(spec["tags"])
        require(expected.issubset(tags), f"{address} missing tags {sorted(expected - tags)}")


def check_xrefs() -> None:
    actual = {
        (
            raw_address(row["target_addr"]),
            row["target_name"],
            raw_address(row["from_addr"]),
            raw_address(row["from_function_addr"]),
            row["from_function"],
            row["ref_type"],
        )
        for row in read_tsv(BASE / "post_xrefs.tsv")
    }
    missing = EXPECTED_XREFS - actual
    require(not missing, f"missing expected xrefs: {sorted(missing)}")


def check_vtables() -> None:
    actual = {
        (
            raw_address(row["vtable"]),
            row["slot_index"],
            raw_address(row["slot_addr"]),
            raw_address(row["function_entry"]),
            row["function_name"],
            row["status"],
        )
        for row in read_tsv(BASE / "post_vtables.tsv")
    }
    missing = EXPECTED_VTABLE_ROWS - actual
    require(not missing, f"missing expected vtable rows: {sorted(missing)}")


def check_decompile() -> None:
    index = read_tsv(BASE / "post_decomp" / "index.tsv")
    require(len(index) == len(TARGETS), f"decompile index row count {len(index)}")
    for row in index:
        address = normalize_address(row["address"])
        require(row["status"] == "OK", f"{address} decompile status {row['status']}")
        require(address in TARGETS, f"unexpected decompile address {address}")
    for address, spec in TARGETS.items():
        text = decompile_text(address, spec["name"])
        for token in spec["decompile_tokens"]:
            require(token_present(text, token), f"{address} missing decompile token {token!r}")
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lowered, f"{address} overclaim token in decompile: {token}")


def check_logs() -> None:
    require(
        parse_summary(BASE / "apply_warspite_dome_state_tail_wave541_apply.log")
        == {"updated": 4, "skipped": 0, "renamed": 4, "would_rename": 0, "missing": 0, "bad": 0},
        "apply summary mismatch",
    )
    require(
        parse_summary(BASE / "apply_warspite_dome_state_tail_wave541_verify_dry.log")
        == {"updated": 0, "skipped": 4, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
        "verify dry summary mismatch",
    )
    apply_text = read_text(BASE / "apply_warspite_dome_state_tail_wave541_apply.log")
    require("REPORT: Save succeeded" in apply_text, "apply log missing save report")


def check_docs_when_present() -> None:
    docs = [
        ROOT / "release" / "readiness" / "ghidra_warspite_dome_state_wave541_2026-05-18.md",
        ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md",
        ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
        ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Unit.cpp" / "_index.md",
    ]
    for path in docs:
        if not path.is_file():
            continue
        text = read_text(path)
        if "Wave541" not in text:
            continue
        for address, spec in TARGETS.items():
            require(spec["name"] in text, f"{path} missing {spec['name']}")
            require(address in text, f"{path} missing {address}")
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lowered, f"{path} contains overclaim token {token}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run Wave541 checks")
    args = parser.parse_args()
    if not args.check:
        parser.error("--check is required")

    check_metadata()
    check_tags()
    check_xrefs()
    check_vtables()
    check_decompile()
    check_logs()
    check_docs_when_present()
    print("Wave541 WarspiteDome state-tail probe PASS: 4 functions, vtable/read-back evidence verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
