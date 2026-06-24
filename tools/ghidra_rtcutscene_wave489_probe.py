#!/usr/bin/env python3
"""Validate Wave489 RTCutscene/CRenderThing static RE evidence."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave489-rtcutscene-renderthing-004d6a30"

COMMON_TAGS = {"static-reaudit", "rtcutscene-wave489", "retail-binary-evidence"}


def spec(name: str, signature: str, tags: set[str], comment_tokens: list[str], decompile_tokens: list[str]) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "tags": COMMON_TAGS | tags,
        "comment_tokens": comment_tokens,
        "decompile_tokens": decompile_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x004d6a30": spec(
        "CRenderThing__Init",
        "void __thiscall CRenderThing__Init(void * this, void * init_record, int context_token)",
        {"crenderthing", "base-init", "signature-corrected", "renamed", "comment-hardened"},
        ["CRTCutscene__Init", "CRTMesh__Init", "0x3727c5ac", "init_record+0x400", "rebuild parity remain unproven"],
        ["CRenderThing__Init", "0x3727c5ac", "init_record"],
    ),
    "0x004d6b20": spec(
        "SharedVFunc__ReturnZero_004d6b20",
        "int __thiscall SharedVFunc__ReturnZero_004d6b20(void * this)",
        {"shared-vfunc", "return-zero", "signature-corrected", "renamed", "comment-hardened"},
        ["many unrelated vtables", "save/load callsites", "returns 0", "prevents an owner-specific label"],
        ["SharedVFunc__ReturnZero_004d6b20", "return 0"],
    ),
    "0x00405940": spec(
        "SharedVFunc__ReturnZeroRet4_00405940",
        "int __thiscall SharedVFunc__ReturnZeroRet4_00405940(void * this, void * arg0)",
        {"shared-vfunc", "return-zero", "ret4", "function-created", "signature-corrected", "comment-hardened"},
        ["function-boundary recovery", "slot 5", "previously missing", "RET 0x4"],
        ["SharedVFunc__ReturnZeroRet4_00405940", "return 0"],
    ),
    "0x004dbb60": spec(
        "CRTCutscene__CRTCutscene",
        "void __fastcall CRTCutscene__CRTCutscene(void * this)",
        {"rtcutscene", "constructor", "signature-corrected", "comment-hardened"},
        ["PCRTID__CreateObject", "type id 5", "vtable 0x005dea38", "this+0x18"],
        ["CRTCutscene__CRTCutscene", "PTR_CRTCutscene__scalar_deleting_dtor_005dea38"],
    ),
    "0x004dbb80": spec(
        "CRenderThing__VFunc_07_ClearRenderOutputs",
        "void __thiscall CRenderThing__VFunc_07_ClearRenderOutputs(void * this, void * arg0, void * arg1, void * out_vec4, void * out_matrix, void * arg4, void * arg5)",
        {"crenderthing", "vfunc-slot-07", "render-output", "function-created", "signature-corrected", "comment-hardened"},
        ["function-boundary recovery", "RET 0x18", "first three dwords", "0x0083ccd8", "fourth-lane semantics"],
        ["CRenderThing__VFunc_07_ClearRenderOutputs", "out_vec4", "out_matrix", "DAT_0083ccd8"],
    ),
    "0x004dbbe0": spec(
        "CRenderThing__VFunc_08_ClearVec3",
        "void __thiscall CRenderThing__VFunc_08_ClearVec3(void * this, void * out_vec3, void * arg1)",
        {"crenderthing", "vfunc-slot-08", "clear-vec3", "function-created", "signature-corrected", "comment-hardened"},
        ["function-boundary recovery", "RET 0x8", "clears three dwords", "vector type"],
        ["CRenderThing__VFunc_08_ClearVec3", "out_vec3"],
    ),
    "0x004dbc10": spec(
        "SharedVFunc__ReturnMinusOneRet4_004dbc10",
        "int __thiscall SharedVFunc__ReturnMinusOneRet4_004dbc10(void * this, void * arg0)",
        {"shared-vfunc", "return-minus-one", "ret4", "function-created", "signature-corrected", "comment-hardened"},
        ["function-boundary recovery", "slot 19", "returns -1", "RET 0x4"],
        ["SharedVFunc__ReturnMinusOneRet4_004dbc10", "return -1"],
    ),
    "0x004dbc30": spec(
        "CRTCutscene__scalar_deleting_dtor",
        "void * __thiscall CRTCutscene__scalar_deleting_dtor(void * this, byte flags)",
        {"rtcutscene", "destructor", "scalar-deleting-dtor", "signature-corrected", "renamed", "comment-hardened"},
        ["slot 0", "CRTCutscene__dtor", "delete flag bit 0", "CDXMemoryManager__Free"],
        ["CRTCutscene__scalar_deleting_dtor", "CRTCutscene__dtor(this)", "CDXMemoryManager__Free"],
    ),
    "0x004dbc50": spec(
        "CRTCutscene__dtor",
        "void __fastcall CRTCutscene__dtor(void * this)",
        {"rtcutscene", "destructor", "mesh-name-table", "signature-corrected", "renamed", "comment-hardened"},
        ["this+0x14", "this+0x20", "0x100-byte name buffer", "CRenderThing vtable"],
        ["CRTCutscene__dtor", "CDXMemoryManager__Free", "CRenderThing__scalar_deleting_dtor"],
    ),
    "0x004dbd20": spec(
        "CRenderThing__dtor",
        "void __fastcall CRenderThing__dtor(void * this)",
        {"crenderthing", "destructor", "owner-corrected", "signature-corrected", "renamed", "comment-hardened"},
        ["not as a constructor", "vtable 0x005deaac", "this+0x10", "delete flag 1"],
        ["CRenderThing__dtor", "PTR_CRenderThing__scalar_deleting_dtor_005deaac"],
    ),
    "0x004dbd50": spec(
        "CRenderThing__scalar_deleting_dtor",
        "void * __thiscall CRenderThing__scalar_deleting_dtor(void * this, byte flags)",
        {"crenderthing", "destructor", "scalar-deleting-dtor", "signature-corrected", "renamed", "comment-hardened"},
        ["slot 0", "this+0x10", "delete flag bit 0", "CDXMemoryManager__Free"],
        ["CRenderThing__scalar_deleting_dtor", "CDXMemoryManager__Free"],
    ),
    "0x004dbd80": spec(
        "CRTCutscene__Init",
        "void __thiscall CRTCutscene__Init(void * this, void * init_record)",
        {"rtcutscene", "init", "mesh-name-table", "signature-corrected", "comment-hardened"},
        ["slot 1", "CRenderThing__Init", "init_record+0x418", "0x100-byte buffer", "this+0x24 to -1"],
        ["CRTCutscene__Init", "CRenderThing__Init", "OID__AllocObject", "0xffffffff"],
    ),
    "0x004dbe50": spec(
        "CRTCutscene__Activate",
        "void __fastcall CRTCutscene__Activate(void * this)",
        {"rtcutscene", "activate", "mesh-cache", "function-created", "signature-corrected", "comment-hardened"},
        ["function-boundary recovery", "slot 12", "CMesh__FindOrCreate", "this+0x14", "sets active"],
        ["CRTCutscene__Activate", "CMesh__FindOrCreate", "this + 0x20"],
    ),
    "0x004dbe90": spec(
        "CRTCutscene__Reset",
        "void __fastcall CRTCutscene__Reset(void * this)",
        {"rtcutscene", "reset", "deactivate", "signature-corrected", "comment-hardened"},
        ["slot 13", "this+0x14", "this+0x20", "this+0x24 to -1"],
        ["CRTCutscene__Reset", "CDXMemoryManager__Free", "0xffffffff"],
    ),
    "0x004dbec0": spec(
        "CRTCutscene__RenderCurrent",
        "void __thiscall CRTCutscene__RenderCurrent(void * this, void * render_context)",
        {"rtcutscene", "render-current", "function-created", "signature-corrected", "comment-hardened"},
        ["function-boundary recovery", "slot 2", "DAT_00704e60", "0x00631e50", "runtime visual behavior"],
        ["CRTCutscene__RenderCurrent", "DebugTrace", "DAT_00704e60", "CSphere__RenderAnimatedRecursive"],
    ),
    "0x004dbf70": spec(
        "CRTCutscene__SetCurrentIndex",
        "void __thiscall CRTCutscene__SetCurrentIndex(void * this, int current_index)",
        {"rtcutscene", "current-index", "signature-corrected", "comment-hardened"},
        ["CCutscene update/prep", "this+0x24", "runtime cutscene behavior"],
        ["CRTCutscene__SetCurrentIndex", "current_index"],
    ),
    "0x004dbf80": spec(
        "CRTCutscene__GetCurrentMesh",
        "void * __fastcall CRTCutscene__GetCurrentMesh(void * this)",
        {"rtcutscene", "current-mesh", "getter", "function-created", "signature-corrected", "comment-hardened"},
        ["function-boundary recovery", "slot 9", "this+0x08", "this+0x20", "this+0x14 array"],
        ["CRTCutscene__GetCurrentMesh", "this + 0x14"],
    ),
    "0x004dbfb0": spec(
        "CRTCutscene__GetDefaultScalar",
        "float __fastcall CRTCutscene__GetDefaultScalar(void * this)",
        {"rtcutscene", "default-scalar", "float-return", "function-created", "signature-corrected", "comment-hardened"},
        ["function-boundary recovery", "slot 6", "0x005d856c", "default scalar"],
        ["CRTCutscene__GetDefaultScalar", "_DAT_005d856c"],
    ),
    "0x004dbfc0": spec(
        "CRTCutscene__GetCurrentMeshEntryValue",
        "float __thiscall CRTCutscene__GetCurrentMeshEntryValue(void * this, int type_id, int * out_index)",
        {"rtcutscene", "current-mesh", "entry-lookup", "float-return", "function-created", "signature-corrected", "comment-hardened"},
        ["function-boundary recovery", "slot 14", "CMesh__FindEntryValueByTypeId", "0x005d856c"],
        ["CRTCutscene__GetCurrentMeshEntryValue", "CMesh__FindEntryValueByTypeId"],
    ),
    "0x004dbff0": spec(
        "CRTCutscene__BuildCurrentFrameOutputs",
        "void __thiscall CRTCutscene__BuildCurrentFrameOutputs(void * this, void * out_primary, void * out_secondary, void * animation_query, void * out_scalar)",
        {"rtcutscene", "current-mesh", "frame-output", "function-created", "signature-corrected", "comment-hardened"},
        ["function-boundary recovery", "slot 17", "frame/sample index", "identity/default", "output record layouts"],
        ["CRTCutscene__BuildCurrentFrameOutputs", "CMesh__FindEntryByInclusiveRangeTable", "CMCMech__BuildInterpolatedPoseAndAnchor", "0x42b40000"],
    ),
}

VTABLE_EXPECTATIONS = {
    0: ("0x004dbc30", "CRTCutscene__scalar_deleting_dtor"),
    1: ("0x004dbd80", "CRTCutscene__Init"),
    2: ("0x004dbec0", "CRTCutscene__RenderCurrent"),
    5: ("0x00405940", "SharedVFunc__ReturnZeroRet4_00405940"),
    6: ("0x004dbfb0", "CRTCutscene__GetDefaultScalar"),
    7: ("0x004dbb80", "CRenderThing__VFunc_07_ClearRenderOutputs"),
    8: ("0x004dbbe0", "CRenderThing__VFunc_08_ClearVec3"),
    9: ("0x004dbf80", "CRTCutscene__GetCurrentMesh"),
    12: ("0x004dbe50", "CRTCutscene__Activate"),
    13: ("0x004dbe90", "CRTCutscene__Reset"),
    14: ("0x004dbfc0", "CRTCutscene__GetCurrentMeshEntryValue"),
    17: ("0x004dbff0", "CRTCutscene__BuildCurrentFrameOutputs"),
    18: ("0x004d6b20", "SharedVFunc__ReturnZero_004d6b20"),
    19: ("0x004dbc10", "SharedVFunc__ReturnMinusOneRet4_004dbc10"),
}

EXPECTED_SUMMARIES = {
    "apply_rtcutscene_wave489_dry.log": {"updated": 0, "skipped": 20, "created": 0, "would_create": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
    "apply_rtcutscene_wave489_apply_idempotent.log": {"updated": 20, "skipped": 0, "created": 0, "would_create": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
    "apply_rtcutscene_wave489_verify_dry.log": {"updated": 0, "skipped": 20, "created": 0, "would_create": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0},
}

XREF_EXPECTATIONS = [
    ("0x004d6a30", "0x004dbd8a", "CRTCutscene__Init", "UNCONDITIONAL_CALL"),
    ("0x004d6a30", "0x004dc398", "CRTMesh__Init", "UNCONDITIONAL_CALL"),
    ("0x004dbb60", "0x00516678", "PCRTID__CreateObject", "UNCONDITIONAL_CALL"),
    ("0x004dbc50", "0x004dbc33", "CRTCutscene__scalar_deleting_dtor", "UNCONDITIONAL_CALL"),
    ("0x004dbe50", "0x005dea68", "<no_function>", "DATA"),
    ("0x004dbec0", "0x005dea40", "<no_function>", "DATA"),
    ("0x004dbf70", "0x0043f82f", "CCutscene__Update", "UNCONDITIONAL_CALL"),
    ("0x004dbf70", "0x0043faee", "CCutscene__PrepareAnimations", "UNCONDITIONAL_CALL"),
]

OVERCLAIMS = ("fully re'ed", "runtime behavior proven", "source identity proven", "exact layout proven", "rebuild parity proven")


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
        for key in ("address", "target_addr", "from_addr", "vtable", "slot_addr", "pointer_addr", "function_entry", "containing_entry"):
            if key in row and row[key]:
                row[key] = normalize_address(row[key])
        if "comment" in row:
            row["comment"] = unescape(row["comment"])
    return rows


def parse_summary(text: str) -> dict[str, int] | None:
    match = re.search(
        r"updated=(\d+)\s+skipped=(\d+)\s+created=(\d+)\s+would_create=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        text,
    )
    if not match:
        return None
    keys = ("updated", "skipped", "created", "would_create", "renamed", "would_rename", "missing", "bad")
    return {key: int(value) for key, value in zip(keys, match.groups(), strict=True)}


def decompile_text(base: Path, address: str, name: str) -> str:
    path = base / "post-decomp" / f"{normalize_address(address)[2:]}_{name}.c"
    return read_text(path)


def check_logs(base: Path, failures: list[str]) -> None:
    for filename, expected in EXPECTED_SUMMARIES.items():
        text = read_text(base / filename)
        if not text:
            failures.append(f"{filename}: missing")
            continue
        if parse_summary(text) != expected:
            failures.append(f"{filename}: summary mismatch {parse_summary(text)} != {expected}")
        for bad in ("FAIL:", "LockException", "Exception:"):
            if bad in text:
                failures.append(f"{filename}: unexpected token {bad!r}")
        if "REPORT: Save succeeded" not in text:
            failures.append(f"{filename}: missing save-success marker")


def check_metadata(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_metadata.tsv")
    tags = read_tsv(base / "post_tags.tsv")
    if len(rows) != len(TARGETS):
        failures.append(f"post_metadata.tsv: expected {len(TARGETS)} rows, got {len(rows)}")
    for address, data in TARGETS.items():
        row = next((r for r in rows if r.get("address") == address), None)
        if row is None:
            failures.append(f"{address}: missing metadata")
            continue
        if row.get("name") != data["name"]:
            failures.append(f"{address}: name {row.get('name')} != {data['name']}")
        if compact(row.get("signature", "")) != compact(str(data["signature"])):
            failures.append(f"{address}: signature {row.get('signature')} != {data['signature']}")
        comment = row.get("comment", "")
        for token in data["comment_tokens"]:  # type: ignore[index]
            if not token_present(comment, str(token)):
                failures.append(f"{address}: comment missing token {token!r}")
        for token in OVERCLAIMS:
            if token_present(comment, token):
                failures.append(f"{address}: overclaim token {token!r}")
        tag_row = next((r for r in tags if r.get("address") == address), None)
        if tag_row is None:
            failures.append(f"{address}: missing tags")
            continue
        actual_tags = {part.strip() for part in re.split(r"[;,]", tag_row.get("tags", "")) if part.strip()}
        missing = set(data["tags"]) - actual_tags  # type: ignore[arg-type]
        if missing:
            failures.append(f"{address}: missing tags {sorted(missing)}")


def check_decompile(base: Path, failures: list[str]) -> None:
    for address, data in TARGETS.items():
        text = decompile_text(base, address, str(data["name"]))
        if not text:
            failures.append(f"{address}: missing decompile file")
            continue
        for token in data["decompile_tokens"]:  # type: ignore[index]
            if not token_present(text, str(token)):
                failures.append(f"{address}: decompile missing token {token!r}")


def check_vtable(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_vtable.tsv")
    if len(rows) != 20:
        failures.append(f"post_vtable.tsv: expected 20 rows, got {len(rows)}")
    for row in rows:
        if row.get("status") != "OK":
            failures.append(f"vtable slot {row.get('slot_index')}: non-OK status {row.get('status')}")
    for slot, (pointer, name) in VTABLE_EXPECTATIONS.items():
        row = next((r for r in rows if r.get("vtable") == "0x005dea38" and r.get("slot_index") == str(slot)), None)
        if row is None:
            failures.append(f"vtable slot {slot}: missing")
            continue
        if row.get("pointer_addr") != pointer:
            failures.append(f"vtable slot {slot}: pointer {row.get('pointer_addr')} != {pointer}")
        if row.get("function_name") != name:
            failures.append(f"vtable slot {slot}: name {row.get('function_name')} != {name}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    for target, from_addr, from_function, ref_type in XREF_EXPECTATIONS:
        row = next((r for r in rows if r.get("target_addr") == target and r.get("from_addr") == from_addr), None)
        if row is None:
            failures.append(f"{target}: missing xref from {from_addr}")
            continue
        if row.get("from_function") != from_function:
            failures.append(f"{target}: xref {from_addr} function {row.get('from_function')} != {from_function}")
        if row.get("ref_type") != ref_type:
            failures.append(f"{target}: xref {from_addr} type {row.get('ref_type')} != {ref_type}")


def check_instructions(base: Path, failures: list[str]) -> None:
    text = read_text(base / "post_instructions.tsv")
    for token in ("0x004dbb80", "RET\t0x18", "0x004dbec0", "CALL\t0x0040c640", "0x004dbff0", "RET\t0x10", "0x00405940", "RET\t0x4"):
        if token not in text:
            failures.append(f"post_instructions.tsv missing token {token!r}")


def run(base: Path = DEFAULT_BASE) -> list[str]:
    failures: list[str] = []
    check_logs(base, failures)
    check_metadata(base, failures)
    check_decompile(base, failures)
    check_vtable(base, failures)
    check_xrefs(base, failures)
    check_instructions(base, failures)
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    failures = run(args.base)
    if failures:
        print("FAIL Wave489 RTCutscene probe")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("PASS Wave489 RTCutscene probe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
