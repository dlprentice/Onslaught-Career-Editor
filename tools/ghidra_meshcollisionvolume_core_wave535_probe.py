#!/usr/bin/env python3
"""Validate Wave535 MeshCollisionVolume core Ghidra metadata hardening."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave535-meshcollisionvolume-core-004abe50"
COMMON_TAGS = {
    "static-reaudit",
    "meshcollisionvolume-core-wave535",
    "retail-binary-evidence",
    "signature-corrected",
    "comment-hardened",
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
    "0x004abe50": target(
        "CMeshCollisionVolume__VFunc_02_004abe50",
        "int __thiscall CMeshCollisionVolume__VFunc_02_004abe50(void * this, void * query_arg0, void * query_arg1, void * source_sphere_record, void * contact_record)",
        ["vtable slot 2", "0x005d95d0", "RET 0x10", "rebuild parity remain unproven"],
        ["mesh-collision-volume", "vtable-slot"],
        ["source_sphere_record", "vtable slot +0x0c", "query_arg0,query_arg1,&local_28,contact_record"],
    ),
    "0x004ac000": target(
        "CMeshCollisionVolume__InitDirectionLookupTable",
        "void __cdecl CMeshCollisionVolume__InitDirectionLookupTable(void)",
        ["0x00704bf8..0x00704c54", "0x00704cc8", "rebuild parity remain unproven"],
        ["mesh-collision-volume", "lookup-table"],
        ["DAT_00704bf8", "DAT_00704cc8 = 1"],
    ),
    "0x004ac140": target(
        "CMeshCollisionVolume__TestSweptSphereAgainstBounds",
        "int __stdcall CMeshCollisionVolume__TestSweptSphereAgainstBounds(void * part_context, void * bounds_record, float * sphere_start, float * sweep_delta, float * sphere_radius, void * contact_record)",
        ["RET 0x18", "direction-table triangle faces", "Geometry__DistanceOutsideAabb", "rebuild parity remain unproven"],
        ["mesh-collision-volume", "swept-sphere", "bounds-test"],
        ["bounds_record", "Geometry__DistanceOutsideAabb", "contact_record + 0xe4"],
    ),
    "0x004ac4a0": target(
        "CMeshCollisionVolume__TestSweptSphereAgainstMeshPart",
        "int __stdcall CMeshCollisionVolume__TestSweptSphereAgainstMeshPart(void * part_context, void * mesh_part, float * sphere_start, float * sweep_delta, float * sphere_radius, void * contact_record)",
        ["RET 0x18", "mesh-part triangle bucket search", "mesh_part+0x100", "rebuild parity remain unproven"],
        ["mesh-collision-volume", "swept-sphere", "mesh-part-triangle"],
        ["mesh_part", "CMeshPart__StartTriangleBucketSearch", "contact_record + 0xe4"],
    ),
    "0x004acf30": target(
        "CMeshCollisionVolume__ResolveContactNormalAndPlane",
        "int __stdcall CMeshCollisionVolume__ResolveContactNormalAndPlane(float * contact_record, float hit_x, float hit_y, float hit_z, float hit_w, float normal_x, float normal_y, float normal_z, float normal_w, float unused_source_w, float * out_contact_point, float * out_contact_normal)",
        ["RET 0x30", "unused source value", "out_contact_point/out_contact_normal", "rebuild parity remain unproven"],
        ["mesh-collision-volume", "contact-resolution"],
        ["unused_source_w", "out_contact_point", "out_contact_normal"],
    ),
}

EXPECTED_XREFS = {
    ("0x004abe50", "005d95d0", "<no_function>"),
    ("0x004ac000", "004ac14c", "CMeshCollisionVolume__TestSweptSphereAgainstBounds"),
    ("0x004ac140", "004aca03", "CMeshCollisionVolume__VFunc_03_004ac6e0"),
    ("0x004ac4a0", "004aca31", "CMeshCollisionVolume__VFunc_03_004ac6e0"),
    ("0x004acf30", "004acd1b", "CMeshCollisionVolume__VFunc_03_004ac6e0"),
}

EXPECTED_VERIFY_DRY = {"updated": 0, "skipped": 5, "missing": 0, "bad": 0}
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
        for key in ("address", "target_addr"):
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


def decompile_text_for(address: str) -> str:
    directory = BASE / "post_decomp"
    if not directory.is_dir():
        return ""
    prefix = normalize_address(address)[2:]
    matches = sorted(directory.glob(f"{prefix}_*.c"))
    return read_text(matches[0]) if matches else ""


def parse_summary(text: str) -> dict[str, int] | None:
    match = re.search(r"SUMMARY\s+updated=(\d+)\s+skipped=(\d+)\s+missing=(\d+)\s+bad=(\d+)", text)
    if not match:
        return None
    keys = ["updated", "skipped", "missing", "bad"]
    return {key: int(value) for key, value in zip(keys, match.groups(), strict=True)}


def check_metadata(failures: list[str]) -> None:
    metadata = read_tsv(BASE / "post_metadata.tsv")
    tags = read_tsv(BASE / "post_tags.tsv")
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
        lowered = comment.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{address}: overclaim token present {token!r}")

        tag_row = row_by_address(tags, address)
        if tag_row is None:
            failures.append(f"{address}: missing post_tags row")
        else:
            actual = {item.strip() for item in re.split(r"[;,]", tag_row.get("tags", "")) if item.strip()}
            missing = sorted(set(spec["tags"]) - actual)  # type: ignore[arg-type]
            if missing:
                failures.append(f"{address}: missing tags {missing}")


def check_decompile(failures: list[str]) -> None:
    for address, spec in TARGETS.items():
        text = decompile_text_for(address)
        if not text:
            failures.append(f"{address}: missing post decompile")
            continue
        for token in spec["decompileTokens"]:  # type: ignore[index]
            if not token_present(text, str(token)):
                failures.append(f"{address}: decompile missing token {token!r}")
        lowered = text.lower()
        for token in OVERCLAIM_TOKENS:
            if token in lowered:
                failures.append(f"{address}: decompile overclaim token present {token!r}")


def check_xrefs(failures: list[str]) -> None:
    rows = read_tsv(BASE / "post_xrefs.tsv")
    actual = {
        (row.get("target_addr", ""), row.get("from_addr", "").lower(), row.get("from_function", ""))
        for row in rows
    }
    for target, from_addr, from_function in EXPECTED_XREFS:
        key = (normalize_address(target), from_addr.lower(), from_function)
        if key not in actual:
            failures.append(f"{target}: missing xref from {from_addr} / {from_function}")


def check_logs(failures: list[str]) -> None:
    apply_log = read_text(BASE / "apply_meshcollisionvolume_core_wave535_apply.log")
    verify_log = read_text(BASE / "apply_meshcollisionvolume_core_wave535_verify_dry.log")
    if parse_summary(apply_log) != {"updated": 5, "skipped": 0, "missing": 0, "bad": 0}:
        failures.append("apply log summary mismatch")
    if parse_summary(verify_log) != EXPECTED_VERIFY_DRY:
        failures.append("verify-dry log summary mismatch")
    for label, text in (("apply", apply_log), ("verify-dry", verify_log)):
        if "REPORT: Save succeeded" not in text:
            failures.append(f"{label} log missing save-success marker")
        for token in ("FAIL:", "Exception", "LockException", "BADNAME:", "MISSING:"):
            if token in text:
                failures.append(f"{label} log unexpected token {token!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    _ = parser.parse_args()

    failures: list[str] = []
    check_metadata(failures)
    check_decompile(failures)
    check_xrefs(failures)
    check_logs(failures)

    if failures:
        print("Wave535 MeshCollisionVolume core probe FAILED:")
        for failure in failures:
            print(f" - {failure}")
        return 1
    print("Wave535 MeshCollisionVolume core probe PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
