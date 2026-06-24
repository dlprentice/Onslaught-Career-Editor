#!/usr/bin/env python3
"""Validate Wave455 InfluenceMap follow-up static metadata corrections."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave455-influencemap-followup-current"
COMMON_TAGS = {"static-reaudit", "influencemap-followup-wave455", "retail-binary-evidence"}

EXPECTED_DRY = {
    "updated": 0,
    "skipped": 8,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 5,
    "missing": 0,
    "bad": 0,
}
EXPECTED_APPLY = {
    "updated": 8,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 5,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_VERIFY_DRY = {
    "updated": 0,
    "skipped": 8,
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
    "0x004ad7f0": target(
        "CInfluenceMap__SetTrackedThingAndClearCachedObject",
        "void __thiscall CInfluenceMap__SetTrackedThingAndClearCachedObject(void * this, void * tracked_thing)",
        ["BattleEngine caller", "+0x24", "+0x14", "ret 0x4", "runtime handoff behavior remains unproven"],
        ["influencemap", "battleengine-handoff", "signature-corrected", "comment-hardened"],
        ["tracked_thing", "CDXMemoryManager__Free", "+0x24", "+0x14"],
    ),
    "0x004bf9e0": target(
        "OID__InitInfluenceMapObject",
        "void * __fastcall OID__InitInfluenceMapObject(void * init_subobject)",
        ["CInitThing", "PTR_LAB_005dc1c0", "+0x3bc", "OID factory init helper", "runtime object identity remains unproven"],
        ["oid", "initthing", "influencemap", "signature-corrected", "comment-hardened"],
        ["CInitThing__ctor", "PTR_LAB_005dc1c0", "0x3bc"],
    ),
    "0x004d30d0": target(
        "CInfluenceMap__AccumulateThingFlags",
        "void __thiscall CInfluenceMap__AccumulateThingFlags(void * this, void * thing)",
        ["thing+0x34", "0x400", "0x20000", "0x40000", "runtime category semantics remain unproven"],
        ["influencemap", "flag-accumulator", "signature-corrected", "comment-hardened"],
        ["thing", "0x20000", "0x40000", "+0x18"],
    ),
    "0x004d38c0": target(
        "CUnit__TryDestroyedCleanupAndResetDeploymentGraph",
        "int __fastcall CUnit__TryDestroyedCleanupAndResetDeploymentGraph(void * this)",
        ["CUnit cleanup wrapper", "MarkDestroyedAndCleanupLinks", "ResetDeploymentGraph", "vtable data xref", "runtime unit lifecycle behavior remains unproven"],
        ["unit", "cleanup", "owner-corrected", "signature-corrected", "comment-hardened"],
        ["CUnit__MarkDestroyedAndCleanupLinks", "CUnit__ResetDeploymentGraphAndScheduleEvent", "return 1"],
    ),
    "0x004d39d0": target(
        "CPolyBucket__InitFields",
        "void __fastcall CPolyBucket__InitFields(void * this)",
        ["CMeshPart__CreatePolyBucket", "CStaticShadows", "+0x60", "+0x98", "concrete CPolyBucket layout and runtime render behavior remain unproven"],
        ["polybucket", "init", "owner-corrected", "name-corrected", "signature-corrected", "comment-hardened"],
        ["CPolyBucket__InitFields", "+0x50", "0x3f800000", "+0x98"],
    ),
    "0x004d3a00": target(
        "CPolyBucket__FreeBuffers",
        "void __fastcall CPolyBucket__FreeBuffers(void * this)",
        ["CMeshPart, CMesh, and CStaticShadows paths", "+0x60", "+0x80", "+0x98", "concrete CPolyBucket layout and runtime render behavior remain unproven"],
        ["polybucket", "cleanup", "owner-corrected", "name-corrected", "signature-corrected", "comment-hardened"],
        ["CPolyBucket__FreeBuffers", "CDXLandscape__DestroyArrayWithCallback", "LAB_004d3af0", "CDXLandscape__FreeObjectCallback"],
    ),
    "0x0050b930": target(
        "CInfluenceMapManager__scalar_deleting_dtor",
        "void * __thiscall CInfluenceMapManager__scalar_deleting_dtor(void * this, byte flags)",
        ["scalar-deleting destructor", "flags bit 0", "0x005dfcb4", "DAT_0067a748", "runtime cleanup behavior remains unproven"],
        ["influencemap-manager", "destructor", "owner-corrected", "name-corrected", "signature-corrected", "comment-hardened"],
        ["CInfluenceMapManager__dtor", "byte flags", "CDXMemoryManager__Free"],
    ),
    "0x0050b950": target(
        "CInfluenceMapManager__dtor",
        "void __fastcall CInfluenceMapManager__dtor(void * this)",
        ["destructor body for the InfluenceMap manager object", "0x005dfcb4", "CInfluenceMap__FreeObjectIfPresent", "CSPtrSet", "runtime cleanup behavior remains unproven"],
        ["influencemap-manager", "destructor", "owner-corrected", "name-corrected", "signature-corrected", "comment-hardened"],
        ["CInfluenceMap__FreeObjectIfPresent", "CSPtrSet__Clear", "CMonitor__Shutdown", "PTR_LAB_005dfcb4"],
    ),
}

EXPECTED_XREF_EDGES = [
    ("0x004ad7f0", "0x00406550", "CBattleEngine__SwapPrimarySecondaryPartReadersForState"),
    ("0x004bf9e0", "0x004bf4a3", "OID__CreateObject"),
    ("0x004d30d0", "0x0040a578", "<no_function>"),
    ("0x004d38c0", "0x005e0054", "<no_function>"),
    ("0x004d39d0", "0x004ae319", "CMeshPart__CreatePolyBucket"),
    ("0x004d39d0", "0x004ec4ba", "CStaticShadows__BuildShadowMaps"),
    ("0x004d3a00", "0x004ae811", "CMeshPart__FreeOwnedResourcePointers_004ae640"),
    ("0x004d3a00", "0x004ab143", "CMesh__Deserialize"),
    ("0x004d3a00", "0x004ae3c8", "CMeshPart__CreatePolyBucket"),
    ("0x004d3a00", "0x004ec4ec", "CStaticShadows__BuildShadowMaps"),
    ("0x004d3a00", "0x004ee0d3", "CStaticShadows__CleanupHelper"),
    ("0x0050b930", "0x005dfcb8", "<no_function>"),
    ("0x0050b950", "0x0050b933", "CInfluenceMapManager__scalar_deleting_dtor"),
]

INSTRUCTION_TOKENS = {
    "0x004ad7f0": [
        "0x004ad7f0\tCInfluenceMap__SetTrackedThingAndClearCachedObject\tCALL\t0x00549220",
        "0x004ad7f0\tCInfluenceMap__SetTrackedThingAndClearCachedObject\tRET\t0x4",
    ],
    "0x004bf9e0": [
        "0x004bf9e0\tOID__InitInfluenceMapObject\tCALL\t0x0048dcf0",
        "0x004bf9e0\tOID__InitInfluenceMapObject\tMOV\tdword ptr [ESI], 0x5dc1c0",
    ],
    "0x004d30d0": [
        "0x004d30d0\tCInfluenceMap__AccumulateThingFlags\tTEST\tdword ptr [EAX + 0x34], 0x20000",
        "0x004d30d0\tCInfluenceMap__AccumulateThingFlags\tRET\t0x4",
    ],
    "0x004d38c0": [
        "0x004d38c0\tCUnit__TryDestroyedCleanupAndResetDeploymentGraph\tCALL\t0x004fd140",
        "0x004d38c0\tCUnit__TryDestroyedCleanupAndResetDeploymentGraph\tCALL\t0x004fd040",
    ],
    "0x004d39d0": [
        "0x004d39d0\tCPolyBucket__InitFields\tMOV\tdword ptr [EAX + 0x50], 0x3f800000",
        "0x004d39d0\tCPolyBucket__InitFields\tRET\t",
    ],
    "0x004d3a00": [
        "0x004d3a00\tCPolyBucket__FreeBuffers\tPUSH\t0x4d3af0",
        "0x004d3a00\tCPolyBucket__FreeBuffers\tCALL\t0x0055db0a",
        "0x004d3a00\tCPolyBucket__FreeBuffers\tCALL\t0x00549220",
    ],
    "0x0050b930": [
        "0x0050b930\tCInfluenceMapManager__scalar_deleting_dtor\tCALL\t0x0050b950",
        "0x0050b930\tCInfluenceMapManager__scalar_deleting_dtor\tTEST\tbyte ptr [ESP + 0x8], 0x1",
        "0x0050b930\tCInfluenceMapManager__scalar_deleting_dtor\tRET\t0x4",
    ],
    "0x0050b950": [
        "0x0050b950\tCInfluenceMapManager__dtor\tMOV\tdword ptr [ESI], 0x5dfcb4",
        "0x0050b950\tCInfluenceMapManager__dtor\tCALL\t0x0048afb0",
        "0x0050b950\tCInfluenceMapManager__dtor\tCALL\t0x004e5c60",
        "0x0050b950\tCInfluenceMapManager__dtor\tCALL\t0x004bac40",
    ],
}

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime ai behavior proven",
    "runtime cleanup behavior proven",
    "source identity proven",
    "concrete layout proven",
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
    parser.add_argument("--base", default=str(BASE), help="Wave455 evidence directory")
    parser.add_argument("--check", action="store_true", help="Return non-zero on failure")
    args = parser.parse_args(argv)

    base = Path(args.base)
    status, failures = run_checks(base)
    print(f"Wave455 InfluenceMap follow-up probe: {status}")
    print(f"Base: {base}")
    print(f"Targets: {len(TARGETS)}")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
    return 1 if args.check and failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
