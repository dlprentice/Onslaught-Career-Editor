#!/usr/bin/env python3
"""Validate the Wave426 map/heightfield resource saved-Ghidra correction."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave426-map-resource-queue" / "current"

COMMON_TAGS = {"static-reaudit", "map-resource-wave426", "terrain-heightfield", "retail-binary-evidence"}


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
    "0x0047e870": target(
        "CHeightField__ResetCoreBuffersAndFlags",
        "void * __fastcall CHeightField__ResetCoreBuffersAndFlags(void * this)",
        ["supersedes the older CUnitAI owner label", "clears +0x20/+0x24", "1024 dwords", "+0x1028", "returns this", "runtime terrain behavior", "rebuild parity remain unproven"],
        ["0x400", "0x1028", "this + 0x28"],
        ["heightfield", "constructor-helper", "owner-corrected", "signature-corrected", "comment-hardened"],
        ["CHeightField__Constructor"],
    ),
    "0x0047e8a0": target(
        "CHeightField__FreeOwnedBuffers_24_1028",
        "void __fastcall CHeightField__FreeOwnedBuffers_24_1028(void * this)",
        ["supersedes the older CUnitAI owner label", "+0x24", "+0x1028", "OID__FreeObject", "runtime terrain behavior", "rebuild parity remain unproven"],
        ["0x24", "0x1028", "OID__FreeObject"],
        ["heightfield", "owned-buffer-free", "owner-corrected", "signature-corrected", "comment-hardened"],
        ["CHeightField__FreeOwnedBuffers_Thunk", "CHeightField__ShutdownAndDestroyMixerMap"],
    ),
    "0x0047ea20": target(
        "CHeightField__GetHeightSamplePacked16",
        "uint __fastcall CHeightField__GetHeightSamplePacked16(void * this, uint x_packed, uint z_packed)",
        ["supersedes the older provisional CWorld owner label", "+0x1028", "packed X/Z", "0x200", "runtime terrain behavior", "rebuild parity remain unproven"],
        ["0x1028", "0x3ffe00", "0xa1ffe"],
        ["heightfield", "packed-height-sample", "owner-corrected", "signature-corrected", "comment-hardened"],
        ["CHeightField__BuildCellMinMaxHeightTable"],
    ),
    "0x00490900": target(
        "Vec3__SubtractInPlace",
        "void __thiscall Vec3__SubtractInPlace(void * this, void * rhs_vector)",
        ["RET 0x4", "subtracts rhs_vector", "three float components", "runtime vector behavior", "rebuild parity remain unproven"],
        ["rhs_vector", "this", "-"],
        ["vector-math", "signature-corrected", "comment-hardened"],
        ["004c512d", "004e53c4"],
    ),
    "0x00490a40": target(
        "CHeightField__TraceLineAgainstHeightfield",
        "int __thiscall CHeightField__TraceLineAgainstHeightfield(void * this, void * line, void * hit_out, int stop_at_height_limit)",
        ["corrects the older CStaticShadows owner label", "RET 0xc", "+0x13dc/+0x13e0", "CHeightField__SampleInterpolatedHeight", "runtime terrain behavior", "rebuild parity remain unproven"],
        ["stop_at_height_limit", "CHeightField__SampleInterpolatedHeight", "0x13dc", "0x13e0"],
        ["heightfield", "line-trace", "owner-corrected", "signature-corrected", "comment-hardened"],
        ["OID__TraceLineAndSelectBestTargetHit", "CStaticShadows__BuildShadowMaps"],
    ),
    "0x00490e10": target(
        "CHeightField__Constructor",
        "void * __fastcall CHeightField__Constructor(void * this)",
        ["global MAP constructor wrapper", "CHeightField__ResetCoreBuffersAndFlags", "returns this", "runtime terrain behavior", "rebuild parity remain unproven"],
        ["CHeightField__ResetCoreBuffersAndFlags", "return this"],
        ["heightfield", "constructor", "owner-corrected", "signature-corrected", "comment-hardened"],
        ["00490a15"],
    ),
    "0x00490e20": target(
        "CHeightField__FreeOwnedBuffers_Thunk",
        "void __fastcall CHeightField__FreeOwnedBuffers_Thunk(void * this)",
        ["global MAP destructor thunk", "tail-calls CHeightField__FreeOwnedBuffers_24_1028", "runtime terrain behavior", "rebuild parity remain unproven"],
        ["CHeightField__FreeOwnedBuffers_24_1028"],
        ["heightfield", "destructor-thunk", "owner-corrected", "signature-corrected", "comment-hardened"],
        ["00490a35"],
    ),
    "0x00490e30": target(
        "CHeightField__BuildCellMinMaxHeightTable",
        "void __fastcall CHeightField__BuildCellMinMaxHeightTable(void * this)",
        ["corrects the older CGame owner label", "9x9", "+0x13dc", "+0x102c", "CHeightField__GetHeightSamplePacked16", "runtime terrain behavior", "rebuild parity remain unproven"],
        ["CHeightField__GetHeightSamplePacked16", "0x13dc", "0x102c"],
        ["heightfield", "minmax-table", "owner-corrected", "signature-corrected", "comment-hardened"],
        ["CGame__PostLoadProcess"],
    ),
    "0x00490f10": target(
        "CHeightField__InitAndClearMapLoadFlags",
        "int __fastcall CHeightField__InitAndClearMapLoadFlags(void * this)",
        ["source CGame::Init MAP.Init context", "+0x93e0/+0x93e4", "returns TRUE/FALSE", "runtime terrain behavior", "rebuild parity remain unproven"],
        ["0x93e0", "0x93e4", "return 1"],
        ["heightfield", "map-init", "owner-corrected", "signature-corrected", "comment-hardened"],
        ["CGame__Init"],
    ),
    "0x00490f40": target(
        "CHeightField__ShutdownAndDestroyMixerMap",
        "void __fastcall CHeightField__ShutdownAndDestroyMixerMap(void * this)",
        ["corrects the older CUnitAI owner label", "CHeightField__FreeOwnedBuffers_24_1028", "CMixerMap__Destroy", "MAP.Shutdown context", "runtime terrain behavior", "rebuild parity remain unproven"],
        ["CHeightField__FreeOwnedBuffers_24_1028", "CMixerMap__Destroy"],
        ["heightfield", "map-shutdown", "mixer-map", "owner-corrected", "signature-corrected", "comment-hardened"],
        ["0046ca0e"],
    ),
    "0x00490f50": target(
        "CHeightField__TraceMapLoadRequestAndCheckLoadedFlags",
        "int __thiscall CHeightField__TraceMapLoadRequestAndCheckLoadedFlags(void * this, int map_number, int load_geometry, int load_properties)",
        ["corrects the older CWorld owner label", "RET 0xc", "Loading map %d", "+0x93e0/+0x93e4", "runtime terrain behavior", "rebuild parity remain unproven"],
        ["map_number", "load_geometry", "load_properties", "0x93e0", "0x93e4"],
        ["heightfield", "map-load-flags", "owner-corrected", "signature-corrected", "comment-hardened"],
        ["CWorld__LoadWorld"],
    ),
    "0x00491060": target(
        "CHeightField__DeserializeMapAndInitResources",
        "void __thiscall CHeightField__DeserializeMapAndInitResources(void * this, void * chunk_reader)",
        ["corrects the older CResourceAccumulator owner label", "MAP.Deserialize context", "CHeightField__Load", "CMixerMap__Init", "CEngine__LoadMixers", "runtime terrain behavior", "rebuild parity remain unproven"],
        ["chunk_reader", "CHeightField__Load", "CMixerMap__Init", "CEngine__LoadMixers"],
        ["heightfield", "map-deserialize", "resource-init", "owner-corrected", "signature-corrected", "comment-hardened"],
        ["CEngine__Deserialize"],
    ),
}

EXPECTED_DRY = {"updated": 0, "skipped": 12, "renamed": 0, "would_rename": 1, "missing": 0, "bad": 0}
EXPECTED_APPLY = {"updated": 12, "skipped": 0, "renamed": 1, "would_rename": 0, "missing": 0, "bad": 0}

INSTRUCTION_RETURNS = {
    "0x0047e870": ("RET", ""),
    "0x0047e8a0": ("RET", ""),
    "0x0047ea20": ("RET", ""),
    "0x00490900": ("RET", "0x4"),
    "0x00490a40": ("RET", "0xc"),
    "0x00490e10": ("RET", ""),
    "0x00490e20": ("JMP", "0x0047e8a0"),
    "0x00490e30": ("RET", ""),
    "0x00490f10": ("RET", ""),
    "0x00490f40": ("JMP", "0x00523230"),
    "0x00490f50": ("RET", "0xc"),
    "0x00491060": ("RET", "0x4"),
}

STALE_OWNER_TOKENS = (
    "CUnitAI__ResetWorkGrid1024AndFlags",
    "CUnitAI__FreeOwnedObjects_24_1028",
    "CWorld__GetHeightSamplePacked16",
    "CStaticShadows__TraceSegmentAgainstHeightfield",
    "CUnitAI__InitWorkGrid1024",
    "CGame__BuildCellMinMaxHeightTable",
    "CGame__InitMapLoadStateFlags",
    "CUnitAI__ReleaseOwnedObjectsAndDestroyMixerMap",
    "CWorld__CanLoadMapSection",
    "CResourceAccumulator__DeserializeMapAndInitResources",
)

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime terrain behavior proven",
    "runtime map loading proven",
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

        name_sig = f"{row.get('name', '')} {row.get('signature', '')}"
        for stale in STALE_OWNER_TOKENS:
            if token_present(name_sig, stale):
                failures.append(f"{address}: stale owner token {stale}")

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
            for stale in STALE_OWNER_TOKENS:
                if stale != row.get("name") and token_present(decompile, stale):
                    failures.append(f"{address}: stale decompile owner token {stale}")

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
        "schema": "ghidra-map-resource-wave426.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base": str(base.relative_to(ROOT)) if base.is_relative_to(ROOT) else str(base),
        "status": "PASS" if not failures else "FAIL",
        "target_count": len(TARGETS),
        "classification": "map-heightfield-owner-and-signature-correction" if not failures else "map-heightfield-correction-incomplete",
        "not_proven": [
            "runtime terrain behavior",
            "runtime map load behavior",
            "concrete CHeightField/CMap layout",
            "source-complete identity because HeightField.cpp/world.cpp are absent from the current Stuart snapshot",
            "rebuild parity",
        ],
        "failures": failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--out", type=Path, default=BASE / "map-resource-wave426.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    failures = check_targets(args.base)
    result = build_result(args.base, failures)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if failures:
        print("FAIL ghidra_map_resource_wave426_probe")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PASS ghidra_map_resource_wave426_probe")
    if args.check:
        return 0
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
