#!/usr/bin/env python3
"""Validate Wave458 mesh optimization / NamedMesh static metadata corrections."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave458-mesh-optimization-current"
COMMON_TAGS = {"static-reaudit", "mesh-optimization-wave458", "retail-binary-evidence"}

EXPECTED_DRY = {
    "updated": 0,
    "skipped": 5,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 1,
    "missing": 0,
    "bad": 0,
}
EXPECTED_APPLY = {
    "updated": 5,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 1,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_VERIFY_DRY = {
    "updated": 0,
    "skipped": 5,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
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
    "0x004bae70": target(
        "CMeshPart__CanOptimizePart_Strict",
        "int __cdecl CMeshPart__CanOptimizePart_Strict(void * part)",
        [
            "CMesh__OptimizeParts",
            "CMeshPart pointer",
            "wheel/body/axle",
            "buggy CORE/x1",
            "barrel-spinner",
            "Runtime optimization behavior",
        ],
        ["mesh", "mesh-part", "optimization", "signature-corrected", "comment-hardened"],
        [
            "CMeshPart__HasWheelMotionAnimation",
            "CMeshPart__PassesBuggyCoreStateForStrictOptimize",
            "CMeshPart__NameAvoidsBarrelSpinnerOptimizationTokens",
        ],
    ),
    "0x004bb040": target(
        "CMeshPart__CanMergeInOptimizePass",
        "int __cdecl CMeshPart__CanMergeInOptimizePass(void * part)",
        [
            "CMesh__OptimizeParts",
            "merge eligibility",
            "merge-specific buggy CORE/x1",
            "shared true-return helper",
            "Runtime merge behavior",
        ],
        ["mesh", "mesh-part", "optimization", "signature-corrected", "comment-hardened"],
        [
            "CMeshPart__PassesBuggyCoreStateForMergeOptimize",
            "CFrontEndPage__Init_ReturnTrue",
            "CMeshPart__AnyChildNameMatchesBarrelSpinnerOptimizationTokens",
        ],
    ),
    "0x004bb210": target(
        "CMesh__HasSpecialOptimizationConstraints",
        "bool __cdecl CMesh__HasSpecialOptimizationConstraints(void * mesh)",
        [
            "CMesh__OptimizeParts",
            "mesh pointer",
            "0x623074",
            "nmidoutcyl",
            "tentacle-bone",
            "Runtime optimization behavior",
        ],
        ["mesh", "optimization", "signature-corrected", "comment-hardened"],
        [
            "CMeshPart__HasWheelMotionAnimation",
            "CMeshPart__AnyChildNameIsNmidoutcyl",
            "CMesh__HasTentacleBone",
        ],
    ),
    "0x004bbcd0": target(
        "CNamedMesh__VFunc_09_004bbcd0",
        "void __thiscall CNamedMesh__VFunc_09_004bbcd0(void * this, void * param_1, void * param_2)",
        [
            "EAX-carried init pointer",
            "CActor__Init",
            "CMesh__FindAnimationIndexByName",
            "event 3000",
            "world occupancy/static-shadow tracking",
            "Runtime NamedMesh behavior",
        ],
        ["named-mesh", "actor-init", "occupancy", "comment-hardened"],
        [
            "CActor__Init",
            "CMesh__FindAnimationIndexByName",
            "CEventManager__AddEvent_AtTime",
            "CWorld__AddUnitToOccupancyGridAndRebuildShadows",
        ],
    ),
    "0x004bc050": target(
        "CNamedMesh__VFunc02_RemoveFromOccupancyAndForward",
        "void __fastcall CNamedMesh__VFunc02_RemoveFromOccupancyAndForward(void * this)",
        [
            "CNamedMesh vtable slot 2",
            "CWorld__RemoveUnitFromOccupancyGrid_Thunk",
            "VFuncSlot_02_004f41b0",
            "CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh",
            "Runtime NamedMesh cleanup behavior",
        ],
        ["named-mesh", "occupancy", "vtable-slot", "signature-corrected", "comment-hardened"],
        ["CWorld__RemoveUnitFromOccupancyGrid_Thunk", "VFuncSlot_02_004f41b0"],
    ),
}

EXPECTED_XREF_EDGES = {
    ("0x004bae70", "0x004ab549", "CMesh__OptimizeParts"),
    ("0x004bae70", "0x004ab750", "CMesh__OptimizeParts"),
    ("0x004bb040", "0x004ab44e", "CMesh__OptimizeParts"),
    ("0x004bb040", "0x004ab46e", "CMesh__OptimizeParts"),
    ("0x004bb040", "0x004ab565", "CMesh__OptimizeParts"),
    ("0x004bb210", "0x004ab772", "CMesh__OptimizeParts"),
    ("0x004bc050", "0x00418460", "CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh"),
}

INSTRUCTION_TOKENS = {
    "0x004bae70": [
        "0x004bae70\tCMeshPart__CanOptimizePart_Strict\tCALL\t0x00495030",
        "0x004bae70\tCMeshPart__CanOptimizePart_Strict\tCALL\t0x0049f600",
        "0x004bae70\tCMeshPart__CanOptimizePart_Strict\tRET\t",
    ],
    "0x004bb040": [
        "0x004bb040\tCMeshPart__CanMergeInOptimizePass\tCALL\t0x00495090",
        "0x004bb040\tCMeshPart__CanMergeInOptimizePass\tCALL\t0x004fdc10",
        "0x004bb040\tCMeshPart__CanMergeInOptimizePass\tRET\t",
    ],
    "0x004bb210": [
        "0x004bb210\tCMesh__HasSpecialOptimizationConstraints\tCALL\t0x00494b50",
        "0x004bb210\tCMesh__HasSpecialOptimizationConstraints\tCALL\t0x0049ed30",
        "0x004bb210\tCMesh__HasSpecialOptimizationConstraints\tRET\t",
    ],
    "0x004bbcd0": [
        "0x004bbcd0\tCNamedMesh__VFunc_09_004bbcd0\tCALL\t0x004011e0",
        "0x004bbcd0\tCNamedMesh__VFunc_09_004bbcd0\tCALL\t0x004aa630",
        "0x004bbcd0\tCNamedMesh__VFunc_09_004bbcd0\tCALL\t0x0050b010",
    ],
    "0x004bc050": [
        "0x004bc050\tCNamedMesh__VFunc02_RemoveFromOccupancyAndForward\tCALL\t0x0050b020",
        "0x004bc050\tCNamedMesh__VFunc02_RemoveFromOccupancyAndForward\tCALL\t0x004f41b0",
        "0x004bc050\tCNamedMesh__VFunc02_RemoveFromOccupancyAndForward\tRET\t",
    ],
}

VTABLE_EXPECTED = {
    ("0x005dd5f0", "2", "0x004bc050", "CNamedMesh__VFunc02_RemoveFromOccupancyAndForward"),
    ("0x005dd5f0", "9", "0x004bbcd0", "CNamedMesh__VFunc_09_004bbcd0"),
}

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime optimization behavior proven",
    "runtime namedmesh behavior proven",
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
        for key in ("address", "target_addr", "from_addr", "from_function_addr", "function_entry", "vtable", "pointer_addr"):
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
        if address != "0x004bbcd0" and "param_" in row.get("signature", ""):
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


def check_vtable(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_vtable_slots.tsv")
    if not rows:
        failures.append("post_vtable_slots.tsv: missing or empty")
        return
    observed = {
        (
            row.get("vtable", ""),
            row.get("slot_index", ""),
            row.get("pointer_addr", ""),
            row.get("function_name", ""),
        )
        for row in rows
    }
    for vtable, slot, pointer, name in VTABLE_EXPECTED:
        edge = (normalize_address(vtable), slot, normalize_address(pointer), name)
        if edge not in observed:
            failures.append(f"vtable {vtable} slot {slot}: missing {name} at {pointer}")


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
    check_vtable(base, failures)
    return ("PASS" if not failures else "FAIL"), failures


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=str(BASE), help="Wave458 evidence directory")
    parser.add_argument("--check", action="store_true", help="Return non-zero on failure")
    args = parser.parse_args(argv)

    base = Path(args.base)
    status, failures = run_checks(base)
    print(f"Wave458 mesh optimization/NamedMesh probe: {status}")
    print(f"Base: {base}")
    print(f"Targets: {len(TARGETS)}")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
    return 1 if args.check and failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
