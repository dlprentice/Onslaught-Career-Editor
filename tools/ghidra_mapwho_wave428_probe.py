#!/usr/bin/env python3
"""Validate the Wave428 CMapWho saved-Ghidra correction."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave428-mapwho" / "current"

COMMON_TAGS = {"static-reaudit", "mapwho-wave428", "spatial-query", "retail-binary-evidence"}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    decompile_tokens: list[str],
    tags: list[str],
    xref_tokens: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "decompileTokens": decompile_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "xrefTokens": xref_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x00491900": target(
        "CMapWhoEntry__Init",
        "void __fastcall CMapWhoEntry__Init(void * entry)",
        ["RET with no stack cleanup", "entry", "clears +0x00/+0x04", "mapwho.cpp", "runtime spatial-query behavior", "rebuild parity remain unproven"],
        ["entry", "entry + 4"],
        ["entry-init", "signature-corrected", "comment-hardened"],
        ["CMapWho__Init"],
    ),
    "0x00491930": target(
        "CMapWho__Destroy",
        "void __fastcall CMapWho__Destroy(void * this)",
        ["RET with no stack cleanup", "+0x90", "CDXLandscape__DestroyArrayWithCallback", "OID__FreeObject", "mapwho.cpp", "runtime spatial-query behavior", "rebuild parity remain unproven"],
        ["this + 0x90", "CDXLandscape__DestroyArrayWithCallback", "OID__FreeObject"],
        ["destroy", "signature-corrected", "comment-hardened"],
        ["CGame__ShutdownRestartLoop"],
    ),
    "0x004919b0": target(
        "CMapWho__Init",
        "void __fastcall CMapWho__Init(void * this)",
        ["RET with no stack cleanup", "allocates five level arrays", "64x64 down to 4x4", "+0x90", "fatal construction warning", "mapwho.cpp", "runtime spatial-query behavior", "rebuild parity remain unproven"],
        ["OID__AllocObject", "CMapWhoEntry__Init", "s_FATAL_ERROR__Mapwho_construction"],
        ["init", "quadtree-levels", "signature-corrected", "comment-hardened"],
        ["CGame__InitRestartLoop"],
    ),
    "0x00491c50": target(
        "CMapWho__GetLevelForRadius",
        "int __thiscall CMapWho__GetLevelForRadius(void * this, float radius)",
        ["RET 0x4", "radius", "+0xa4", "object is too big", "mapwho.cpp", "runtime spatial-query behavior", "rebuild parity remain unproven"],
        ["radius", "Object_too_big", "this + 0xa4"],
        ["radius-level", "signature-corrected", "comment-hardened"],
        ["CMapWhoEntry__SetPosition"],
    ),
    "0x00491cd0": target(
        "CMapWho__AddEntry",
        "void __thiscall CMapWho__AddEntry(void * this, void * entry)",
        ["RET 0x4", "entry", "sector head", "doubly linked list", "+0x90", "mapwho.cpp", "runtime spatial-query behavior", "rebuild parity remain unproven"],
        ["entry", "this + 0x90", "entry + 4"],
        ["entry-list", "signature-corrected", "comment-hardened"],
        ["CMapWhoEntry__SetPosition", "CMapWhoEntry__UpdatePosition"],
    ),
    "0x00491d20": target(
        "CMapWho__RemoveEntry",
        "void __thiscall CMapWho__RemoveEntry(void * this, void * entry)",
        ["RET 0x4", "entry", "next/previous links", "sector head", "+0x90", "mapwho.cpp", "runtime spatial-query behavior", "rebuild parity remain unproven"],
        ["entry", "this + 0x90", "entry + 4"],
        ["entry-list", "signature-corrected", "comment-hardened"],
        ["CMapWhoEntry__RemoveFromMap", "CMapWhoEntry__UpdatePosition"],
    ),
    "0x00491d80": target(
        "CMapWho__SetIteratorFromSectorHead",
        "void * __thiscall CMapWho__SetIteratorFromSectorHead(void * this, void * sector_entry)",
        ["RET 0x4", "sector_entry", "writes the sector head at +0x04 into this +0x00", "returns the current entry through EAX", "supersedes the stale CCollisionSeekingRound owner", "mapwho.cpp", "runtime spatial-query behavior", "rebuild parity remain unproven"],
        ["sector_entry", "sector_entry + 4", "return"],
        ["iterator", "owner-corrected", "signature-corrected", "comment-hardened"],
        ["CVBufTexture__RenderDynamicUnitPass", "CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions", "CDXTrees__BuildTreeGeometry"],
    ),
    "0x00491d90": target(
        "CMapWho__AdvanceIteratorAndGetCurrent",
        "void * __fastcall CMapWho__AdvanceIteratorAndGetCurrent(void * this)",
        ["RET with no stack cleanup", "advances this +0x00 through the current entry next pointer", "returns the current entry through EAX", "supersedes the stale CCollisionSeekingRound owner", "mapwho.cpp", "runtime spatial-query behavior", "rebuild parity remain unproven"],
        ["this", "return", "*this"],
        ["iterator", "owner-corrected", "signature-corrected", "comment-hardened"],
        ["CVBufTexture__RenderDynamicUnitPass", "CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions", "CDXTrees__BuildTreeGeometry"],
    ),
    "0x00491da0": target(
        "CMapWho__IsSectorCoordInBounds",
        "int __stdcall CMapWho__IsSectorCoordInBounds(void * sector_coord)",
        ["RET 0x4", "sector_coord", "level 0..4", "64 >> (4 - level)", "x/y sector bounds", "mapwho.cpp", "runtime spatial-query behavior", "rebuild parity remain unproven"],
        ["sector_coord", "0x40", "return 1"],
        ["sector-bounds", "owner-corrected", "signature-corrected", "comment-hardened"],
        ["CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions", "CDXTrees__BuildTreeGeometry"],
    ),
    "0x00491df0": target(
        "CMapWho__SetupNextRadiusLevel",
        "int __fastcall CMapWho__SetupNextRadiusLevel(void * this)",
        ["RET with no stack cleanup", "decrements the active level", "query radius at +0x28", "sector bounds at +0x04/+0x08/+0x0c/+0x10", "mapwho.cpp", "runtime spatial-query behavior", "rebuild parity remain unproven"],
        ["this + 0x24", "this + 0x28", "ROUND"],
        ["radius-query", "signature-corrected", "comment-hardened"],
        ["CMapWho__GetFirstEntryWithinRadius", "CMapWho__GetNextEntryWithinRadius"],
    ),
    "0x00491ea0": target(
        "CMapWho__GetFirstEntryWithinRadius",
        "void * __thiscall CMapWho__GetFirstEntryWithinRadius(void * this, float query_x, float query_y, float query_z, float query_w, float radius)",
        ["RET 0x14", "query_x/query_y/query_z/query_w", "radius", "seeds radius-query state", "CMapWho__SetupNextRadiusLevel", "mapwho.cpp", "runtime spatial-query behavior", "rebuild parity remain unproven"],
        ["query_x", "radius", "CMapWho__SetupNextRadiusLevel"],
        ["radius-query", "signature-corrected", "comment-hardened"],
        ["CAirGuide__AcquireNearestTargetReader", "CBattleEngine__HandleAutoAim", "CEngine__FindNearbyHostileWithinProjectileRadius"],
    ),
    "0x00492020": target(
        "CMapWho__GetNextEntryWithinRadius",
        "void * __fastcall CMapWho__GetNextEntryWithinRadius(void * this)",
        ["RET with no stack cleanup", "checks the active flag", "GetNextEntryWithinRadius not set up", "CMapWho__SetupNextRadiusLevel", "mapwho.cpp", "runtime spatial-query behavior", "rebuild parity remain unproven"],
        ["GetNextEntryWithinRadius", "CMapWho__SetupNextRadiusLevel", "this + 100"],
        ["radius-query", "signature-corrected", "comment-hardened"],
        ["CAirGuide__AcquireNearestTargetReader", "CBattleEngine__HandleAutoAim", "CEngine__FindNearbyHostileWithinProjectileRadius"],
    ),
}

EXPECTED_DRY = {"updated": 0, "skipped": 12, "renamed": 0, "would_rename": 4, "missing": 0, "bad": 0}
EXPECTED_APPLY = {"updated": 12, "skipped": 0, "renamed": 4, "would_rename": 0, "missing": 0, "bad": 0}

INSTRUCTION_RETURNS = {
    "0x00491900": ("RET", ""),
    "0x00491930": ("RET", ""),
    "0x004919b0": ("RET", ""),
    "0x00491c50": ("RET", "0x4"),
    "0x00491cd0": ("RET", "0x4"),
    "0x00491d20": ("RET", "0x4"),
    "0x00491d80": ("RET", "0x4"),
    "0x00491d90": ("RET", ""),
    "0x00491da0": ("RET", "0x4"),
    "0x00491df0": ("RET", ""),
    "0x00491ea0": ("RET", "0x14"),
    "0x00492020": ("RET", ""),
}

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime spatial-query behavior proven",
    "runtime collision behavior proven",
    "source identity proven",
    "concrete layout proven",
    "rebuild parity proven",
    "fully re'ed",
    "100% re",
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
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        for key in ("address", "target_addr", "from_addr", "from_function_addr", "function_entry"):
            if key in row and row[key]:
                row[key] = normalize_address(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def row_by_address(rows: list[dict[str, str]], address: str, key: str = "address") -> dict[str, str] | None:
    wanted = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(key, "")) == wanted:
            return row
    return None


def rows_by_address(rows: list[dict[str, str]], address: str, key: str = "target_addr") -> list[dict[str, str]]:
    wanted = normalize_address(address)
    return [row for row in rows if normalize_address(row.get(key, "")) == wanted]


def decompile_text_for(base: Path, address: str) -> str:
    directory = base / "decompile_after"
    if not directory.is_dir():
        return ""
    matches = sorted(directory.glob(f"{normalize_address(address)[2:]}_*.c"))
    if not matches:
        return ""
    return "\n".join(read_text(path) for path in matches)


def parse_tags(value: str) -> set[str]:
    return {part.strip() for part in value.split(";") if part.strip()}


def parse_summary(path: Path) -> dict[str, int] | None:
    text = read_text(path)
    match = re.search(
        r"SUMMARY\s+updated=(\d+)\s+skipped=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        text,
    )
    if not match:
        return None
    keys = ("updated", "skipped", "renamed", "would_rename", "missing", "bad")
    return {key: int(value) for key, value in zip(keys, match.groups())}


def compare_summary(failures: list[str], label: str, path: Path, expected: dict[str, int]) -> None:
    actual = parse_summary(path)
    if actual is None:
        failures.append(f"{label}: missing SUMMARY")
    elif actual != expected:
        failures.append(f"{label}: summary mismatch {actual} != {expected}")


def check_targets(base: Path = BASE) -> list[str]:
    failures: list[str] = []
    metadata = read_tsv(base / "metadata_after.tsv")
    tags = read_tsv(base / "tags_after.tsv")
    xrefs = read_tsv(base / "xrefs_after.tsv")
    instructions = read_tsv(base / "instructions_after.tsv")

    if metadata:
        compare_summary(failures, "dry", base / "apply_dry.log", EXPECTED_DRY)
        compare_summary(failures, "apply", base / "apply_apply.log", EXPECTED_APPLY)
    else:
        failures.append("metadata_after.tsv: missing or empty")

    for address, expected in TARGETS.items():
        row = row_by_address(metadata, address)
        if row is None:
            failures.append(f"{address}: missing metadata row")
            continue
        expected_name = str(expected["name"])
        expected_signature = str(expected["signature"])
        if row.get("name") != expected_name:
            failures.append(f"{address}: name mismatch {row.get('name')} != {expected_name}")
        if row.get("signature") != expected_signature:
            failures.append(f"{address}: signature mismatch {row.get('signature')} != {expected_signature}")

        comment = row.get("comment", "")
        for token in expected["commentTokens"]:  # type: ignore[assignment]
            if not token_present(comment, str(token)):
                failures.append(f"{address}: missing comment token {token!r}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                failures.append(f"{address}: overclaim token {token!r}")

        tag_row = row_by_address(tags, address)
        if tag_row is None:
            failures.append(f"{address}: missing tags row")
        else:
            actual_tags = parse_tags(tag_row.get("tags", ""))
            expected_tags = COMMON_TAGS | set(expected["tags"])  # type: ignore[arg-type]
            missing = expected_tags - actual_tags
            if missing:
                failures.append(f"{address}: missing tags {sorted(missing)}")

        decompile = decompile_text_for(base, address)
        if not decompile:
            failures.append(f"{address}: missing decompile_after text")
        else:
            for token in expected["decompileTokens"]:  # type: ignore[assignment]
                if not token_present(decompile, str(token)):
                    failures.append(f"{address}: missing decompile token {token!r}")
            for token in OVERCLAIM_TOKENS:
                if token_present(decompile, token):
                    failures.append(f"{address}: decompile overclaim token {token!r}")

        xref_rows = rows_by_address(xrefs, address)
        if not xref_rows:
            failures.append(f"{address}: missing xrefs")
        else:
            combined = "\n".join(" ".join(row.values()) for row in xref_rows)
            for token in expected["xrefTokens"]:  # type: ignore[assignment]
                if not token_present(combined, str(token)):
                    failures.append(f"{address}: missing xref token {token!r}")

        mnemonic, operand = INSTRUCTION_RETURNS[address]
        insn_rows = rows_by_address(instructions, address)
        if not any(row.get("mnemonic") == mnemonic and (not operand or row.get("operands") == operand) for row in insn_rows):
            failures.append(f"{address}: missing instruction terminator {mnemonic} {operand}".rstrip())

    return failures


def build_result(base: Path, failures: list[str]) -> dict[str, object]:
    return {
        "schema": "ghidra-mapwho-wave428.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base": str(base.relative_to(ROOT)) if base.is_relative_to(ROOT) else str(base),
        "status": "PASS" if not failures else "FAIL",
        "target_count": len(TARGETS),
        "classification": "mapwho-radius-query-signature-owner-correction" if not failures else "mapwho-correction-incomplete",
        "not_proven": [
            "runtime spatial-query behavior",
            "runtime collision/render/tree query behavior",
            "concrete CMapWho or CMapWhoEntry layout beyond observed offsets",
            "source-complete identity because mapwho.cpp is absent from the current Stuart snapshot",
            "rebuild parity",
        ],
        "failures": failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--out", type=Path, default=BASE / "mapwho-wave428.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    failures = check_targets(args.base)
    result = build_result(args.base, failures)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if failures:
        print("FAIL ghidra_mapwho_wave428_probe")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PASS ghidra_mapwho_wave428_probe")
    if args.check:
        return 0
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
