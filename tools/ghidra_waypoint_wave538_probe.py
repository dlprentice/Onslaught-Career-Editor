#!/usr/bin/env python3
"""Validate Wave538 Waypoint/WaypointManager Ghidra read-back."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave538-waypoint-005057b0"
COMMON_TAGS = {
    "static-reaudit",
    "waypoint-wave538",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
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
    "0x005057b0": target(
        "CWaypoint__InitAndLink",
        "void __thiscall CWaypoint__InitAndLink(void * this, void * init)",
        ["vtable 0x005dd2f0 slot 9", "CThing__Init", "0x00855120", "runtime pathing behavior"],
        ["waypoint", "vtable-readback", "renamed", "init", "list-link"],
        [
            "CThing__Init",
            "CSPtrSet__AddToTail",
            "CStaticShadows__SampleShadowHeightBilinear",
            "CGenericActiveReader__SetReader",
        ],
    ),
    "0x00505810": target(
        "CWaypoint__ShutdownAndUnlink",
        "void __fastcall CWaypoint__ShutdownAndUnlink(void * this)",
        ["vtable 0x005dd2f0 slot 2", "0x00855120", "CThing__Shutdown", "runtime pathing behavior"],
        ["waypoint", "vtable-readback", "renamed", "shutdown", "list-unlink"],
        ["CSPtrSet__Remove", "CThing__Shutdown"],
    ),
    "0x00505960": target(
        "CWaypoint__Load",
        "void __thiscall CWaypoint__Load(void * this, void * mem_buffer, int load_mode, void * object_table)",
        ["CWaypointManager__LoadWaypoints calls this", "RET 0x0c", "WaypointManager.cpp line 0x1a", "runtime AI navigation behavior"],
        ["waypoint", "renamed", "load", "mem-buffer", "object-link"],
        ["CDXMemBuffer__Read", "OID__AllocObject", "CSPtrSet__AddToHead", "CConsole__Printf"],
    ),
    "0x00505ab0": target(
        "CWaypointManager__ReleasePendingObjects",
        "void __cdecl CWaypointManager__ReleasePendingObjects(void)",
        ["0x00854fc0", "vtable slot 0", "delete flag 1", "runtime shutdown behavior"],
        ["waypoint", "pending-set", "shutdown", "virtual-dispatch"],
        ["DAT_00854fc0", "CSPtrSet__Remove", "(**(code **)*value)(1)"],
    ),
    "0x00505ae0": target(
        "CWaypointManager__LoadWaypoints",
        "void __cdecl CWaypointManager__LoadWaypoints(void * mem_buffer, int load_mode, void * object_table)",
        ["16-bit waypoint count", "0x18-byte waypoint objects", "CWaypoint__Load", "Loading waypoints"],
        ["waypoint", "load", "mem-buffer", "object-allocation", "status-message"],
        ["OID__AllocObject", "CWaypoint__Load", "CSPtrSet__AddToTail", "CConsole__StatusDone"],
    ),
    "0x005d5860": target(
        "CWaypointManager__LoadWaypoints_unwind",
        "void __cdecl CWaypointManager__LoadWaypoints_unwind(void)",
        ["SEH data xref", "EBP+0x0c", "OID__FreeObject_Callback", "rebuild parity"],
        ["waypoint", "seh-unwind", "allocation-cleanup"],
        ["OID__FreeObject_Callback"],
    ),
}

EXPECTED_XREFS = {
    ("005057b0", "CWaypoint__InitAndLink", "005dd314", "<none>", "<no_function>", "DATA"),
    ("00505810", "CWaypoint__ShutdownAndUnlink", "005dd2f8", "<none>", "<no_function>", "DATA"),
    ("00505960", "CWaypoint__Load", "00505b64", "00505ae0", "CWaypointManager__LoadWaypoints", "UNCONDITIONAL_CALL"),
    ("00505ab0", "CWaypointManager__ReleasePendingObjects", "0050aee2", "0050ada0", "CWorld__ShutdownAndClear", "UNCONDITIONAL_CALL"),
    ("00505ae0", "CWaypointManager__LoadWaypoints", "0050d187", "0050b9c0", "CWorld__LoadWorld", "UNCONDITIONAL_CALL"),
    ("005d5860", "CWaypointManager__LoadWaypoints_unwind", "0061e0cc", "<none>", "<no_function>", "DATA"),
}

EXPECTED_VTABLES = {
    ("005dd2f0", "2", "00505810", "CWaypoint__ShutdownAndUnlink", "OK"),
    ("005dd2f0", "9", "005057b0", "CWaypoint__InitAndLink", "OK"),
    ("005dfc8c", "1", "00617328", "<no_function>", "NO_FUNCTION_AT_POINTER"),
}

EXPECTED_APPLY = {
    "updated": 6,
    "skipped": 0,
    "renamed": 3,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_VERIFY_DRY = {
    "updated": 0,
    "skipped": 6,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "source identity proven",
    "rebuild parity proven",
    "fully re'ed",
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


def check_vtables() -> None:
    actual = {
        (
            row["vtable"].lower(),
            row["slot_index"],
            row["pointer_addr"].lower(),
            row["function_name"],
            row["status"],
        )
        for row in read_tsv(BASE / "post_vtables.tsv")
    }
    missing = EXPECTED_VTABLES - actual
    require(not missing, f"missing expected vtable rows: {sorted(missing)}")


def check_decompile() -> None:
    index = read_tsv(BASE / "post_decomp" / "index.tsv")
    ok = {normalize_address(row["address"]) for row in index if row["status"] == "OK"}
    require(ok == set(TARGETS), f"decompile OK mismatch: {sorted(ok)}")
    for address, spec in TARGETS.items():
        text = decompile_text(address, spec["name"])  # type: ignore[arg-type]
        for token in spec["decompileTokens"]:  # type: ignore[index]
            require(token_present(text, token), f"{address} missing decompile token {token!r}")


def check_logs() -> None:
    require(parse_summary(BASE / "apply_waypoint_wave538_apply.log") == EXPECTED_APPLY, "apply summary mismatch")
    require(
        parse_summary(BASE / "apply_waypoint_wave538_verify_dry.log") == EXPECTED_VERIFY_DRY,
        "verify dry summary mismatch",
    )
    apply_text = read_text(BASE / "apply_waypoint_wave538_apply.log")
    require("REPORT: Save succeeded" in apply_text, "apply log missing save report")


def check_docs_when_present() -> None:
    docs = [
        ROOT / "release" / "readiness" / "ghidra_waypoint_wave538_2026-05-18.md",
        ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "WaypointManager.cpp" / "_index.md",
    ]
    for path in docs:
        if not path.is_file():
            continue
        text = read_text(path)
        for address, spec in TARGETS.items():
            require(spec["name"] in text, f"{path} missing {spec['name']}")  # type: ignore[index]
            require(address in text, f"{path} missing {address}")
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            require(token not in lowered, f"{path} contains overclaim token {token}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run Wave538 checks")
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
    print("Wave538 Waypoint probe PASS: 6 functions, 6 xrefs, vtable/read-back evidence verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
