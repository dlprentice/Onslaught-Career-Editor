#!/usr/bin/env python3
"""Validate Wave443 CMesh Ghidra metadata corrections."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave443-cmesh-current"

COMMON_TAGS = {"static-reaudit", "cmesh-wave443", "retail-binary-evidence"}
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
    "0x004a5020": target(
        "CMesh__Init",
        "void * __thiscall CMesh__Init(void * this)",
        ["+0x150 resource buffer", "DAT_00704ad8/g_pMeshList", "rebuild parity remain unproven"],
        ["cmesh", "init", "resource-list", "signature-corrected", "comment-hardened"],
        ["OID__AllocObject(0x28", "DAT_00704ad8"],
    ),
    "0x004a50b0": target(
        "CMesh__FreeResourcesAndUnlink",
        "void __thiscall CMesh__FreeResourcesAndUnlink(void * this)",
        ["unlink this", "CMeshPart__FreeResources", "+0x170", "rebuild parity remain unproven"],
        ["cmesh", "resource-cleanup", "linked-list", "signature-corrected", "comment-hardened"],
        ["CMeshPart__FreeResources", "DAT_00704ad8", "CDXMemoryManager__Free"],
    ),
    "0x004a51f0": target(
        "CMeshPart__FreeResources",
        "void __thiscall CMeshPart__FreeResources(void * this)",
        ["tail jump into the existing 0x004ae640", "influence-map runtime buffers", "rebuild parity remain unproven"],
        ["cmeshpart", "resource-cleanup", "thunk", "signature-corrected", "comment-hardened"],
        ["CInfluenceMap__FreeRuntimeBuffers", "+ 0x138"],
    ),
    "0x004a5200": target(
        "CMesh__InitStatic",
        "int __cdecl CMesh__InitStatic(void)",
        ["DAT_00704adc", "meshtex\\default.tga", "rebuild parity remain unproven"],
        ["cmesh", "static-init", "default-texture", "signature-corrected", "comment-hardened"],
        ["DAT_00704adc", "CTexture__FindTexture", "meshtex_default_tga"],
    ),
    "0x004a5500": target(
        "CMesh__MapStateNameToId",
        "void __stdcall CMesh__MapStateNameToId(char * state_name, void * state_record)",
        ["STAND", "SHOOTWALK", "RET 0x8", "source parity remain unproven"],
        ["cmesh", "animation-state", "state-map", "signature-corrected", "comment-hardened"],
        ["s_SHOOTWALK", "+ 0x10", "state_record"],
    ),
    "0x004a5670": target(
        "CMesh__OptimizeTextures",
        "void __thiscall CMesh__OptimizeTextures(void * this)",
        ["0x24-byte material entries", "dynamic-vertex material slots", "rebuild parity remain unproven"],
        ["cmesh", "texture-dedup", "optimization", "signature-corrected", "comment-hardened"],
        ["s_OptimiseTextures", "DebugTrace", "+ 0x15c"],
    ),
    "0x004a5970": target(
        "CMesh__LoadByNameWithStatus",
        "int __thiscall CMesh__LoadByNameWithStatus(void * this, char * mesh_name, void * load_context)",
        ["data\\Meshes", "this+0x24", "RET 0x8", "rebuild parity remain unproven"],
        ["cmesh", "load-wrapper", "file-io", "signature-corrected", "comment-hardened"],
        ["CDXMemBuffer__InitFromFile", "CMesh__Load", "s_data_Meshes"],
    ),
    "0x004a5b70": target(
        "CMesh__Load",
        "int __thiscall CMesh__Load(void * this, void * mem_buffer, void * load_context)",
        ["DAT_00704a90", "old and newer CMeshPart load paths", "CMesh__OptimizeTextures", "rebuild parity remain unproven"],
        ["cmesh", "stream-load", "mesh-format", "signature-corrected", "comment-hardened"],
        ["DAT_00704a90", "CMesh__MapStateNameToId", "CMeshPart__CacheFrameData"],
    ),
}

EXPECTED_XREF_EDGES = [
    ("0x004a5020", "CMesh__FindOrCreate"),
    ("0x004a50b0", "CMesh__ClearOut"),
    ("0x004a51f0", "CMesh__FreeResourcesAndUnlink"),
    ("0x004a5200", "CLTShell__InitializeRuntimeAndLoadCoreResources"),
    ("0x004a5500", "CMesh__Load"),
    ("0x004a5670", "CMesh__Load"),
    ("0x004a5970", "CMesh__FindOrCreate"),
    ("0x004a5b70", "CMesh__LoadByNameWithStatus"),
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
            failures.append(f"post_xrefs.tsv: missing edge {target_addr} from {from_name}")


def run(base: Path) -> dict[str, object]:
    failures: list[str] = []
    check_verify_log(base, failures)
    check_metadata(base, failures)
    check_xrefs(base, failures)
    return {
        "status": "PASS" if not failures else "FAIL",
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "base": relative_or_absolute(base),
        "targetCount": len(TARGETS),
        "failures": failures,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--base", type=Path, default=BASE)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")

    base = args.base if args.base.is_absolute() else ROOT / args.base
    result = run(base)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Wave443 CMesh probe: {result['status']}")
        print(f"Base: {result['base']}")
        print(f"Targets: {result['targetCount']}")
        for failure in result["failures"]:  # type: ignore[index]
            print(f"- {failure}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
