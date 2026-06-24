#!/usr/bin/env python3
"""Validate Wave461 particle-descriptor static metadata corrections."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave461-particle-descriptor-current"
COMMON_TAGS = {"static-reaudit", "particle-descriptor-wave461", "retail-binary-evidence"}

EXPECTED_DRY = {
    "updated": 0,
    "skipped": 14,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 12,
    "missing": 0,
    "bad": 0,
}
EXPECTED_APPLY = {
    "updated": 14,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 12,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_VERIFY_DRY = {
    "updated": 0,
    "skipped": 14,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}


def target(name: str, signature: str, comment_tokens: list[str], tags: list[str], decompile_tokens: list[str]) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "decompileTokens": decompile_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x004c07f0": target(
        "CPDSimpleSprite__WriteTokenFields",
        "void __fastcall CPDSimpleSprite__WriteTokenFields(void * this)",
        ["Wave461 correction", "CPDSimpleSprite", "writes token fields", "tokens 6 through 0x1b"],
        ["simple-sprite", "token-writer", "signature-corrected", "comment-hardened"],
        ["CTokenArchive__WriteFloatPointer(6", "CTokenArchive__WriteString(0xb", "CTokenArchive__WriteFloatPointer(0x18"],
    ),
    "0x004c1970": target(
        "CPDEmitter__WriteTokenFields",
        "void __fastcall CPDEmitter__WriteTokenFields(void * this)",
        ["Wave461 correction", "CPDEmitter", "vtable slot 7", "0x1a through 0x28"],
        ["emitter", "token-writer", "signature-corrected", "comment-hardened"],
        ["CTokenArchive__WriteFloatPointer(0x1a", "CTokenArchive__WritePointer(0x28"],
    ),
    "0x004c2220": target(
        "CPDSelector__WriteTokenFields",
        "void __fastcall CPDSelector__WriteTokenFields(void * this)",
        ["Wave461 correction", "CPDSelector", "vtable slot 7", "0x29 through 0x30"],
        ["selector", "token-writer", "signature-corrected", "comment-hardened"],
        ["CTokenArchive__WritePointer(0x29", "CTokenArchive__WriteInt(0x30"],
    ),
    "0x004c2400": target(
        "CPDColourRange__WriteTokenFields",
        "void __fastcall CPDColourRange__WriteTokenFields(void * this)",
        ["Wave461 correction", "CPDColourRange", "vtable slot 7", "0x31 through 0x3c"],
        ["colour-range", "token-writer", "signature-corrected", "comment-hardened"],
        ["CTokenArchive__WriteFloatPointer(0x31", "CTokenArchive__WriteFloat(0x3c"],
    ),
    "0x004c2ca0": target(
        "CPDShape__WriteTokenFields",
        "void __fastcall CPDShape__WriteTokenFields(void * this)",
        ["Wave461 correction", "CPDShape", "vtable slot 7", "0x3f through 0x46"],
        ["shape", "token-writer", "signature-corrected", "comment-hardened"],
        ["CTokenArchive__WriteInt(0x3f", "CTokenArchive__WriteFloat(0x46"],
    ),
    "0x004c3440": target(
        "CPDTrail__WriteTokenFields",
        "void __fastcall CPDTrail__WriteTokenFields(void * this)",
        ["Wave461 correction", "CPDTrail", "vtable slot 7", "0x47 through 0x54"],
        ["trail", "token-writer", "signature-corrected", "comment-hardened"],
        ["CTokenArchive__WriteString(0xb", "CTokenArchive__WriteFloatPointer(0x53"],
    ),
    "0x004c4920": target(
        "CPDFunction__WriteTokenFields",
        "void __fastcall CPDFunction__WriteTokenFields(void * this)",
        ["Wave461 correction", "CPDFunction", "vtable slot 7", "0x5c through 0x64"],
        ["function", "token-writer", "signature-corrected", "comment-hardened"],
        ["CTokenArchive__WriteFloatPointer(0x5c", "CTokenArchive__WriteInt(100"],
    ),
    "0x004c49b0": target(
        "CPDMesh__dtor_base",
        "void __fastcall CPDMesh__dtor_base(void * this)",
        ["Wave461 correction", "CPDMesh destructor-base", "+0x5c resource pointer", "+0x170 refcount"],
        ["mesh", "dtor-base", "signature-corrected", "comment-hardened"],
        ["+ 0x170", "PTR_", "+ 0x5c"],
    ),
    "0x004c4ae0": target(
        "CPDMesh__scalar_deleting_dtor",
        "void * __thiscall CPDMesh__scalar_deleting_dtor(void * this, byte flags)",
        ["Wave461 correction", "CPDMesh vtable slot 0", "CPDMesh__dtor_base", "flags & 1"],
        ["mesh", "scalar-deleting-dtor", "vtable-slot", "signature-corrected", "comment-hardened"],
        ["CPDMesh__dtor_base", "CDXMemoryManager__Free"],
    ),
    "0x004c4c70": target(
        "CPDMesh__WriteTokenFields",
        "void __fastcall CPDMesh__WriteTokenFields(void * this)",
        ["Wave461 correction", "CPDMesh", "vtable slot 7", "0x65 through 0x68"],
        ["mesh", "token-writer", "signature-corrected", "comment-hardened"],
        ["CTokenArchive__WriteString(0x65", "CTokenArchive__WritePointer(0x67"],
    ),
    "0x004c53b0": target(
        "CPDFoR__WriteTokenFields",
        "void __fastcall CPDFoR__WriteTokenFields(void * this)",
        ["Wave461 correction", "CPDFoR", "vtable slot 7", "0x69, 0x6a, and 0x28"],
        ["for", "token-writer", "signature-corrected", "comment-hardened"],
        ["CTokenArchive__WritePointer(0x69", "CTokenArchive__WritePointer(0x28"],
    ),
    "0x004c5410": target(
        "CParticleDescriptor__Update",
        "int __thiscall CParticleDescriptor__Update(void * this, void * particle)",
        ["Wave461 correction", "CParticleDescriptor update", "CParticleManager__CreateEffect", "fallback particle"],
        ["particle-descriptor", "update", "signature-corrected", "comment-hardened"],
        ["CParticleManager__CreateEffect", "CParticleManager__AllocateParticle", "CUnit__PushTransformHistoryAndSetCurrent"],
    ),
    "0x004c5730": target(
        "CParticleDescriptor__Load",
        "int __thiscall CParticleDescriptor__Load(void * this, void * token_archive)",
        ["Wave461 correction", "CParticleDescriptor load", "1000-byte temp token buffer", "CTokenArchive__ReadNextToken"],
        ["particle-descriptor", "load", "signature-corrected", "comment-hardened"],
        ["OID__AllocObject(1000", "CTokenArchive__ReadNextToken", "CTokenArchive__RegisterReferenceFixup"],
    ),
    "0x004c59e0": target(
        "CPDPMesh__WriteTokenFields",
        "void __fastcall CPDPMesh__WriteTokenFields(void * this)",
        ["Wave461 correction", "CPDPMesh", "vtable slot 7", "0x6b through 0x7b"],
        ["pmesh", "token-writer", "signature-corrected", "comment-hardened"],
        ["CTokenArchive__WriteString(0xb", "CTokenArchive__WriteFloatPointer(0x7b"],
    ),
}

EXPECTED_XREF_EDGES = {
    ("0x004c07f0", "0x005ddf7c", "<no_function>"),
    ("0x004c1970", "0x005ddf14", "<no_function>"),
    ("0x004c2220", "0x005dde44", "<no_function>"),
    ("0x004c2400", "0x005ddddc", "<no_function>"),
    ("0x004c2ca0", "0x005ddd0c", "<no_function>"),
    ("0x004c3440", "0x005ddca4", "<no_function>"),
    ("0x004c4920", "0x005ddbd4", "<no_function>"),
    ("0x004c49b0", "0x004c4ae3", "CPDMesh__scalar_deleting_dtor"),
    ("0x004c4ae0", "0x005ddb3c", "<no_function>"),
    ("0x004c4c70", "0x005ddb58", "<no_function>"),
    ("0x004c53b0", "0x005ddfe4", "<no_function>"),
    ("0x004c5410", "0x005ddff0", "<no_function>"),
    ("0x004c5730", "0x005de048", "<no_function>"),
    ("0x004c59e0", "0x005de04c", "<no_function>"),
}

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime particle behavior proven",
    "runtime rendering proven",
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
    wanted = normalize_address(address)[2:]
    for path in directory.glob(f"{wanted}_*.c"):
        return read_text(path)
    return ""


def parse_summary(text: str) -> dict[str, int]:
    match = re.search(r"SUMMARY\s+(.+)", text)
    if not match:
        return {}
    return {key: int(value) for key, value in re.findall(r"([a-z_]+)=(\d+)", match.group(1))}


def check_summary(path: Path, expected: dict[str, int], failures: list[str]) -> None:
    actual = parse_summary(read_text(path))
    if not actual:
        failures.append(f"{path.name}: missing SUMMARY")
        return
    for key, value in expected.items():
        if actual.get(key) != value:
            failures.append(f"{path.name}: expected {key}={value}, got {actual.get(key)}")


def check_metadata(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_metadata.tsv")
    if len(rows) < len(TARGETS):
        failures.append(f"post_metadata.tsv: expected at least {len(TARGETS)} rows, got {len(rows)}")
    for address, expected in TARGETS.items():
        row = row_by_address(rows, address)
        if row is None:
            failures.append(f"post_metadata.tsv: missing {address}")
            continue
        if row.get("name") != expected["name"]:
            failures.append(f"{address}: name {row.get('name')} != {expected['name']}")
        if row.get("signature") != expected["signature"]:
            failures.append(f"{address}: signature {row.get('signature')} != {expected['signature']}")
        comment = row.get("comment", "")
        for token in expected["commentTokens"]:
            if not token_present(comment, str(token)):
                failures.append(f"{address}: comment missing token {token!r}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                failures.append(f"{address}: comment contains overclaim token {token!r}")


def check_tags(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_tags.tsv")
    seen: dict[str, set[str]] = {}
    for row in rows:
        tags = {tag for tag in row.get("tags", "").split(";") if tag}
        seen.setdefault(row.get("address", ""), set()).update(tags)
    for address, expected in TARGETS.items():
        actual = seen.get(normalize_address(address), set())
        for tag in expected["tags"]:
            if tag not in actual:
                failures.append(f"{address}: missing tag {tag}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    edges = {(row.get("target_addr", ""), row.get("from_addr", ""), row.get("from_function", "")) for row in rows}
    for edge in EXPECTED_XREF_EDGES:
        if edge not in edges:
            failures.append(f"post_xrefs.tsv: missing edge {edge}")


def check_decompile(base: Path, failures: list[str]) -> None:
    for address, expected in TARGETS.items():
        decompile = decompile_text_for(base, address)
        if not decompile:
            failures.append(f"{address}: missing post decompile export")
            continue
        for token in expected["decompileTokens"]:
            if not token_present(decompile, str(token)):
                failures.append(f"{address}: decompile missing token {token!r}")


def run_checks(base: Path) -> tuple[str, list[str]]:
    failures: list[str] = []
    check_summary(base / "dry.log", EXPECTED_DRY, failures)
    check_summary(base / "apply.log", EXPECTED_APPLY, failures)
    check_summary(base / "verify_dry.log", EXPECTED_VERIFY_DRY, failures)
    check_metadata(base, failures)
    check_tags(base, failures)
    check_xrefs(base, failures)
    check_decompile(base, failures)
    return ("FAIL" if failures else "PASS", failures)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Accepted for npm-script consistency")
    parser.add_argument("--base", type=Path, default=BASE, help="Wave461 artifact directory")
    args = parser.parse_args()

    status, failures = run_checks(args.base)
    print(f"STATUS {status}")
    for failure in failures:
        print(f"FAIL {failure}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
