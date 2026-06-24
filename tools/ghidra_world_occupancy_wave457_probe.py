#!/usr/bin/env python3
"""Validate Wave457 world occupancy/pathfinding static metadata corrections."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave457-world-occupancy-current"
COMMON_TAGS = {"static-reaudit", "world-occupancy-wave457", "retail-binary-evidence"}

EXPECTED_DRY = {
    "updated": 0,
    "skipped": 13,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_APPLY = {
    "updated": 13,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_VERIFY_DRY = EXPECTED_DRY


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
    "0x004bc260": target(
        "CWorld__InitOccupancyBitplanes",
        "void * __thiscall CWorld__InitOccupancyBitplanes(void * this, float max_slope_degrees)",
        [
            "RET 0x4",
            "max_slope_degrees",
            "DAT_00809dc0",
            "0xffffffff",
            "CWorld__InitLODLists",
            "runtime occupancy behavior remains unproven",
        ],
        ["world", "occupancy", "bitplane", "signature-corrected", "comment-hardened"],
        ["DAT_00809598", "DAT_00809dc0", "0xffffffff", "DAT_00829dc4"],
    ),
    "0x004bc3e0": target(
        "CWorld__RemoveUnitFromOccupancyGrid",
        "void __cdecl CWorld__RemoveUnitFromOccupancyGrid(void * unit)",
        [
            "CSPtrSet__Remove",
            "DAT_00809588",
            "unit vfunc +0x40",
            "skip_shadow_rebuild=1",
            "runtime occupancy behavior remains unproven",
        ],
        ["world", "occupancy", "unit-set", "signature-corrected", "comment-hardened"],
        ["CSPtrSet__Remove", "CWorld__RasterizeFootprintIntoOccupancyBitplanes", "+ 0x40"],
    ),
    "0x004bc480": target(
        "CWorld__AddUnitToOccupancyGridAndRebuildShadows",
        "void __cdecl CWorld__AddUnitToOccupancyGridAndRebuildShadows(void * unit)",
        [
            "CSPtrSet__AddToHead",
            "DAT_00809588",
            "skip_shadow_rebuild=1",
            "CEngine__BuildStaticShadowVolumesAroundUnit",
            "runtime static-shadow behavior remains unproven",
        ],
        ["world", "occupancy", "static-shadow", "unit-set", "signature-corrected", "comment-hardened"],
        ["CSPtrSet__AddToHead", "CWorld__RasterizeFootprintIntoOccupancyBitplanes", "CEngine__BuildStaticShadowVolumesAroundUnit"],
    ),
    "0x004bc510": target(
        "CExplosionInitThing__IsGridSegmentBlocked",
        "int __thiscall CExplosionInitThing__IsGridSegmentBlocked(void * this, int start_grid_x, uint start_grid_y, int end_grid_x, uint end_grid_y)",
        [
            "RET 0x10",
            "bitplane_base",
            "start_grid_x",
            "end_grid_y",
            "phantom float",
            "runtime pathfinding behavior remains unproven",
        ],
        ["explosion-init", "pathfinding", "occupancy", "signature-corrected", "comment-hardened"],
        ["0xff", "return 1", "return 0", "ROUND"],
    ),
    "0x004bc6d0": target(
        "CExplosionInitThing__FindNearestSetBitInOccupancyGrid",
        "int __thiscall CExplosionInitThing__FindNearestSetBitInOccupancyGrid(void * this, int * inout_grid_x, int * inout_grid_y)",
        [
            "RET 0x8",
            "inout_grid_x",
            "inout_grid_y",
            "expanding square/ring around",
            "runtime pathfinding behavior remains unproven",
        ],
        ["explosion-init", "pathfinding", "occupancy", "signature-corrected", "comment-hardened"],
        ["inout_grid_x", "inout_grid_y", "0xff", "return 1", "return 0"],
    ),
    "0x004bd440": target(
        "CWorld__ClearCrossNeighborsInBitplane",
        "void __thiscall CWorld__ClearCrossNeighborsInBitplane(void * this, int world_x, int world_y)",
        [
            "RET 0x8",
            "half-resolution",
            "cross-neighbor",
            "world_x",
            "world_y",
            "runtime occupancy behavior remains unproven",
        ],
        ["world", "occupancy", "bitplane", "signature-corrected", "comment-hardened"],
        ["world_x", "world_y", "0x100", "& -('\\x01'"],
    ),
    "0x004bd5c0": target(
        "CWorld__RasterizeFootprintIntoOccupancyBitplanes",
        "void __cdecl CWorld__RasterizeFootprintIntoOccupancyBitplanes(int min_world_x, int min_world_y, int max_world_x, int max_world_y, int skip_shadow_rebuild)",
        [
            "0..511",
            "DAT_00855290",
            "DAT_00855294",
            "DAT_00855298",
            "skip_shadow_rebuild",
            "runtime occupancy behavior remains unproven",
        ],
        ["world", "occupancy", "heightfield", "static-shadow", "signature-corrected", "comment-hardened"],
        [
            "CHeightField__GetHeightSamplePacked16",
            "CMonitor__SampleHeightfieldNormalAtXY",
            "CWorld__SetOrClearOccupancyBit",
            "CWorld__ClearCrossNeighborsInBitplane",
            "CEngine__BuildStaticShadowVolumesAroundUnit",
        ],
    ),
    "0x004bd9e0": target(
        "CEngine__BuildStaticShadowVolumesAroundUnit",
        "void __cdecl CEngine__BuildStaticShadowVolumesAroundUnit(void * unit)",
        [
            "CUnitAI__GetWorldPositionForTargeting",
            "CStaticShadows__SampleShadowHeightBilinear",
            "CWorld__SetOrClearOccupancyBit",
            "CWorld__ClearCrossNeighborsInBitplane",
            "runtime static-shadow behavior remains unproven",
        ],
        ["engine", "world", "static-shadow", "occupancy", "signature-corrected", "comment-hardened"],
        [
            "CUnitAI__GetWorldPositionForTargeting",
            "CStaticShadows__SampleShadowHeightBilinear",
            "CWorld__SetOrClearOccupancyBit",
            "CWorld__ClearCrossNeighborsInBitplane",
        ],
    ),
    "0x004bdf70": target(
        "CWorld__SetOrClearOccupancyBit",
        "void __thiscall CWorld__SetOrClearOccupancyBit(void * this, int world_x, int world_y, int set_flag)",
        [
            "RET 0xc",
            "set_flag",
            "half-resolution packed bit",
            "world_x",
            "world_y",
            "runtime occupancy behavior remains unproven",
        ],
        ["world", "occupancy", "bitplane", "signature-corrected", "comment-hardened"],
        ["set_flag != 0", "| '\\x01'", "& -('\\x01'", "world_x >> 4"],
    ),
    "0x004be050": target(
        "CWorld__LoadOccupancyBitplaneChunk",
        "void __thiscall CWorld__LoadOccupancyBitplaneChunk(void * this, void * mem_buffer)",
        [
            "RET 0x4",
            "CDXMemBuffer__Read",
            "version 1",
            "version 2",
            "packed direct rows",
            "runtime load behavior remains unproven",
        ],
        ["world", "occupancy", "bitplane", "load", "signature-corrected", "comment-hardened"],
        ["CDXMemBuffer__Read", "local_8 == 1", "local_8 == 2", "0x200", "0x100"],
    ),
    "0x004be970": target(
        "CExplosionInitThing__TestBitAtGridCoordPacked",
        "uint __thiscall CExplosionInitThing__TestBitAtGridCoordPacked(void * this, int grid_x, uint grid_y)",
        [
            "RET 0x8",
            "packed bit mask",
            "grid_x",
            "grid_y",
            "runtime pathfinding behavior remains unproven",
        ],
        ["explosion-init", "pathfinding", "occupancy", "bitplane", "signature-corrected", "comment-hardened"],
        ["grid_x", "grid_y", "1 <<", ">> 3"],
    ),
    "0x004bed30": target(
        "CExplosionInitThing__StepToLowestCostNeighbor8",
        "void __cdecl CExplosionInitThing__StepToLowestCostNeighbor8(int * inout_grid_x, int * inout_grid_y)",
        [
            "DAT_00809dc0",
            "eight neighbors",
            "inout_grid_x",
            "inout_grid_y",
            "runtime pathfinding behavior remains unproven",
        ],
        ["explosion-init", "pathfinding", "occupancy", "signature-corrected", "comment-hardened"],
        ["DAT_00809dc0", "inout_grid_x", "inout_grid_y", "0xff"],
    ),
    "0x004beea0": target(
        "CExplosionInitThing__SimplifyGridPathByLineOfSight",
        "void __thiscall CExplosionInitThing__SimplifyGridPathByLineOfSight(void * this, void * bitplane_base)",
        [
            "RET 0x4",
            "path+0x0c",
            "path+0x10/+0x18",
            "CExplosionInitThing__IsGridSegmentBlocked",
            "phantom third parameter",
            "runtime pathfinding behavior remains unproven",
        ],
        ["explosion-init", "pathfinding", "occupancy", "signature-corrected", "comment-hardened"],
        ["CExplosionInitThing__IsGridSegmentBlocked", "+ 0xc", "+ 0x10", "+ 0x18"],
    ),
}

EXPECTED_XREF_EDGES = [
    ("0x004bc260", "0x0050d5cb", "CWorld__InitLODLists"),
    ("0x004bc260", "0x0050d614", "CWorld__InitLODLists"),
    ("0x004bc260", "0x0050d65d", "CWorld__InitLODLists"),
    ("0x004bc3e0", "0x0050b025", "CWorld__RemoveUnitFromOccupancyGrid_Thunk"),
    ("0x004bc480", "0x0050b015", "CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk"),
    ("0x004bc510", "0x004be254", "CExplosionInitThing__BuildGridPathWithFallbackSearch"),
    ("0x004bc510", "0x004beed5", "CExplosionInitThing__SimplifyGridPathByLineOfSight"),
    ("0x004bc6d0", "0x004be2e6", "CExplosionInitThing__BuildGridPathWithFallbackSearch"),
    ("0x004bd440", "0x004bd93a", "CWorld__RasterizeFootprintIntoOccupancyBitplanes"),
    ("0x004bd5c0", "0x004bc46b", "CWorld__RemoveUnitFromOccupancyGrid"),
    ("0x004bd5c0", "0x004bc4f3", "CWorld__AddUnitToOccupancyGridAndRebuildShadows"),
    ("0x004bd9e0", "0x004bd9a6", "CWorld__RasterizeFootprintIntoOccupancyBitplanes"),
    ("0x004bdf70", "0x004bd7b7", "CWorld__RasterizeFootprintIntoOccupancyBitplanes"),
    ("0x004bdf70", "0x004bde08", "CEngine__BuildStaticShadowVolumesAroundUnit"),
    ("0x004be050", "0x0050d363", "CWorld__LoadWorld"),
    ("0x004be970", "0x004be4e3", "CExplosionInitThing__SelectNextPathStepDirection"),
    ("0x004bed30", "0x004be3d3", "CExplosionInitThing__BuildGridPathWithFallbackSearch"),
    ("0x004beea0", "0x004be40a", "CExplosionInitThing__BuildGridPathWithFallbackSearch"),
]

INSTRUCTION_TOKENS = {
    "0x004bc260": [
        "0x004bc260\tCWorld__InitOccupancyBitplanes\tMOV\tdword ptr [0x00809598], EDX",
        "0x004bc260\tCWorld__InitOccupancyBitplanes\tMOV\tdword ptr [0x00829dc4], 0xff",
        "0x004bc260\tCWorld__InitOccupancyBitplanes\tRET\t0x4",
    ],
    "0x004bc3e0": [
        "0x004bc3e0\tCWorld__RemoveUnitFromOccupancyGrid\tCALL\t0x004e5bd0",
        "0x004bc3e0\tCWorld__RemoveUnitFromOccupancyGrid\tCALL\t0x004bd5c0",
    ],
    "0x004bc480": [
        "0x004bc480\tCWorld__AddUnitToOccupancyGridAndRebuildShadows\tCALL\t0x004e5a80",
        "0x004bc480\tCWorld__AddUnitToOccupancyGridAndRebuildShadows\tCALL\t0x004bd5c0",
        "0x004bc480\tCWorld__AddUnitToOccupancyGridAndRebuildShadows\tCALL\t0x004bd9e0",
    ],
    "0x004bc510": [
        "0x004bc510\tCExplosionInitThing__IsGridSegmentBlocked\tRET\t0x10",
    ],
    "0x004bc6d0": [
        "0x004bc6d0\tCExplosionInitThing__FindNearestSetBitInOccupancyGrid\tRET\t0x8",
    ],
    "0x004bd440": [
        "0x004bd440\tCWorld__ClearCrossNeighborsInBitplane\tRET\t0x8",
    ],
    "0x004bd5c0": [
        "0x004bd5c0\tCWorld__RasterizeFootprintIntoOccupancyBitplanes\tCALL\t0x004bdf70",
        "0x004bd5c0\tCWorld__RasterizeFootprintIntoOccupancyBitplanes\tCALL\t0x004bd440",
        "0x004bd5c0\tCWorld__RasterizeFootprintIntoOccupancyBitplanes\tCALL\t0x004bd9e0",
    ],
    "0x004bd9e0": [
        "0x004bd9e0\tCEngine__BuildStaticShadowVolumesAroundUnit\tCALL\t0x004bdf70",
        "0x004bd9e0\tCEngine__BuildStaticShadowVolumesAroundUnit\tCALL\t0x004bd440",
    ],
    "0x004bdf70": [
        "0x004bdf70\tCWorld__SetOrClearOccupancyBit\tRET\t0xc",
    ],
    "0x004be050": [
        "0x004be050\tCWorld__LoadOccupancyBitplaneChunk\tCALL\t0x00548570",
        "0x004be050\tCWorld__LoadOccupancyBitplaneChunk\tRET\t0x4",
    ],
    "0x004be970": [
        "0x004be970\tCExplosionInitThing__TestBitAtGridCoordPacked\tRET\t0x8",
    ],
    "0x004bed30": [
        "0x004bed30\tCExplosionInitThing__StepToLowestCostNeighbor8\tRET\t",
    ],
    "0x004beea0": [
        "0x004beea0\tCExplosionInitThing__SimplifyGridPathByLineOfSight\tCALL\t0x004bc510",
        "0x004beea0\tCExplosionInitThing__SimplifyGridPathByLineOfSight\tRET\t0x4",
    ],
}

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime occupancy behavior proven",
    "runtime pathfinding behavior proven",
    "runtime static-shadow behavior proven",
    "source identity proven",
    "exact layout proven",
    "exact class proven",
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


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def unescape(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


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


def decompile_text_for(base: Path, address: str) -> str:
    directory = base / "post-decomp"
    if not directory.is_dir():
        return ""
    prefix = normalize_address(address)[2:]
    matches = sorted(directory.glob(f"{prefix}_*.c"))
    return read_text(matches[0]) if matches else ""


def parse_summary(text: str) -> dict[str, int] | None:
    match = re.search(
        r"SUMMARY\s+updated=(\d+)\s+skipped=(\d+)\s+created=(\d+)\s+would_create=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        text,
    )
    if not match:
        return None
    keys = ["updated", "skipped", "created", "would_create", "renamed", "would_rename", "missing", "bad"]
    return {key: int(value) for key, value in zip(keys, match.groups(), strict=True)}


def check_log(base: Path, filename: str, expected: dict[str, int], failures: list[str]) -> None:
    text = read_text(base / filename)
    if not text:
        failures.append(f"{filename}: missing or empty")
        return
    summary = parse_summary(text)
    if summary != expected:
        failures.append(f"{filename}: summary mismatch expected {expected}, got {summary}")
    for token in ("FAIL:", "Exception", "LockException"):
        if token in text:
            failures.append(f"{filename}: unexpected failure token {token!r}")
    if "REPORT: Save succeeded" not in text:
        failures.append(f"{filename}: missing Ghidra save-success marker")


def check_metadata(base: Path, failures: list[str]) -> None:
    metadata = read_tsv(base / "post_metadata.tsv")
    tags = read_tsv(base / "post_tags.tsv")
    if len(metadata) != len(TARGETS):
        failures.append(f"post_metadata.tsv: expected {len(TARGETS)} rows, got {len(metadata)}")
    for address, spec in TARGETS.items():
        row = row_by_address(metadata, address)
        if row is None:
            failures.append(f"{address}: missing post_metadata row")
            continue
        if row.get("name") != spec["name"]:
            failures.append(f"{address}: name mismatch {row.get('name')!r}")
        if row.get("signature") != spec["signature"]:
            failures.append(f"{address}: signature mismatch {row.get('signature')!r}")
        if "param_" in row.get("signature", ""):
            failures.append(f"{address}: residual param_ token in signature")
        comment = row.get("comment", "")
        for token in spec["commentTokens"]:  # type: ignore[index]
            if not token_present(comment, str(token)):
                failures.append(f"{address}: missing comment token {token!r}")
        lowered = comment.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{address}: overclaim token {token!r} in comment")

        tag_row = row_by_address(tags, address)
        if tag_row is None:
            failures.append(f"{address}: missing post_tags row")
            continue
        actual_tags = {tag for tag in tag_row.get("tags", "").split(";") if tag}
        for tag in spec["tags"]:  # type: ignore[index]
            if str(tag) not in actual_tags:
                failures.append(f"{address}: missing tag {tag!r}")


def check_decompiles(base: Path, failures: list[str]) -> None:
    index_rows = read_tsv(base / "post-decomp" / "index.tsv")
    ok_rows = [row for row in index_rows if row.get("status") == "OK"]
    if len(ok_rows) != len(TARGETS):
        failures.append(f"post-decomp/index.tsv: expected {len(TARGETS)} OK rows, got {len(ok_rows)}")
    for address, spec in TARGETS.items():
        text = decompile_text_for(base, address)
        if not text:
            failures.append(f"{address}: missing post decompile text")
            continue
        for token in spec["decompileTokens"]:  # type: ignore[index]
            if not token_present(text, str(token)):
                failures.append(f"{address}: missing decompile token {token!r}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    if len(rows) < len(EXPECTED_XREF_EDGES):
        failures.append(f"post_xrefs.tsv: expected at least {len(EXPECTED_XREF_EDGES)} rows, got {len(rows)}")
    edges = {
        (row.get("target_addr", ""), row.get("from_addr", ""), row.get("from_function", ""))
        for row in rows
    }
    for address, from_addr, caller in EXPECTED_XREF_EDGES:
        edge = (normalize_address(address), normalize_address(from_addr), caller)
        if edge not in edges:
            failures.append(f"{address}: missing xref from {caller} at {from_addr}")


def check_instructions(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_instructions.tsv")
    text = "\n".join(
        "\t".join(
            [
                row.get("target_addr", ""),
                row.get("function_name", ""),
                row.get("mnemonic", ""),
                row.get("operands", ""),
                row.get("flow_type", ""),
            ]
        )
        for row in rows
    )
    for address, tokens in INSTRUCTION_TOKENS.items():
        for token in tokens:
            if token not in text:
                failures.append(f"{address}: missing instruction token {token!r}")


def run_checks(base: Path = BASE) -> tuple[str, list[str]]:
    failures: list[str] = []
    if not base.is_dir():
        failures.append(f"missing evidence directory: {base}")
        return "FAIL", failures
    check_log(base, "apply_dry.log", EXPECTED_DRY, failures)
    check_log(base, "apply.log", EXPECTED_APPLY, failures)
    check_log(base, "apply_verify_dry.log", EXPECTED_VERIFY_DRY, failures)
    check_metadata(base, failures)
    check_decompiles(base, failures)
    check_xrefs(base, failures)
    check_instructions(base, failures)
    return ("PASS" if not failures else "FAIL"), failures


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=str(BASE), help="Wave457 evidence directory")
    parser.add_argument("--check", action="store_true", help="Return non-zero on failure")
    args = parser.parse_args(argv)

    base = Path(args.base)
    status, failures = run_checks(base)
    print(f"Wave457 world occupancy/pathfinding probe: {status}")
    print(f"Base: {base}")
    print(f"Targets: {len(TARGETS)}")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
    return 1 if args.check and failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
