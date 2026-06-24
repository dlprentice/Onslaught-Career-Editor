#!/usr/bin/env python3
"""Validate Wave477 particle/effect-link owner and signature correction."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave477-unit-finalize-linked-state-004cb0b0"

TARGET = "0x004cb0b0"
EXPECTED_NAME = "ParticleEffectLink__SetHandleStateAndClear"
EXPECTED_SIGNATURE = "void __thiscall ParticleEffectLink__SetHandleStateAndClear(void * this, int set_state_one)"
OLD_NAME = "CUnit__FinalizeLinkedUnitStateAndClear"

EXPECTED_TAGS = {
    "comment-hardened",
    "effect-handle",
    "owner-corrected",
    "particle",
    "particle-effect-link-wave477",
    "retail-binary-evidence",
    "signature-corrected",
    "static-reaudit",
}
COMMENT_TOKENS = [
    "Wave477 owner/signature correction",
    "RET 0x4",
    "one stack argument",
    "prior extra param_2",
    "this +0x4",
    "handle +0xb4",
    "set_state_one",
    "old CUnit owner is too narrow",
    "raw caller boundaries",
    "runtime particle/effect behavior",
    "rebuild parity remain unproven",
]
DECOMPILE_TOKENS = [
    "ParticleEffectLink__SetHandleStateAndClear",
    "set_state_one",
    "this + 4",
    "+ 0xb4",
    "= 2",
    "= 1",
]
EXPECTED_XREFS = {
    (TARGET, "0x004ba4a0", "CMine__VFunc02_CleanupLinkedParticleAndForward"),
    (TARGET, "0x004f8539", "CUnit__dtor_base"),
    (TARGET, "0x00405a95", "CBattleEngine__dtor_base"),
    (TARGET, "0x004c5713", "<no_function>"),
    (TARGET, "0x004db70c", "CEngine__ArmProjectileAndSpawnTrailEffect"),
}
COMMENT_REFRESH_TARGETS = {
    "0x0047cea0": "CGroundUnit__ClearLinkedThingFlagsAndResetCounter",
    "0x004ba490": "CMine__VFunc02_CleanupLinkedParticleAndForward",
    "0x004f84e0": "CUnit__dtor_base",
}
EXPECTED_DRY = {
    "updated": 0,
    "skipped": 1,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 1,
    "missing": 0,
    "bad": 0,
}
EXPECTED_APPLY = {
    "updated": 1,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 1,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_VERIFY_DRY = {
    "updated": 0,
    "skipped": 1,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_COMMENT_REFRESH_DRY = {
    "updated": 0,
    "skipped": 3,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_COMMENT_REFRESH_APPLY = {
    "updated": 3,
    "skipped": 0,
    "created": 0,
    "would_create": 0,
    "renamed": 0,
    "would_rename": 0,
    "missing": 0,
    "bad": 0,
}
EXPECTED_COMMENT_REFRESH_VERIFY_DRY = EXPECTED_COMMENT_REFRESH_DRY
OVERCLAIMS = (
    "runtime behavior proven",
    "runtime particle/effect behavior proven",
    "exact source identity proven",
    "raw caller boundary proven",
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
        for key in ("address", "target_addr", "from_addr", "from_function_addr", "instruction_addr", "function_entry"):
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


def parse_summary(path: Path) -> dict[str, int]:
    text = read_text(path)
    match = re.search(
        r"updated=(?P<updated>\d+)\s+skipped=(?P<skipped>\d+)\s+created=(?P<created>\d+)\s+"
        r"would_create=(?P<would_create>\d+)\s+renamed=(?P<renamed>\d+)\s+"
        r"would_rename=(?P<would_rename>\d+)\s+missing=(?P<missing>\d+)\s+bad=(?P<bad>\d+)",
        text,
    )
    if not match:
        return {}
    return {key: int(value) for key, value in match.groupdict().items()}


def decompile_text_for(base: Path, address: str) -> str:
    directory = base / "post-decomp"
    if not directory.is_dir():
        return ""
    wanted = normalize_address(address)[2:]
    for path in directory.glob(f"{wanted}_*.c"):
        return read_text(path)
    return ""


def strip_c_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return re.sub(r"//.*", "", text)


def check_summary(path: Path, expected: dict[str, int], label: str, failures: list[str]) -> None:
    actual = parse_summary(path)
    if actual != expected:
        failures.append(f"{label}: expected summary {expected}, got {actual or '<missing>'}")
    if "REPORT: Save succeeded" not in read_text(path):
        failures.append(f"{label}: missing REPORT: Save succeeded")


def check_metadata(base: Path, failures: list[str]) -> None:
    row = row_by_address(read_tsv(base / "post_metadata.tsv"), TARGET)
    if row is None:
        failures.append(f"{TARGET}: missing metadata row")
        return
    if row.get("name") != EXPECTED_NAME:
        failures.append(f"{TARGET}: expected name {EXPECTED_NAME}, got {row.get('name')}")
    if row.get("signature") != EXPECTED_SIGNATURE:
        failures.append(f"{TARGET}: expected signature {EXPECTED_SIGNATURE}, got {row.get('signature')}")
    signature = row.get("signature", "")
    if "param_" in signature:
        failures.append(f"{TARGET}: signature still contains param_N")
    haystack = "\n".join([row.get("name", ""), signature, row.get("comment", "")])
    if OLD_NAME in haystack:
        failures.append(f"{TARGET}: metadata still contains stale name {OLD_NAME}")
    comment = row.get("comment", "")
    for token in COMMENT_TOKENS:
        if not token_present(comment, token):
            failures.append(f"{TARGET}: comment missing token {token!r}")
    for token in OVERCLAIMS:
        if token_present(comment, token):
            failures.append(f"{TARGET}: comment contains overclaim token {token!r}")


def check_comment_refresh_metadata(base: Path, failures: list[str]) -> None:
    metadata = read_tsv(base / "post_metadata.tsv")
    tags_rows = read_tsv(base / "post_tags.tsv")
    for address, name in COMMENT_REFRESH_TARGETS.items():
        row = row_by_address(metadata, address)
        if row is None:
            failures.append(f"{address}: missing comment-refresh metadata row")
            continue
        if row.get("name") != name:
            failures.append(f"{address}: expected name {name}, got {row.get('name')}")
        comment = row.get("comment", "")
        if EXPECTED_NAME not in comment:
            failures.append(f"{address}: refreshed comment missing {EXPECTED_NAME}")
        if OLD_NAME in comment:
            failures.append(f"{address}: refreshed comment still contains {OLD_NAME}")
        for token in OVERCLAIMS:
            if token_present(comment, token):
                failures.append(f"{address}: comment contains overclaim token {token!r}")

        tag_row = row_by_address(tags_rows, address)
        tags = {tag for tag in (tag_row or {}).get("tags", "").split(";") if tag}
        for required in ("particle-effect-link-wave477", "comment-hardened", "retail-binary-evidence"):
            if required not in tags:
                failures.append(f"{address}: missing refreshed tag {required}")


def check_tags(base: Path, failures: list[str]) -> None:
    row = row_by_address(read_tsv(base / "post_tags.tsv"), TARGET)
    if row is None:
        failures.append(f"{TARGET}: missing tag row")
        return
    tags = {tag for tag in row.get("tags", "").split(";") if tag}
    missing = sorted(EXPECTED_TAGS - tags)
    if missing:
        failures.append(f"{TARGET}: missing tags {missing}")


def check_xrefs(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_xrefs.tsv")
    edges = {
        (
            normalize_address(row.get("target_addr", "")),
            normalize_address(row.get("from_addr", "")),
            row.get("from_function", ""),
        )
        for row in rows
    }
    for edge in sorted(EXPECTED_XREFS):
        if edge not in edges:
            failures.append(f"post_xrefs.tsv: missing xref edge {edge}")


def check_decompile(base: Path, failures: list[str]) -> None:
    text = decompile_text_for(base, TARGET)
    if not text:
        failures.append(f"{TARGET}: missing post decompile text")
        return
    for token in DECOMPILE_TOKENS:
        if not token_present(text, token):
            failures.append(f"{TARGET}: decompile missing token {token!r}")
    body = strip_c_comments(text)
    if "param_2" in body:
        failures.append(f"{TARGET}: decompile body still contains param_2")
    for token in OVERCLAIMS:
        if token_present(text, token):
            failures.append(f"{TARGET}: decompile contains overclaim token {token!r}")


def check_ranges(base: Path, failures: list[str]) -> None:
    range_rows = read_tsv(base / "post_004cb080_004cb0df_range.tsv")
    range_by_addr = {normalize_address(row.get("address", "")): row for row in range_rows}
    expected_main = {
        "0x004cb0b0": ("MOV", "EAX, dword ptr [ECX + 0x4]"),
        "0x004cb0c2": ("MOV", "word ptr [EAX + 0xb4], 0x2"),
        "0x004cb0ce": ("RET", "0x4"),
        "0x004cb0d1": ("MOV", "word ptr [EAX + 0xb4], 0x1"),
        "0x004cb0dd": ("RET", "0x4"),
    }
    for address, (mnemonic, operands) in expected_main.items():
        row = range_by_addr.get(address)
        if row is None:
            failures.append(f"{address}: missing main-range row")
            continue
        if row.get("mnemonic") != mnemonic or row.get("operands") != operands:
            failures.append(f"{address}: expected {mnemonic} {operands}, got {row.get('mnemonic')} {row.get('operands')}")

    raw_rows = read_tsv(base / "post_004c5700_004c572d_rawcaller.tsv")
    raw_by_addr = {normalize_address(row.get("address", "")): row for row in raw_rows}
    expected_raw = {
        "0x004c570f": ("PUSH", "0x1"),
        "0x004c5713": ("CALL", "0x004cb0b0"),
        "0x004c571a": ("CALL", "0x004cb050"),
        "0x004c5725": ("CALL", "0x00549220"),
    }
    for address, (mnemonic, operands) in expected_raw.items():
        row = raw_by_addr.get(address)
        if row is None:
            failures.append(f"{address}: missing raw-caller row")
            continue
        if row.get("mnemonic") != mnemonic or row.get("operands") != operands:
            failures.append(f"{address}: expected {mnemonic} {operands}, got {row.get('mnemonic')} {row.get('operands')}")


def check_callsite_pushes(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_callsite_instructions.tsv")
    pushes = {(row.get("mnemonic"), row.get("operands")) for row in rows}
    for operands in ("0x0", "0x1"):
        if ("PUSH", operands) not in pushes:
            failures.append(f"post_callsite_instructions.tsv: missing PUSH {operands} evidence")


def run(base: Path) -> list[str]:
    failures: list[str] = []
    check_summary(base / "dry.log", EXPECTED_DRY, "dry.log", failures)
    check_summary(base / "apply.log", EXPECTED_APPLY, "apply.log", failures)
    check_summary(base / "verify_dry.log", EXPECTED_VERIFY_DRY, "verify_dry.log", failures)
    check_summary(base / "comment_refresh_dry.log", EXPECTED_COMMENT_REFRESH_DRY, "comment_refresh_dry.log", failures)
    check_summary(base / "comment_refresh_apply.log", EXPECTED_COMMENT_REFRESH_APPLY, "comment_refresh_apply.log", failures)
    check_summary(
        base / "comment_refresh_verify_dry.log",
        EXPECTED_COMMENT_REFRESH_VERIFY_DRY,
        "comment_refresh_verify_dry.log",
        failures,
    )
    check_metadata(base, failures)
    check_comment_refresh_metadata(base, failures)
    check_tags(base, failures)
    check_xrefs(base, failures)
    check_decompile(base, failures)
    check_ranges(base, failures)
    check_callsite_pushes(base, failures)
    return failures


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--check", action="store_true", help="Compatibility flag for npm verification scripts.")
    args = parser.parse_args(argv)

    failures = run(args.base)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print(f"PASS: Wave477 particle/effect-link evidence validated at {args.base}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
