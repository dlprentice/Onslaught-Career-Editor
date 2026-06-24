#!/usr/bin/env python3
"""Validate the saved Ghidra ComponentBasedOn copy helper signature pass."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "component-based-copy-wave335" / "current"

ADDRESS = "0x00433390"
COMMON_TAGS = [
    "static-reaudit",
    "physics-script-wave335",
    "physics-script",
    "component-based-copy",
    "retail-binary-evidence",
]

TARGET: dict[str, object] = {
    "address": ADDRESS,
    "name": "CComponentBasedOn__CopyFrom",
    "signature": [
        "void",
        "__thiscall",
        "CComponentBasedOn__CopyFrom",
        "void * this",
        "void * sourceComponent",
    ],
    "staleSignature": ["param_1", "param_2", "int param_"],
    "comment": [
        "Signature/comment/tag hardening",
        "component-based statement deep-copy helper",
        "owned string/resource pointer fields",
        "OID__FreeObject",
        "OID__AllocObject",
        "WorldPhysicsManager.cpp",
        "CSPtrSet__AddToTail",
        "this+0x5c",
        "this+0x164",
        "remain unproven",
    ],
    "tags": COMMON_TAGS + ["copy-helper", "resource-field-copy"],
}

EXPECTED_XREFS = ("CComponentBasedOn__VFunc_01_0043db90", "<no_function>")
MIN_XREF_ROWS = 4
DECOMPILE_TOKENS = (
    "sourceComponent",
    "OID__FreeObject",
    "OID__AllocObject",
    "s_C__dev_ONSLAUGHT2_WorldPhysicsMa_00625850",
    "CSPtrSet__AddToTail",
    "((int)this + 0x5c)",
    "((int)this + 0x164)",
)
INSTRUCTION_TOKENS = (
    "0x625850",
    "0x7ef",
    "0x004e5b20",
    "[EBX + 0x5c]",
    "[EBX + 0x164]",
    "RET 0x4",
)

DEFAULT_METADATA_FINAL = BASE / "metadata_final.tsv"
DEFAULT_INDEX = BASE / "decompile_final" / "index.tsv"
DEFAULT_DECOMPILE_DIR = BASE / "decompile_final"
DEFAULT_XREFS = BASE / "xrefs_final.tsv"
DEFAULT_INSTRUCTIONS = BASE / "instructions_final.tsv"
DEFAULT_TAGS = BASE / "tags_final.tsv"
DEFAULT_OUT = BASE / "component-based-copy-signature.json"

OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "source identity proven",
    "fully re'ed",
    "100% re",
    "exact source identity proven",
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
    if not value:
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
        for key in ("address", "target_addr", "function_entry", "target_raw"):
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


def build_report(
    *,
    metadata_final_path: Path = DEFAULT_METADATA_FINAL,
    decompile_index_path: Path = DEFAULT_INDEX,
    decompile_dir: Path = DEFAULT_DECOMPILE_DIR,
    xrefs_path: Path = DEFAULT_XREFS,
    instructions_path: Path = DEFAULT_INSTRUCTIONS,
    tags_path: Path = DEFAULT_TAGS,
) -> dict[str, object]:
    metadata_final_path = resolve(metadata_final_path)
    decompile_index_path = resolve(decompile_index_path)
    decompile_dir = resolve(decompile_dir)
    xrefs_path = resolve(xrefs_path)
    instructions_path = resolve(instructions_path)
    tags_path = resolve(tags_path)

    failures: list[str] = []
    for path, label in (
        (metadata_final_path, "metadata_final"),
        (decompile_index_path, "decompile_index"),
        (xrefs_path, "xrefs"),
        (instructions_path, "instructions"),
        (tags_path, "tags"),
    ):
        if not path.is_file():
            failures.append(f"missing {label}: {relative(path)}")

    metadata_rows = read_tsv(metadata_final_path)
    index_rows = read_tsv(decompile_index_path)
    xref_rows = read_tsv(xrefs_path)
    instruction_rows = read_tsv(instructions_path)
    tag_rows = read_tsv(tags_path)

    address = ADDRESS
    expected = TARGET
    final = row_by_address(metadata_rows, address)
    index = row_by_address(index_rows, address)
    tag_row = row_by_address(tag_rows, address)
    decompile_text = decompile_text_for(decompile_dir, address)
    xrefs = rows_for_address(xref_rows, address, "target_addr")
    instructions = rows_for_address(instruction_rows, address, "target_addr")
    instruction_text = "\n".join(
        " ".join(row.get(key, "") for key in ("mnemonic", "operands", "bytes", "flow_type")) for row in instructions
    )

    present_tags: set[str] = set()
    if final is None:
        failures.append(f"{address} missing from final metadata")
    else:
        if final.get("status") != "OK":
            failures.append(f"{address} metadata status not OK: {final.get('status')}")
        if final.get("name") != expected["name"]:
            failures.append(f"{address} name mismatch: {final.get('name')} != {expected['name']}")
        signature = final.get("signature", "")
        for token in expected["signature"]:  # type: ignore[index]
            if not token_present(signature, str(token)):
                failures.append(f"{address} signature token missing: {token}")
        for token in expected["staleSignature"]:  # type: ignore[index]
            if token_present(signature, str(token)):
                failures.append(f"{address} stale signature token still present: {token}")
        comment = final.get("comment", "")
        for token in expected["comment"]:  # type: ignore[index]
            if not token_present(comment, str(token)):
                failures.append(f"{address} comment token missing: {token}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                failures.append(f"{address} overclaim token present in comment: {token}")

    if index is None:
        failures.append(f"{address} missing from decompile index")
    elif index.get("status") != "OK":
        failures.append(f"{address} decompile status not OK: {index.get('status')}")
    if not decompile_text:
        failures.append(f"{address} decompile text missing")
    else:
        for token in DECOMPILE_TOKENS:
            if not token_present(decompile_text, token):
                failures.append(f"{address} decompile token missing: {token}")
        signature_line = "void __thiscall CComponentBasedOn__CopyFrom(void *this,void *sourceComponent)"
        if not token_present(decompile_text, signature_line):
            failures.append(f"{address} decompile signature token missing: {signature_line}")

    caller_names = [row.get("from_function", "") for row in xrefs]
    for caller in EXPECTED_XREFS:
        if caller not in caller_names:
            failures.append(f"{address} expected xref missing from {caller}")
    if len(xrefs) < MIN_XREF_ROWS:
        failures.append(f"{address} xref row count below expected floor: {len(xrefs)}")

    if not instructions:
        failures.append(f"{address} instruction read-back missing")
    else:
        for token in INSTRUCTION_TOKENS:
            if not token_present(instruction_text, token):
                failures.append(f"{address} instruction token missing: {token}")

    if tag_row is None:
        failures.append(f"{address} tag row missing")
    else:
        present_tags = parse_tags(tag_row.get("tags", ""))
        for tag in expected["tags"]:  # type: ignore[index]
            if str(tag) not in present_tags:
                failures.append(f"{address} tag missing: {tag}")

    return {
        "schema": "ghidra-component-based-copy-signature.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "target": {
            "address": address,
            "name": expected["name"],
            "tags": sorted(present_tags),
            "xrefRows": len(xrefs),
            "instructionRows": len(instructions),
        },
        "evidence": {
            "metadataFinal": relative(metadata_final_path),
            "decompileIndex": relative(decompile_index_path),
            "decompileDir": relative(decompile_dir),
            "xrefs": relative(xrefs_path),
            "instructions": relative(instructions_path),
            "tags": relative(tags_path),
        },
        "failures": failures,
        "notProven": [
            "Exact source method identity remains open because no matching source body was found in the current references.",
            "Concrete ComponentBasedOn field names and owned resource layouts remain partial.",
            "Runtime behavior and rebuild parity are not proven by this static Ghidra hardening pass.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata-final", type=Path, default=DEFAULT_METADATA_FINAL)
    parser.add_argument("--decompile-index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xrefs", type=Path, default=DEFAULT_XREFS)
    parser.add_argument("--instructions", type=Path, default=DEFAULT_INSTRUCTIONS)
    parser.add_argument("--tags", type=Path, default=DEFAULT_TAGS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_report(
        metadata_final_path=args.metadata_final,
        decompile_index_path=args.decompile_index,
        decompile_dir=args.decompile_dir,
        xrefs_path=args.xrefs,
        instructions_path=args.instructions,
        tags_path=args.tags,
    )
    out = resolve(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{report['status']}: wrote {relative(out)}")
    if report["failures"]:
        for failure in report["failures"]:
            print(f"- {failure}")
    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
