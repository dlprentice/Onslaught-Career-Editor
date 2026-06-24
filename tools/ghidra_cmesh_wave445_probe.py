#!/usr/bin/env python3
"""Validate Wave445 CMesh / MeshCollisionVolume Ghidra metadata corrections."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave445-cmesh-collision-current"

COMMON_TAGS = {"static-reaudit", "cmesh-wave445", "retail-binary-evidence"}
EXPECTED_VERIFY_DRY = {
    "updated": 0,
    "skipped": 9,
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
    "0x004aab90": target(
        "CMesh__Deserialize",
        "void * __cdecl CMesh__Deserialize(void * primary_reader, void * resource_reader)",
        ["chunk-reader streams", "0x174-byte CMesh", "m_%s.aya", "rebuild parity remain unproven"],
        ["cmesh", "deserialize", "aya-resource", "signature-corrected", "comment-hardened"],
        ["primary_reader", "resource_reader", "CMesh__Deserialize", "CMesh__InitPartVBufTextureFormats"],
    ),
    "0x004ab330": target(
        "CMesh__FindByRuntimeId",
        "void * __cdecl CMesh__FindByRuntimeId(int runtime_id)",
        ["DAT_00704ad8/g_pMeshList", "+0x154", "runtime_id", "rebuild parity remain unproven"],
        ["cmesh", "global-list", "runtime-id", "signature-corrected", "comment-hardened"],
        ["runtime_id", "DAT_00704ad8", "+ 0x154"],
    ),
    "0x004ab360": target(
        "CMesh__OptimizeParts",
        "void __thiscall CMesh__OptimizeParts(void * this)",
        ["DAT_00704af0", "Nexus/protected dependencies", "DAT_00704af4", "rebuild parity remain unproven"],
        ["cmesh", "optimize-parts", "signature-corrected", "comment-hardened"],
        ["DAT_00704af0", "+ 0x15c", "DAT_00704af4"],
    ),
    "0x004ac0e0": target(
        "CMeshCollisionVolume__dtor_base",
        "void __thiscall CMeshCollisionVolume__dtor_base(void * this)",
        ["destructor body", "0x00426300", "+0x24", "rebuild parity remain unproven"],
        ["mesh-collision-volume", "destructor", "owner-corrected", "renamed", "signature-corrected", "comment-hardened"],
        ["CMeshCollisionVolume__dtor_base", "+ 0x24", "CDXMemoryManager__Free"],
    ),
    "0x004acde0": target(
        "CMeshCollisionVolume__InitContactOutputRecord",
        "undefined CMeshCollisionVolume__InitContactOutputRecord(void)",
        ["comment/tag hardening only", "Signature intentionally deferred", "EBX/register state", "rebuild parity remain unproven"],
        ["mesh-collision-volume", "contact-output", "signature-deferred", "comment-hardened"],
        ["CMeshCollisionVolume__InitContactOutputRecord", "undefined", "EBX"],
    ),
    "0x004ad600": target(
        "CMeshCollisionVolume__SetPartBounds",
        "void __thiscall CMeshCollisionVolume__SetPartBounds(void * this, void * mesh, int part_index, float bounds_status)",
        ["0x74", "0x6c", "bounds_status", "RET 0x0c", "rebuild parity remain unproven"],
        ["mesh-collision-volume", "part-bounds", "signature-corrected", "comment-hardened"],
        ["bounds_status", "part_index", "OID__AllocObject", "0x74"],
    ),
    "0x004adf90": target(
        "CMesh__ReleaseEmbeddedResources",
        "void __thiscall CMesh__ReleaseEmbeddedResources(void * this)",
        ["0x24-byte", "CDXEngine resource refcount", "rebuild parity remain unproven"],
        ["cmesh", "resource-release", "signature-corrected", "comment-hardened"],
        ["CMesh__ReleaseEmbeddedResources", "CDXMemoryManager__Free", "+ 0xc"],
    ),
    "0x004ae080": target(
        "CMesh__InitSingleVertexPartDefaults",
        "void __thiscall CMesh__InitSingleVertexPartDefaults(void * this)",
        ["CMeshPart__SetVertexCount(1)", "1.0f", "rebuild parity remain unproven"],
        ["cmesh", "single-vertex-defaults", "signature-corrected", "comment-hardened"],
        ["CMesh__InitSingleVertexPartDefaults", "CMeshPart__SetVertexCount", "0x3f800000"],
    ),
    "0x004ae0d0": target(
        "CMesh__InitPartVBufTextureFormats",
        "void __thiscall CMesh__InitPartVBufTextureFormats(void * this)",
        ["CVBufTexture__GetOrCreate", "0x152/8/0x24/4/1", "0x65/8/2/1", "rebuild parity remain unproven"],
        ["cmesh", "vbuf-texture", "signature-corrected", "comment-hardened"],
        ["CMesh__InitPartVBufTextureFormats", "CVBufTexture__GetOrCreate", "CVBufTexture__SetVBFormat"],
    ),
}

EXPECTED_XREF_EDGES = [
    ("0x004aab90", "CResourceAccumulator__ReadResourceFile"),
    ("0x004aab90", "CFEPGoodies__Deserialise"),
    ("0x004aab90", "CMesh__Deserialize"),
    ("0x004ab330", "CDXImposter__Create"),
    ("0x004ab360", "CMesh__Load"),
    ("0x004ac0e0", "CMeshCollisionVolume__ScalarDeletingDestructor_00426300"),
    ("0x004acde0", "<no_function>"),
    ("0x004ad600", "<no_function>"),
    ("0x004adf90", "CMesh__InitStatic"),
    ("0x004adf90", "CMesh__ClearOut"),
    ("0x004adf90", "CMesh__FreeResourcesAndUnlink"),
    ("0x004adf90", "CMesh__Deserialize"),
    ("0x004ae080", "CMesh__InitStatic"),
    ("0x004ae080", "CMesh__Load"),
    ("0x004ae0d0", "CMesh__Load"),
    ("0x004ae0d0", "CMesh__Deserialize"),
]

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
        for key in ("address", "target_addr", "from_addr", "from_function_addr"):
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


def relative_or_absolute(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def check_verify_log(base: Path, failures: list[str]) -> None:
    text = read_text(base / "apply_verify_dry.log")
    if not text:
        failures.append("apply_verify_dry.log: missing or empty")
        return
    summary = parse_summary(text)
    if summary != EXPECTED_VERIFY_DRY:
        failures.append(f"apply_verify_dry.log: summary mismatch expected {EXPECTED_VERIFY_DRY}, got {summary}")
    for token in ("FAIL:", "Exception", "LockException"):
        if token in text:
            failures.append(f"apply_verify_dry.log: unexpected failure token {token!r}")
    if "REPORT: Save succeeded" not in text:
        failures.append("apply_verify_dry.log: missing Ghidra save-success marker")


def check_metadata(base: Path, failures: list[str]) -> None:
    metadata = read_tsv(base / "post_metadata.tsv")
    tags = read_tsv(base / "post_tags.tsv")

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
                failures.append(f"{address}: comment missing token {token!r}")
        lowered_comment = comment.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered_comment:
                failures.append(f"{address}: overclaim token present {token!r}")

        tag_row = row_by_address(tags, address)
        if tag_row is None:
            failures.append(f"{address}: missing post_tags row")
        else:
            actual_tags = {item.strip() for item in re.split(r"[;,]", tag_row.get("tags", "")) if item.strip()}
            missing_tags = sorted(set(spec["tags"]) - actual_tags)  # type: ignore[arg-type]
            if missing_tags:
                failures.append(f"{address}: missing tags {missing_tags}")

        decompile = decompile_text_for(base, address)
        if not decompile:
            failures.append(f"{address}: missing post-decomp export")
        for token in spec["decompileTokens"]:  # type: ignore[index]
            if not token_present(decompile, str(token)):
                failures.append(f"{address}: decompile missing token {token!r}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    if len(rows) < len(TARGETS):
        failures.append(f"post_xrefs.tsv: expected at least {len(TARGETS)} rows, got {len(rows)}")
    for target_addr, from_name in EXPECTED_XREF_EDGES:
        wanted = normalize_address(target_addr)
        if not any(row.get("target_addr") == wanted and row.get("from_function") == from_name for row in rows):
            failures.append(f"post_xrefs.tsv: missing edge {wanted} <- {from_name}")


def run_checks(base: Path) -> tuple[str, list[str]]:
    failures: list[str] = []
    if not base.is_dir():
        failures.append(f"base directory missing: {relative_or_absolute(base)}")
        return "FAIL", failures

    check_verify_log(base, failures)
    check_metadata(base, failures)
    check_xrefs(base, failures)

    status = "PASS" if not failures else "FAIL"
    return status, failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    base = args.base.resolve()
    status, failures = run_checks(base)
    result = {
        "schema": "ghidra-cmesh-wave445-probe.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "base": relative_or_absolute(base),
        "targets": len(TARGETS),
        "failures": failures,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Wave445 CMesh/MeshCollisionVolume probe: {status}")
        print(f"Base: {relative_or_absolute(base)}")
        print(f"Targets: {len(TARGETS)}")
        for failure in failures:
            print(f"- {failure}")

    if args.check and failures:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
