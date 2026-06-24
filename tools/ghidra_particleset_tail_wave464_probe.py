#!/usr/bin/env python3
"""Validate Wave464 ParticleSet tail static metadata corrections."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave464-particleset-tail-current"
COMMON_TAGS = {"static-reaudit", "particleset-tail-wave464", "retail-binary-evidence"}

EXPECTED_DRY = {
    "updated": 0,
    "skipped": 8,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 3,
    "missing": 0,
    "bad": 0,
}
EXPECTED_APPLY = {
    "updated": 8,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 3,
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
    "0x004cc870": target(
        "CParticleSet__dtor_base",
        "void __fastcall CParticleSet__dtor_base(void * particle_set)",
        ["Wave464 correction", "base vtable pointer", "PTR_LAB_005ddad4"],
        ["particle-set", "destructor", "name-corrected", "signature-corrected", "comment-hardened"],
        ["PTR_LAB_005ddad4"],
    ),
    "0x004ccb40": target(
        "CParticleSet__shared_scalar_deleting_dtor",
        "void * __thiscall CParticleSet__shared_scalar_deleting_dtor(void * this, int flags)",
        ["Wave464 correction", "scalar-deleting destructor", "flags bit 0", "CParticleSet__dtor_base"],
        ["particle-set", "destructor", "name-corrected", "signature-corrected", "comment-hardened"],
        ["CParticleSet__dtor_base", "CDXMemoryManager__Free", "flags & 1"],
    ),
    "0x004ccc50": target(
        "CPDSelector__DispatchChildVFunc20",
        "void __thiscall CPDSelector__DispatchChildVFunc20(void * this, int dispatch_context)",
        ["Wave464 correction", "+0x5c..+0x68", "vfunc +0x20", "dispatch_context"],
        ["particle-descriptor", "selector", "name-corrected", "signature-corrected", "comment-hardened"],
        ["+ 0x5c", "+ 0x20", "dispatch_context"],
    ),
    "0x004cd290": target(
        "CParticleSet__InitType11",
        "void __fastcall CParticleSet__InitType11(void * particle_set)",
        ["Wave464 correction", "type 11", "+0x64=100", "+0x74=1"],
        ["particle-set", "type-init", "signature-corrected", "comment-hardened"],
        ["100", "+ 0x74", "PTR_CPDMesh__scalar_deleting_dtor_005ddb3c"],
    ),
    "0x004cd2d0": target(
        "CParticleSet__InitType12",
        "void __fastcall CParticleSet__InitType12(void * particle_set)",
        ["Wave464 correction", "type 12", "+0x5c/+0x60/+0x64"],
        ["particle-set", "type-init", "signature-corrected", "comment-hardened"],
        ["PTR_CParticleSet__shared_scalar_deleting_dtor_005ddfc8", "+ 0x5c", "+ 0x60"],
    ),
    "0x004cd3c0": target(
        "CParticleSet__InitType13",
        "void __fastcall CParticleSet__InitType13(void * particle_set)",
        ["Wave464 correction", "type 13", "180.0", "360.0"],
        ["particle-set", "type-init", "signature-corrected", "comment-hardened"],
        ["0x43340000", "0x43b40000", "PTR_CParticleSet__shared_scalar_deleting_dtor_005de030"],
    ),
    "0x004cd7f0": target(
        "CParticleSet__LoadFromArchive",
        "int __thiscall CParticleSet__LoadFromArchive(void * this, void * archive_source)",
        ["Wave464 correction", "0x1388c archive workspace", "token ids 0/1/2/3/4", "resolving references"],
        ["particle-set", "archive-load", "signature-corrected", "comment-hardened"],
        ["CTokenArchive__ReadNextToken", "CParticleSet__CreateByType", "CTokenArchive__ResolveReferences"],
    ),
    "0x004cda60": target(
        "CParticleSet__LoadParticleSetFile",
        "int __thiscall CParticleSet__LoadParticleSetFile(void * this, int particle_set_mode)",
        ["Wave464 correction", "MainSet.par", "Frontend.par", "CDXMemBuffer__OpenReadMode11"],
        ["particle-set", "file-load", "signature-corrected", "comment-hardened"],
        ["s_data_ParticleSets_MainSet_par", "s_data_ParticleSets_Frontend_par", "CParticleSet__LoadFromArchive"],
    ),
}

EXPECTED_XREF_EDGES = {
    ("0x004cc870", "0x004ccb43", "CParticleSet__shared_scalar_deleting_dtor"),
    ("0x004ccb40", "0x005ddbb8", "<no_function>"),
    ("0x004ccc50", "0x005dde48", "<no_function>"),
    ("0x004cd290", "0x004cc764", "CParticleSet__CreateByType"),
    ("0x004cd2d0", "0x004cc794", "CParticleSet__CreateByType"),
    ("0x004cd3c0", "0x004cc7c7", "CParticleSet__CreateByType"),
    ("0x004cd7f0", "0x004cdb3d", "CParticleSet__LoadParticleSetFile"),
    ("0x004cda60", "0x00468884", "CFrontEnd__LoadSharedResources"),
    ("0x004cda60", "0x0046cdc9", "CGame__LoadResources"),
}

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime rendering proven",
    "exact layout proven",
    "source identity proven",
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
    match = re.search(r"updated=\d+.*bad=\d+", text)
    if not match:
        return {}
    return {key: int(value) for key, value in re.findall(r"([a-z_]+)=(\d+)", match.group(0))}


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
    parser.add_argument("--base", type=Path, default=BASE, help="Wave464 artifact directory")
    args = parser.parse_args()

    status, failures = run_checks(args.base)
    print(f"STATUS {status}")
    for failure in failures:
        print(f"FAIL {failure}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
