#!/usr/bin/env python3
"""Validate the Wave395 Goodies saved-Ghidra comment/tag tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "goodies-wave395" / "current"

COMMON_TAGS = {
    "static-reaudit",
    "goodies-wave395",
    "frontend-goodies",
    "retail-binary-evidence",
}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    decompile_tokens: list[str],
    instruction_tokens: list[str],
    tags: list[str],
    xref_tokens: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "decompileTokens": decompile_tokens,
        "instructionTokens": instruction_tokens,
        "tags": sorted(COMMON_TAGS | set(tags)),
        "xrefTokens": xref_tokens,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x0045ac30": target(
        "CFEPGoodies__BuildStaticGoodieDataTable",
        "void CFEPGoodies__BuildStaticGoodieDataTable(void)",
        ["materializes the retail Goodies metadata table", "CGoodieData-style records", "Static/source-parity evidence only", "runtime unlock/display behavior", "rebuild parity remain unproven"],
        ["CGoodieData__ctor", "DAT_00679848", "-1,-1,-1,-1,5,5"],
        ["[0x006782a0]", "[0x00678304]", "0x0045c770"],
        ["goodie-data-table", "comment-hardened"],
        ["<none>"],
    ),
    "0x0045c770": target(
        "CGoodieData__ctor",
        "void __thiscall CGoodieData__ctor(void * this, int method, int method2, int number, int number2, int t1, int t2)",
        ["writes Method, Method2, Number, Number2, mT1, and mT2", "six 4-byte CGoodieData fields", "Static/source-parity evidence only", "enum names", "concrete structure typing remain unproven"],
        ["this = method", "+ 4) = method2", "+ 8) = number", "+ 0xc) = number2", "+ 0x10) = t1", "+ 0x14) = t2"],
        ["[EAX + 0x14]", "RET\t0x18"],
        ["goodie-data-table", "goodie-record", "comment-hardened"],
        ["CFEPGoodies__BuildStaticGoodieDataTable"],
    ),
    "0x0045c870": target(
        "CFEPGoodies__Deserialise",
        "void __thiscall CFEPGoodies__Deserialise(void * this, void * chunk_reader)",
        ["frees any current payload", "reads the GDAT payload type", "texture pointer array", "texture count/height", "mesh slot state", "Static retail evidence only", "runtime playback/viewer behavior", "rebuild parity remain unproven"],
        ["CFEPGoodies__FreeUpGoodyResources", "CChunkReader__GetNext", "+ 0x154", "CDXTexture__Deserialize", "CMesh__Deserialize", "+ 0x148"],
        ["[ESI + 0x154]", "0x4b1", "0x4d9"],
        ["resource-deserialise", "gdatie-gdat", "comment-hardened"],
        ["CResourceAccumulator__ReadResourceFile"],
    ),
    "0x0045c9f0": target(
        "CFEPGoodies__StartLoadingGoody",
        "void __fastcall CFEPGoodies__StartLoadingGoody(void * this)",
        ["resets image pan offsets", "maps current grid coordinates through get_goodie_number", "builds the -1000-goodie resource filename", "stores current Goodie type", "starts the async 5MB resource load", "Static/source-parity evidence only", "asset coverage remain unproven"],
        ["+ 0x198", "+ 0x19c", "get_goodie_number", "-1000 - iVar1", "+ 0x154", "0x500000", "+ 0x1d8"],
        ["[EDI + 0x198]", "[EDI + 0x19c]", "0x0045cb80"],
        ["async-goodie-load", "goodie-resource-filename", "comment-hardened"],
        ["CFEPGoodies__ButtonPressed"],
    ),
    "0x0045cb80": target(
        "get_goodie_number",
        "int __cdecl get_goodie_number(int x, int y)",
        ["maps Goodies wall grid coordinates", "row 0 covers bios/race/dev ids", "row 1 unit ids", "row 2 FMV ids", "row 3 artwork/model ids", "returning -1 for invalid cells", "hidden reachability", "UI navigation behavior remain unproven"],
        ["return x + 0x3a", "return 0x4a", "return x + 8", "return x + 0xc9", "x + 0x4e"],
        ["0x3a", "0x4a", "0xc9", "0x4e"],
        ["goodie-grid", "goodie-id-map", "comment-hardened"],
        ["CFEPGoodies__Process", "CFEPGoodies__LoadingGoodyPoll", "CFEPGoodies__ButtonPressed", "CFEPGoodies__StartLoadingGoody"],
    ),
    "0x0045cc10": target(
        "CFEPGoodies__LoadingGoodyPoll",
        "void __fastcall CFEPGoodies__LoadingGoodyPoll(void * this)",
        ["when the async Goodie load has completed", "membuffer exists", "reads the -1000-goodie resource", "closes/frees the buffer", "marks the current Goodie loaded", "Static/source-parity evidence only", "runtime async behavior", "asset decode success remain unproven"],
        ["+ 0x1d8", "CBinkOpenThread__IsRunning", "+ 0x28", "get_goodie_number", "CResourceAccumulator__ReadResourceFile", "CDXMemBuffer__Close", "+ 0x1d8) = 2"],
        ["[ESI + 0x1d8]", "[ESI + 0x28]"],
        ["async-goodie-load", "resource-poll", "comment-hardened"],
        ["CFEPGoodies__Process"],
    ),
    "0x0045cd10": target(
        "CFEPGoodies__FreeUpGoodyResources",
        "void __fastcall CFEPGoodies__FreeUpGoodyResources(void * this)",
        ["releases current Goodie mesh and texture payloads", "destroys texture backing resources", "frees the texture pointer array", "resets Goodie state to NO_GOODY", "Static retail evidence only", "allocator/layout/runtime completeness remain unproven"],
        ["+ 0x148", "+ 0x170", "+ 0x144", "+ 0x14c", "CTexture__Release", "OID__FreeObject", "+ 0x1d8) = 0"],
        ["[ESI + 0x148]", "[ESI + 0x144]", "[ESI + 0x1d8]"],
        ["resource-cleanup", "goodie-resource-lifetime", "comment-hardened"],
        ["CFEPGoodies__Deserialise", "CFEPGoodies__Process", "CFEPGoodies__ButtonPressed"],
    ),
    "0x0045cde0": target(
        "CFEPGoodies__ButtonPressed",
        "void __thiscall CFEPGoodies__ButtonPressed(void * this, int button, float val)",
        ["handles Goodies wall navigation and display controls", "updates mCX/mCY-style grid coordinates", "starts loading selectable unlocked/cheat-overridden Goodies", "marks viewed entries old", "frees resources on back/close paths", "Static/source-parity evidence only", "hidden reachability", "asset-viewer parity remain unproven"],
        ["+ 0x13c", "+ 0x140", "get_goodie_number", "CFEPGoodies__StartLoadingGoody", "CFEPGoodies__FreeUpGoodyResources", "+ 0x1d4", "+ 0x194"],
        ["[EBX + 0x13c]", "[EBX + 0x140]", "0x0045cb80"],
        ["goodies-input", "goodie-grid", "comment-hardened"],
        ["DATA"],
    ),
}

EXPECTED_DRY = {"updated": 0, "skipped": 8, "missing": 0, "bad": 0}
EXPECTED_APPLY = {"updated": 8, "skipped": 0, "missing": 0, "bad": 0}

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime goodies behavior proven",
    "hidden goodies 71-73 reachability proven",
    "exact source identity proven",
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
        for key in ("address", "target_addr", "from_function_addr", "function_entry", "entry_addr"):
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


def validate(args: argparse.Namespace) -> tuple[dict[str, object], int]:
    failures: list[str] = []
    metadata_rows = read_tsv(args.metadata)
    tags_rows = read_tsv(args.tags)
    xref_text = read_text(args.xrefs)
    instruction_text = read_text(args.instructions)
    public_note_text = read_text(args.public_note)

    if not metadata_rows:
        failures.append(f"missing or empty metadata: {args.metadata}")
    if not tags_rows:
        failures.append(f"missing or empty tags: {args.tags}")
    if not xref_text:
        failures.append(f"missing or empty xrefs: {args.xrefs}")
    if not instruction_text:
        failures.append(f"missing or empty instructions: {args.instructions}")
    if not public_note_text:
        failures.append(f"missing or empty public note: {args.public_note}")

    for address, spec in TARGETS.items():
        row = row_by_address(metadata_rows, address)
        if row is None:
            failures.append(f"{address}: missing metadata row")
            continue
        if row.get("name") != spec["name"]:
            failures.append(f"{address}: expected name {spec['name']}, got {row.get('name')}")
        if row.get("signature") != spec["signature"]:
            failures.append(f"{address}: expected signature {spec['signature']}, got {row.get('signature')}")
        comment = row.get("comment", "")
        for token in spec["commentTokens"]:  # type: ignore[index]
            if not token_present(comment, str(token)):
                failures.append(f"{address}: missing comment token {token!r}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                failures.append(f"{address}: overclaim token present in comment: {token!r}")

        tag_row = row_by_address(tags_rows, address)
        if tag_row is None:
            failures.append(f"{address}: missing tag row")
        else:
            tags = parse_tags(tag_row.get("tags", ""))
            for tag in spec["tags"]:  # type: ignore[index]
                if str(tag) not in tags:
                    failures.append(f"{address}: missing tag {tag!r}")

        decompile = decompile_text_for(args.decompile_dir, address)
        if not decompile:
            failures.append(f"{address}: missing decompile export")
        for token in spec["decompileTokens"]:  # type: ignore[index]
            if not token_present(decompile, str(token)):
                failures.append(f"{address}: missing decompile token {token!r}")
        for token in spec["instructionTokens"]:  # type: ignore[index]
            if not token_present(instruction_text, str(token)):
                failures.append(f"{address}: missing instruction token {token!r}")
        for token in spec["xrefTokens"]:  # type: ignore[index]
            if not token_present(xref_text, str(token)):
                failures.append(f"{address}: missing xref token {token!r}")

    for token in (
        "0x0045ac30",
        "0x0045c770",
        "0x0045c870",
        "0x0045c9f0",
        "0x0045cb80",
        "0x0045cc10",
        "0x0045cd10",
        "0x0045cde0",
        "does not prove runtime Goodies behavior",
        "does not prove hidden Goodies 71-73 reachability",
        "does not prove rebuild parity",
    ):
        if not token_present(public_note_text, token):
            failures.append(f"public note missing token {token!r}")
    for token in OVERCLAIM_TOKENS:
        if token_present(public_note_text, token):
            failures.append(f"public note overclaim token present: {token!r}")

    dry_summary = parse_summary(read_text(args.dry_log))
    if dry_summary != EXPECTED_DRY:
        failures.append(f"dry summary mismatch: expected {EXPECTED_DRY}, got {dry_summary}")
    apply_log_text = read_text(args.apply_log)
    apply_summary = parse_summary(apply_log_text)
    if apply_summary != EXPECTED_APPLY:
        failures.append(f"apply summary mismatch: expected {EXPECTED_APPLY}, got {apply_summary}")
    if "REPORT: Save succeeded" not in apply_log_text:
        failures.append("apply log missing REPORT: Save succeeded")

    report = {
        "schema": "ghidra-goodies-wave395.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "targets": len(TARGETS),
        "failures": failures,
        "inputs": {
            "metadata": str(args.metadata),
            "tags": str(args.tags),
            "xrefs": str(args.xrefs),
            "instructions": str(args.instructions),
            "decompileDir": str(args.decompile_dir),
            "publicNote": str(args.public_note),
            "dryLog": str(args.dry_log),
            "applyLog": str(args.apply_log),
        },
    }
    return report, 0 if not failures else 1


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", type=Path, default=BASE / "metadata_after.tsv")
    parser.add_argument("--tags", type=Path, default=BASE / "tags_after.tsv")
    parser.add_argument("--xrefs", type=Path, default=BASE / "xrefs_after.tsv")
    parser.add_argument("--instructions", type=Path, default=BASE / "instructions_after.tsv")
    parser.add_argument("--decompile-dir", type=Path, default=BASE / "decompile_after")
    parser.add_argument("--public-note", type=Path, default=ROOT / "release" / "readiness" / "ghidra_goodies_wave395_2026-05-14.md")
    parser.add_argument("--dry-log", type=Path, default=BASE / "apply_dry.log")
    parser.add_argument("--apply-log", type=Path, default=BASE / "apply.log")
    parser.add_argument("--out", type=Path, default=BASE / "goodies-wave395.json")
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report, status = validate(args)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"status={report['status']} targets={report['targets']} failures={len(report['failures'])} out={args.out.as_posix()}")
    if report["failures"]:
        for failure in report["failures"]:
            print(f"FAIL {failure}")
    return status if args.check else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
