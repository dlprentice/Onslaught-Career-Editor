#!/usr/bin/env python3
"""Validate the Wave387 geometry/collision Ghidra correction tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "geometry-collision-wave387" / "current"

COMMON_TAGS = {"static-reaudit", "geometry-collision-wave387", "retail-binary-evidence"}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    decompile_tokens: list[str],
    tags: list[str],
    caller: str,
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "decompileTokens": decompile_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "caller": caller,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x00479020": target(
        "CMeshCollisionVolume__IsDirectionInsideTrianglePrism",
        "int __cdecl CMeshCollisionVolume__IsDirectionInsideTrianglePrism(void * vertex0, void * vertex1, void * vertex2, void * vertex3, void * direction)",
        [
            "Wave387 geometry/collision correction",
            "three signed edge/plane dot tests",
            "called from CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore",
            "Concrete vector layout, exact source identity, runtime collision behavior, and rebuild parity remain unproven",
        ],
        ["Vec3__Cross", "Vec3__Dot", "return 1;"],
        ["mesh-collision", "triangle-prism", "comment-hardened", "signature-hardened"],
        "CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore",
    ),
    "0x00479200": target(
        "Geometry__SelectClosestPointOnTriangleEdges",
        "void __cdecl Geometry__SelectClosestPointOnTriangleEdges(void * outClosest, void * vertexA, void * vertexB, void * vertexC, void * queryPoint)",
        [
            "Wave387 geometry/collision correction",
            "clamped projections across all three triangle edges",
            "selects the nearest candidate point to queryPoint",
            "Concrete vector layout, exact source identity, runtime collision behavior, and rebuild parity remain unproven",
        ],
        ["Geometry__NoOpHook", "Vec3__NormalizeInPlace", "Vec3__ScaleToOut", "Vec3__Add"],
        ["geometry", "closest-point", "comment-hardened", "signature-hardened"],
        "CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore",
    ),
    "0x00479630": target(
        "Geometry__RaySphereEntryDistance",
        "double __cdecl Geometry__RaySphereEntryDistance(void * rayStart, void * rayEnd, float radius)",
        [
            "Wave387 geometry/collision correction",
            "normalizes rayEnd minus rayStart",
            "solves origin-centered sphere entry distance",
            "returns the retail sentinel when no positive entry is observed",
            "Concrete vector layout, exact source identity, runtime collision behavior, and rebuild parity remain unproven",
        ],
        ["SQRT", "_DAT_005d8be0", "return (double)"],
        ["geometry", "ray-sphere", "comment-hardened", "signature-hardened"],
        "CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore",
    ),
    "0x00479770": target(
        "Geometry__DistanceOutsideAabb",
        "double __cdecl Geometry__DistanceOutsideAabb(void * point, void * halfExtents)",
        [
            "Wave387 geometry/collision correction",
            "absolute centered AABB overhangs",
            "single-axis and two-axis distance branches",
            "all-three-axis branch records the retail instruction sequence rather than an idealized formula",
            "Concrete vector layout, exact source identity, runtime collision behavior, and rebuild parity remain unproven",
        ],
        ["ABS", "CConsole__Printf", "s_Error__Should_not_be_here_in__Di_0062c998"],
        ["geometry", "aabb-distance", "comment-hardened", "signature-hardened"],
        "CMeshCollisionVolume__TestSweptSphereAgainstBounds",
    ),
}

INSTRUCTION_EVIDENCE = [
    ("0x00479020", "0x004790a6", "FCOMP", "double ptr [0x005d87b0]", "dc 1d b0 87 5d 00"),
    ("0x00479020", "0x004791c0", "CALL", "0x00411a60", "e8 9b 88 f9 ff"),
    ("0x00479020", "0x004791cc", "CALL", "0x0040d180", "e8 af 3f f9 ff"),
    ("0x00479200", "0x00479248", "CALL", "0x00477ba0", "e8 53 e9 ff ff"),
    ("0x00479200", "0x00479255", "CALL", "0x00406d50", "e8 f6 da f8 ff"),
    ("0x00479200", "0x004792e4", "CALL", "0x0040d150", "e8 67 3e f9 ff"),
    ("0x00479630", "0x0047965f", "FSQRT", "", "d9 fa"),
    ("0x00479630", "0x00479701", "FLD", "float ptr [0x005d8be0]", "d9 05 e0 8b 5d 00"),
    ("0x00479770", "0x004798a4", "FADD", "ST0, ST0", "dc c0"),
    ("0x00479770", "0x004798b7", "CALL", "0x00441740", "e8 84 7e fc ff"),
    ("0x00479770", "0x004798bf", "FLD", "float ptr [0x005d856c]", "d9 05 6c 85 5d 00"),
]

EXPECTED_DRY = {"updated": 0, "skipped": 4, "missing": 0, "bad": 0}
EXPECTED_APPLY = {"updated": 4, "skipped": 0, "missing": 0, "bad": 0}

DEFAULT_DRY = BASE / "geometry_collision_wave387_dry.log"
DEFAULT_APPLY = BASE / "geometry_collision_wave387_apply.log"
DEFAULT_METADATA = BASE / "metadata_after.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_after"
DEFAULT_XREFS = BASE / "xrefs_after.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_after.tsv"
DEFAULT_TAGS = BASE / "tags_after.tsv"
DEFAULT_OUT = BASE / "geometry-collision-wave387.json"

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime collision behavior proven",
    "runtime proof",
    "source identity proven",
    "fully re'ed",
    "100% re",
    "rebuild parity proven",
)


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


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
        for key in ("address", "target_addr", "instruction_addr", "function_entry", "target_raw"):
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


def rows_for_address(rows: list[dict[str, str]], address: str, key: str) -> list[dict[str, str]]:
    wanted = normalize_address(address)
    return [row for row in rows if normalize_address(row.get(key, "")) == wanted]


def decompile_text_for(directory: Path, address: str) -> str:
    if not directory.is_dir():
        return ""
    matches = sorted(directory.glob(f"{normalize_address(address)[2:]}_*.c"))
    if not matches:
        return ""
    return read_text(matches[0])


def parse_tags(value: str) -> set[str]:
    return {part.strip() for part in value.split(";") if part.strip()}


def parse_summary(log_text: str) -> dict[str, int]:
    match = re.search(r"updated=(\d+)\s+skipped=(\d+)\s+missing=(\d+)\s+bad=(\d+)", log_text)
    if not match:
        return {"updated": -1, "skipped": -1, "missing": -1, "bad": -1}
    return {
        "updated": int(match.group(1)),
        "skipped": int(match.group(2)),
        "missing": int(match.group(3)),
        "bad": int(match.group(4)),
    }


def instruction_hit(rows: list[dict[str, str]], target: str, instruction_addr: str, mnemonic: str, operands: str, bytes_: str) -> bool:
    target_norm = normalize_address(target)
    instruction_norm = normalize_address(instruction_addr)
    return any(
        (
            normalize_address(row.get("target_addr", "")) == target_norm
            or normalize_address(row.get("function_entry", "")) == target_norm
        )
        and normalize_address(row.get("instruction_addr", "")) == instruction_norm
        and row.get("mnemonic", "") == mnemonic
        and row.get("operands", "") == operands
        and row.get("bytes", "") == bytes_
        for row in rows
    )


def build_report(
    dry_log_path: Path = DEFAULT_DRY,
    apply_log_path: Path = DEFAULT_APPLY,
    metadata_path: Path = DEFAULT_METADATA,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
    tags_path: Path = DEFAULT_TAGS,
) -> dict[str, object]:
    dry_log_path = resolve(dry_log_path)
    apply_log_path = resolve(apply_log_path)
    metadata_path = resolve(metadata_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)
    tags_path = resolve(tags_path)

    dry_log = read_text(dry_log_path)
    apply_log = read_text(apply_log_path)
    metadata_rows = read_tsv(metadata_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)
    tag_rows = read_tsv(tags_path)

    failures: list[str] = []
    dry_summary = parse_summary(dry_log)
    apply_summary = parse_summary(apply_log)
    if dry_summary != EXPECTED_DRY:
        failures.append(f"dry summary mismatch: {dry_summary} != {EXPECTED_DRY}")
    if apply_summary != EXPECTED_APPLY:
        failures.append(f"apply summary mismatch: {apply_summary} != {EXPECTED_APPLY}")
    if "REPORT: Save succeeded" not in apply_log:
        failures.append("apply log missing REPORT: Save succeeded")

    commented = 0
    signature_hardened = 0
    caller_hits = 0
    for address, expected in TARGETS.items():
        metadata = row_by_address(metadata_rows, address)
        if metadata is None:
            failures.append(f"{address}: missing metadata row")
            continue
        if metadata.get("name") != expected["name"]:
            failures.append(f"{address}: name mismatch {metadata.get('name')} != {expected['name']}")
        if metadata.get("signature") != expected["signature"]:
            failures.append(f"{address}: signature mismatch {metadata.get('signature')} != {expected['signature']}")
        else:
            signature_hardened += 1
        comment = metadata.get("comment", "")
        for token in expected["commentTokens"]:
            if not token_present(comment, str(token)):
                failures.append(f"{address}: missing comment token {token!r}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                failures.append(f"{address}: comment overclaim token {token!r}")
        if comment:
            commented += 1

        decompile_text = decompile_text_for(decompile_dir, address)
        if not decompile_text:
            failures.append(f"{address}: missing decompile output")
        for token in expected["decompileTokens"]:
            if not token_present(decompile_text, str(token)):
                failures.append(f"{address}: missing decompile token {token!r}")

        tags = parse_tags((row_by_address(tag_rows, address) or {}).get("tags", ""))
        for tag in expected["tags"]:
            if tag not in tags:
                failures.append(f"{address}: missing tag {tag!r}")

        target_xrefs = rows_for_address(xref_rows, address, "target_addr")
        if not any(row.get("from_function") == expected["caller"] for row in target_xrefs):
            failures.append(f"{address}: caller mismatch; expected {expected['caller']}")
        else:
            caller_hits += 1

    instruction_hits = 0
    for target_addr, instruction_addr, mnemonic, operands, bytes_ in INSTRUCTION_EVIDENCE:
        if instruction_hit(instruction_rows, target_addr, instruction_addr, mnemonic, operands, bytes_):
            instruction_hits += 1
        else:
            failures.append(
                f"{target_addr}: missing instruction evidence at {instruction_addr} {mnemonic} {operands} {bytes_}"
            )

    report: dict[str, object] = {
        "status": "PASS" if not failures else "FAIL",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "targetCount": len(TARGETS),
        "commentedTargets": commented,
        "signatureHardenedTargets": signature_hardened,
        "callerHits": caller_hits,
        "instructionEvidenceHits": instruction_hits,
        "drySummary": dry_summary,
        "applySummary": apply_summary,
        "inputs": {
            "dryLog": relative(dry_log_path),
            "applyLog": relative(apply_log_path),
            "metadata": relative(metadata_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
            "tags": relative(tags_path),
        },
        "failures": failures,
        "notProven": [
            "Runtime collision behavior is not proven.",
            "Exact Stuart-source method identity is not proven.",
            "Concrete FVector/Vec3/AABB/mesh-collision layouts, locals, and types are not fully recovered.",
            "BEA.exe was not launched or patched.",
            "Rebuild parity is not proven.",
        ],
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail with non-zero status if validation fails")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--dry-log", type=Path, default=DEFAULT_DRY)
    parser.add_argument("--apply-log", type=Path, default=DEFAULT_APPLY)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--instructions", type=Path, default=DEFAULT_INSTRUCTIONS)
    parser.add_argument("--tags", type=Path, default=DEFAULT_TAGS)
    args = parser.parse_args()

    report = build_report(
        dry_log_path=args.dry_log,
        apply_log_path=args.apply_log,
        metadata_path=args.metadata,
        decompile_dir=args.decompile_dir,
        xrefs_path=args.xrefs,
        instructions_path=args.instructions,
        tags_path=args.tags,
    )
    out_path = resolve(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(
        f"status={report['status']} targets={report['targetCount']} "
        f"commented={report['commentedTargets']} signature_hardened={report['signatureHardenedTargets']} "
        f"caller_hits={report['callerHits']} instruction_hits={report['instructionEvidenceHits']}"
    )
    print(f"wrote={relative(out_path)}")
    if report["failures"]:
        for failure in report["failures"]:
            print(f"FAIL: {failure}")
    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
