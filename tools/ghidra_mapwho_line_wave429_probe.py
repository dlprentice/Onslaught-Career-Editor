#!/usr/bin/env python3
"""Validate the Wave429 CMapWho line-query and entry-position correction."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave429-mapwho-line-entry" / "current"

COMMON_TAGS = {"static-reaudit", "mapwho-wave429", "retail-binary-evidence"}


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
    "0x00492110": target(
        "CMapWho__GetFirstEntryWithinLine",
        "void * __thiscall CMapWho__GetFirstEntryWithinLine(void * this, float line_start_x, float line_start_y, float line_start_z, float line_start_w, float line_end_x, float line_end_y, float line_end_z, float line_end_w)",
        ["RET 0x20", "line_start", "line_end", "Geometry__ClipSegmentAgainstAABB3D", "+0x38..+0x54", "runtime line-query behavior", "rebuild parity remain unproven"],
        ["Geometry__ClipSegmentAgainstAABB3D", "CMapWho__SetupLineLevel", "CMapWho__AdvanceLineIterator"],
        ["line-query", "signature-corrected", "comment-hardened"],
        ["OID__TraceLineAndSelectBestTargetHit"],
    ),
    "0x004922f0": target(
        "CMapWho__SetupLineLevel",
        "int __fastcall CMapWho__SetupLineLevel(void * this)",
        ["RET with no stack cleanup", "decrements the active line level", "+0x24", "+0x68/+0x6c/+0x70/+0x74", "CMapWho__WorldToSector", "runtime line-query behavior", "rebuild parity remain unproven"],
        ["CMapWho__WorldToSector", "+ 0x24", "+ 0x68"],
        ["line-query", "line-iterator", "signature-corrected", "comment-hardened"],
        ["CMapWho__GetFirstEntryWithinLine", "CMapWho__GetNextEntryWithinLine"],
    ),
    "0x004924b0": target(
        "CMapWho__AdvanceLineIterator",
        "int __fastcall CMapWho__AdvanceLineIterator(void * this)",
        ["RET with no stack cleanup", "advances the line iterator", "+0x34", "+0x58", "+0x5c/+0x5e/+0x60", "CMapWho__WorldToSector", "runtime line-query behavior", "rebuild parity remain unproven"],
        ["CMapWho__WorldToSector", "return 0", "return 1"],
        ["line-query", "line-iterator", "signature-corrected", "comment-hardened"],
        ["CMapWho__GetFirstEntryWithinLine", "CMapWho__GetNextEntryWithinLine"],
    ),
    "0x004925a0": target(
        "CMapWho__GetNextEntryWithinLine",
        "void * __fastcall CMapWho__GetNextEntryWithinLine(void * this)",
        ["RET with no stack cleanup", "active flag", "GetNextEntryWithinLine", "CMapWho__AdvanceLineIterator", "CMapWho__SetupLineLevel", "runtime line-query behavior", "rebuild parity remain unproven"],
        ["GetNextEntryWithinLine", "CMapWho__AdvanceLineIterator", "CMapWho__SetupLineLevel"],
        ["line-query", "line-iterator", "signature-corrected", "comment-hardened"],
        ["OID__TraceLineAndSelectBestTargetHit"],
    ),
    "0x00492670": target(
        "CMapWho__WorldToSector",
        "void * __thiscall CMapWho__WorldToSector(void * this, void * sector_coord, void * position, int level)",
        ["RET 0xc", "sector_coord", "position", "level", "+0x94", "+0xa8", "+0xbc", "returns the output sector pointer through EAX", "runtime sector mapping", "rebuild parity remain unproven"],
        ["ROUND", "sector_coord", "position", "level"],
        ["sector-conversion", "signature-corrected", "comment-hardened"],
        ["CMapWhoEntry__SetPosition", "CMapWhoEntry__UpdatePosition", "CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions"],
    ),
    "0x004926e0": target(
        "CMapWho__Sort",
        "void __fastcall CMapWho__Sort(void * this)",
        ["RET with no stack cleanup", "validates sector coordinates", "invalid-sector warning", "CMapWhoEntry__GetOwner", "0x2000000", "runtime sort behavior", "rebuild parity remain unproven"],
        ["invalid_sector_in_m", "CMapWhoEntry__GetOwner", "0x2000000"],
        ["sector-sort", "signature-corrected", "comment-hardened"],
        ["CGame__PostLoadProcess"],
    ),
    "0x00492860": target(
        "CMapWho__DebugDrawSector",
        "void __thiscall CMapWho__DebugDrawSector(void * this, int packed_sector_coord, int level)",
        ["RET 0x8", "packed_sector_coord", "level", "debug color", "CThing__RenderDebugVolumeOverlay", "runtime debug rendering", "rebuild parity remain unproven"],
        ["CThing__RenderDebugVolumeOverlay", "0xff00ff20", "level"],
        ["debug-draw", "signature-corrected", "comment-hardened"],
        ["CMapWho__DebugDraw"],
    ),
    "0x00492950": target(
        "CMapWho__DebugDraw",
        "void __fastcall CMapWho__DebugDraw(void * this)",
        ["RET with no stack cleanup", "render state/world matrix", "CMapWhoEntry__GetOwner", "CMapWho__DebugDrawSector", "runtime debug rendering", "rebuild parity remain unproven"],
        ["RenderState__Set0x89_Zero", "CMapWhoEntry__GetOwner", "CMapWho__DebugDrawSector"],
        ["debug-draw", "signature-corrected", "comment-hardened"],
        ["CDXEngine__Render"],
    ),
    "0x00492ba0": target(
        "CMapWhoEntry__SetPosition",
        "void __thiscall CMapWhoEntry__SetPosition(void * this, void * position, void * owner, float explicit_radius)",
        ["RET 0xc", "entry", "position", "owner", "explicit_radius", "CMapWho__GetLevelForRadius", "CMapWho__WorldToSector", "adds the entry to the global mapwho singleton", "runtime entry tracking", "rebuild parity remain unproven"],
        ["CMapWho__GetLevelForRadius", "CMapWho__WorldToSector", "CMapWho__AddEntry"],
        ["entry-position", "signature-corrected", "comment-hardened"],
        ["CThing__VFunc_09_004f34a0"],
    ),
    "0x00492c60": target(
        "CMapWhoEntry__Invalidate",
        "void __fastcall CMapWhoEntry__Invalidate(void * entry)",
        ["RET with no stack cleanup", "entry", "+0x0c", "writes -1", "runtime entry tracking", "rebuild parity remain unproven"],
        ["entry", "-1"],
        ["entry-position", "signature-corrected", "comment-hardened"],
        ["CThing__ctor_like_004f33e0", "CThing__ctor_like_004f3e10"],
    ),
    "0x00492c70": target(
        "CMapWhoEntry__RemoveFromMap",
        "void __fastcall CMapWhoEntry__RemoveFromMap(void * entry)",
        ["RET with no stack cleanup", "entry", "level is not -1", "CMapWho__RemoveEntry", "DAT_00704200", "runtime entry tracking", "rebuild parity remain unproven"],
        ["CMapWho__RemoveEntry", "DAT_00704200"],
        ["entry-position", "signature-corrected", "comment-hardened"],
        ["CComplexThing__dtor_base", "CThing__ctor_like_004f3640"],
    ),
    "0x00492c90": target(
        "CMapWhoEntry__GetOwner",
        "void * __fastcall CMapWhoEntry__GetOwner(void * entry)",
        ["RET with no stack cleanup", "entry", "returns entry - 0x0c", "owning object pointer", "runtime owner identity", "rebuild parity remain unproven"],
        ["entry + -0xc", "return"],
        ["entry-owner", "signature-corrected", "comment-hardened"],
        ["CMapWho__Sort", "CMapWho__DebugDraw", "CBattleEngine__HandleAutoAim", "CHLCollisionDetector__ScanNeighborSectorsAndDispatchCollisions"],
    ),
    "0x00492ca0": target(
        "CMapWhoEntry__UpdatePosition",
        "int __thiscall CMapWhoEntry__UpdatePosition(void * this, void * position)",
        ["RET 0x4", "entry", "position", "CMapWho__WorldToSector", "removes the entry from its old map sector", "CMapWho__AddEntry", "returns 0 when unchanged", "runtime entry tracking", "rebuild parity remain unproven"],
        ["CMapWho__WorldToSector", "CMapWho__RemoveEntry", "CMapWho__AddEntry"],
        ["entry-position", "signature-corrected", "comment-hardened"],
        ["CActor__Move", "CAtmospheric__Process", "CDXEngine__UpdateWrappedThingPositionsAndDistance"],
    ),
}

EXPECTED_DRY = {"updated": 0, "skipped": 13, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}
EXPECTED_APPLY = {"updated": 13, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}

INSTRUCTION_RETURNS = {
    "0x00492110": ("RET", "0x20"),
    "0x004922f0": ("RET", ""),
    "0x004924b0": ("RET", ""),
    "0x004925a0": ("RET", ""),
    "0x00492670": ("RET", "0xc"),
    "0x004926e0": ("RET", ""),
    "0x00492860": ("RET", "0x8"),
    "0x00492950": ("RET", ""),
    "0x00492ba0": ("RET", "0xc"),
    "0x00492c60": ("RET", ""),
    "0x00492c70": ("RET", ""),
    "0x00492c90": ("RET", ""),
    "0x00492ca0": ("RET", "0x4"),
}

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime line-query behavior proven",
    "runtime entry tracking proven",
    "runtime debug rendering proven",
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
        "schema": "ghidra-mapwho-line-wave429.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base": str(base.relative_to(ROOT)) if base.is_relative_to(ROOT) else str(base),
        "status": "PASS" if not failures else "FAIL",
        "target_count": len(TARGETS),
        "classification": "mapwho-line-query-entry-position-signature-correction" if not failures else "mapwho-line-entry-correction-incomplete",
        "not_proven": [
            "runtime line-query behavior",
            "runtime entry tracking behavior",
            "runtime debug rendering behavior",
            "concrete CMapWho or CMapWhoEntry layout beyond observed offsets",
            "source-complete identity because mapwho.cpp is absent from the current Stuart snapshot",
            "rebuild parity",
        ],
        "failures": failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--out", type=Path, default=BASE / "mapwho-line-wave429.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    failures = check_targets(args.base)
    result = build_result(args.base, failures)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if failures:
        print("FAIL ghidra_mapwho_line_wave429_probe")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PASS ghidra_mapwho_line_wave429_probe")
    if args.check:
        return 0
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
