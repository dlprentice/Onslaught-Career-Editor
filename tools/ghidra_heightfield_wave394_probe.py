#!/usr/bin/env python3
"""Validate the Wave394 heightfield/static-shadow Ghidra correction tranche."""

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
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "heightfield-wave394" / "current"

COMMON_TAGS = {"static-reaudit", "heightfield-wave394", "terrain-heightfield", "retail-binary-evidence"}


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
    "0x0047e8e0": target(
        "CHeightField__InitColorGradient",
        "void __fastcall CHeightField__InitColorGradient(void * this)",
        ["+0x1038/+0x103c", "+0x10d0", "+0x107c/+0x108c", "+0x13c4", "+0x13d0", "source file is absent", "runtime terrain behavior", "rebuild parity remain unproven"],
        ["0x108c", "0x1038", "0x10d0", "0x13d0"],
        ["[ESI + 0x108c]", "[ESI + 0x10bc]", "[ESI + 0x13c4]", "0x40"],
        ["heightfield", "color-gradient", "signature-hardened", "comment-hardened"],
        ["CHeightField__Load"],
    ),
    "0x0047ea20": target(
        "CWorld__GetHeightSamplePacked16",
        "uint __fastcall CWorld__GetHeightSamplePacked16(void * heightfield_or_world, uint x_packed, uint z_packed)",
        ["+0x1028", "packed X/Z", "0x200", "0xa1ffe", "owner label is preserved", "runtime terrain behavior", "rebuild parity remain unproven"],
        ["0x1028", "0x3ffe00", "0xa1ffe"],
        ["[ECX + 0x1028]", "0x3ffe00", "0xa1ffe"],
        ["heightfield", "packed-height-sample", "owner-provisional", "signature-hardened", "comment-hardened"],
        ["CGame__BuildCellMinMaxHeightTable", "CDXLandscape__BuildVertexBuffer"],
    ),
    "0x0047eb00": target(
        "CHeightField__SampleInterpolatedHeight",
        "int __fastcall CHeightField__SampleInterpolatedHeight(void * this, uint x_packed, uint z_packed)",
        ["bilinearly interpolates", "signed 16-bit", "+0x1028", "9x9 tile stride", "runtime terrain behavior", "rebuild parity remain unproven"],
        ["0x1028", "0x14", "0x12", "x_packed & 0xff", "z_packed & 0xff"],
        ["[ECX + 0x1028]", "0x14", "0x12"],
        ["heightfield", "bilinear-height-sample", "signature-hardened", "comment-hardened"],
        ["CStaticShadows__TraceSegmentAgainstHeightfield"],
    ),
    "0x0047eb80": target(
        "CStaticShadows__SampleShadowHeightBilinear",
        "double __fastcall CStaticShadows__SampleShadowHeightBilinear(void * this, void * world_pos)",
        ["corrected the calling convention", "older saved __thiscall", "world-position pointer from EDX", "+0x1028", "+0x102c", "runtime shadow/terrain behavior", "rebuild parity remain unproven"],
        ["world_pos", "0x1028", "0x102c", "0x3e0000", "_DAT_005d856c"],
        ["[ECX + 0x1028]", "[ECX + 0x102c]", "005d856c"],
        ["static-shadows", "heightfield", "bilinear-height-sample", "signature-corrected", "comment-hardened"],
        ["CActor__Move", "CStaticShadows__BuildShadowMaps"],
    ),
    "0x0047ec60": target(
        "CMonitor__SampleHeightfieldNormalAtXY",
        "float * __fastcall CMonitor__SampleHeightfieldNormalAtXY(void * heightfield_or_monitor, void * out_normal, void * world_pos)",
        ["output normal vector", "out_normal pointer", "+0x1028", "+0x102c", "upward normal (0,0,1)", "Owner remains bounded", "runtime terrain-normal behavior", "rebuild parity remain unproven"],
        ["CRT__RoundDoubleWithFpuChecks", "0x1028", "0x102c", "0x3f800000", "SQRT"],
        ["[ECX + 0x1028]", "[ECX + 0x102c]", "005d8568"],
        ["heightfield", "terrain-normal", "owner-provisional", "signature-hardened", "comment-hardened"],
        ["CMonitor__IntegrateMovementAgainstTerrain", "CBattleEngineWalkerPart__Move"],
    ),
}

EXPECTED_DRY = {"updated": 0, "skipped": 5, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}
EXPECTED_APPLY = {"updated": 5, "skipped": 0, "renamed": 0, "would_rename": 0, "missing": 0, "bad": 0}

OVERCLAIM_TOKENS = (
    "runtime proof",
    "runtime terrain behavior proven",
    "runtime shadow behavior proven",
    "source identity proven",
    "source-complete",
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
    match = re.search(
        r"updated=(\d+)\s+skipped=(\d+)\s+renamed=(\d+)\s+would_rename=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        log_text,
    )
    if not match:
        return {"updated": -1, "skipped": -1, "renamed": -1, "would_rename": -1, "missing": -1, "bad": -1}
    return {
        "updated": int(match.group(1)),
        "skipped": int(match.group(2)),
        "renamed": int(match.group(3)),
        "would_rename": int(match.group(4)),
        "missing": int(match.group(5)),
        "bad": int(match.group(6)),
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

    for token in ("0x0047e8e0", "0x0047ea20", "0x0047eb00", "0x0047eb80", "0x0047ec60", "does not prove runtime terrain behavior", "does not prove rebuild parity"):
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
        "schema": "ghidra-heightfield-wave394.v1",
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
    parser.add_argument("--public-note", type=Path, default=ROOT / "release" / "readiness" / "ghidra_heightfield_wave394_2026-05-14.md")
    parser.add_argument("--dry-log", type=Path, default=BASE / "apply_dry.log")
    parser.add_argument("--apply-log", type=Path, default=BASE / "apply.log")
    parser.add_argument("--out", type=Path, default=BASE / "heightfield-wave394.json")
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
