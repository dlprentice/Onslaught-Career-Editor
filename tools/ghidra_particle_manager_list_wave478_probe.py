#!/usr/bin/env python3
"""Validate Wave478 particle-manager global-list link/unlink correction."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave478-engine-queue-head-004cdbe0"

LINK_ADDR = "0x004cdba0"
UNLINK_ADDR = "0x004cdbe0"
CALLER_ADDR = "0x004c0560"
OLD_UNLINK_NAME = "CEngine__UnlinkNodeFromDoublyLinkedList"

EXPECTED = {
    LINK_ADDR: {
        "name": "CParticleManager__LinkNodeByOffset3C40",
        "signature": "void __thiscall CParticleManager__LinkNodeByOffset3C40(void * this, void * node)",
        "tags": {
            "comment-hardened",
            "linked-list",
            "particle-manager",
            "particle-manager-list-wave478",
            "retail-binary-evidence",
            "signature-corrected",
            "static-reaudit",
        },
        "comment_tokens": [
            "Wave478 signature/comment hardening",
            "[ESP+4]",
            "RET 0x4",
            "CParticleManager__AppendNodeToActiveList",
            "0x0082b400",
            "head/tail fields +0x4/+0x8",
            "node +0x3c/+0x40",
            "runtime particle scheduling behavior",
            "rebuild parity remain unproven",
        ],
        "decompile_tokens": [
            "CParticleManager__LinkNodeByOffset3C40",
            "void *this,void *node",
            "this + 8",
            "this + 4",
            "node + 0x3c",
            "node + 0x40",
        ],
    },
    UNLINK_ADDR: {
        "name": "CParticleManager__UnlinkNodeByOffset3C40",
        "signature": "void __thiscall CParticleManager__UnlinkNodeByOffset3C40(void * this, void * node)",
        "tags": {
            "comment-hardened",
            "linked-list",
            "owner-corrected",
            "particle-manager",
            "particle-manager-list-wave478",
            "retail-binary-evidence",
            "signature-corrected",
            "static-reaudit",
        },
        "comment_tokens": [
            "Wave478 owner/signature correction",
            "[ESP+4]",
            "RET 0x4",
            "prior param_1/param_2 shape",
            "CParticleManager__LinkNodeByOffset3C40",
            "CParticleManager__UnlinkNodeFromActiveList",
            "0x0082b400",
            "head/tail fields +0x4/+0x8",
            "node +0x3c/+0x40",
            "runtime particle scheduling behavior",
            "rebuild parity remain unproven",
        ],
        "decompile_tokens": [
            "CParticleManager__UnlinkNodeByOffset3C40",
            "void *this,void *node",
            "node + 0x3c",
            "node + 0x40",
            "this + 4",
            "this + 8",
        ],
    },
}

EXPECTED_SUMMARIES = {
    "apply_particle_manager_list_wave478_dry.log": {
        "updated": 0,
        "skipped": 2,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 1,
        "missing": 0,
        "bad": 0,
    },
    "apply_particle_manager_list_wave478_dry_corrected.log": {
        "updated": 0,
        "skipped": 2,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_particle_manager_list_wave478_apply_corrected.log": {
        "updated": 2,
        "skipped": 0,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
    "apply_particle_manager_list_wave478_verify_dry.log": {
        "updated": 0,
        "skipped": 2,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    },
}

EXPECTED_XREFS = {
    (CALLER_ADDR, "0x004caebc", "CParticle__Destroy"),
    (CALLER_ADDR, "0x004cb8ad", "CParticleManager__AllocateParticle"),
    (LINK_ADDR, "0x004c0520", "CParticleManager__AppendNodeToActiveList"),
    (UNLINK_ADDR, "0x004c05b4", "CParticleManager__UnlinkNodeFromActiveList"),
}

EXPECTED_PAIR_ROWS = {
    "0x004cdba0": ("MOV", "EDX, dword ptr [ECX + 0x8]"),
    "0x004cdbbf": ("RET", "0x4"),
    "0x004cdbce": ("RET", "0x4"),
    "0x004cdbe0": ("MOV", "EAX, dword ptr [ESP + 0x4]"),
    "0x004cdc12": ("RET", "0x4"),
    "0x004cdc22": ("RET", "0x4"),
}

EXPECTED_CALLSITE_ROWS = {
    "0x004c0520": ("CALL", "0x004cdba0"),
    "0x004c05ae": ("PUSH", "ECX"),
    "0x004c05af": ("MOV", "ECX, 0x82b400"),
    "0x004c05b4": ("CALL", "0x004cdbe0"),
}

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime particle scheduling behavior proven",
    "exact source identity proven",
    "global-list type proven",
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


def check_summary(path: Path, expected: dict[str, int], label: str, failures: list[str]) -> None:
    actual = parse_summary(path)
    if actual != expected:
        failures.append(f"{label}: expected summary {expected}, got {actual or '<missing>'}")
    if "REPORT: Save succeeded" not in read_text(path):
        failures.append(f"{label}: missing REPORT: Save succeeded")


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


def check_optional_initial_apply_issue(base: Path, failures: list[str]) -> None:
    path = base / "apply_particle_manager_list_wave478_apply.log"
    if not path.is_file():
        return
    summary = parse_summary(path)
    if summary.get("bad") != 2 or summary.get("renamed") != 1:
        failures.append(f"initial apply issue log: expected renamed=1 bad=2, got {summary or '<missing>'}")
    text = read_text(path)
    if "Read-back signature mismatch" not in text:
        failures.append("initial apply issue log: missing read-back signature mismatch text")
    if "REPORT: Save succeeded" not in text:
        failures.append("initial apply issue log: missing REPORT: Save succeeded")


def check_metadata(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_metadata.tsv")
    for address, expected in EXPECTED.items():
        row = row_by_address(rows, address)
        if row is None:
            failures.append(f"{address}: missing metadata row")
            continue
        if row.get("name") != expected["name"]:
            failures.append(f"{address}: expected name {expected['name']}, got {row.get('name')}")
        signature = row.get("signature", "")
        if signature != expected["signature"]:
            failures.append(f"{address}: expected signature {expected['signature']}, got {signature}")
        if "param_" in signature or "unused_ctx" in signature or "list_owner" in signature:
            failures.append(f"{address}: signature still contains stale/generated parameter naming")
        if OLD_UNLINK_NAME in "\n".join([row.get("name", ""), signature, row.get("comment", "")]):
            failures.append(f"{address}: metadata still contains stale name {OLD_UNLINK_NAME}")
        comment = row.get("comment", "")
        for token in expected["comment_tokens"]:
            if not token_present(comment, token):
                failures.append(f"{address}: comment missing token {token!r}")
        for token in OVERCLAIMS:
            if token_present(comment, token):
                failures.append(f"{address}: comment contains overclaim token {token!r}")


def check_tags(base: Path, failures: list[str]) -> None:
    rows = read_tsv(base / "post_tags.tsv")
    for address, expected in EXPECTED.items():
        row = row_by_address(rows, address)
        if row is None:
            failures.append(f"{address}: missing tag row")
            continue
        tags = {tag for tag in row.get("tags", "").split(";") if tag}
        missing = sorted(expected["tags"] - tags)
        if missing:
            failures.append(f"{address}: missing tags {missing}")


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
    for address, expected in EXPECTED.items():
        text = decompile_text_for(base, address)
        if not text:
            failures.append(f"{address}: missing post decompile text")
            continue
        for token in expected["decompile_tokens"]:
            if not token_present(text, token):
                failures.append(f"{address}: decompile missing token {token!r}")
        body = strip_c_comments(text)
        for stale in ("param_1", "param_2", "unused_ctx", "list_owner"):
            if stale in body:
                failures.append(f"{address}: decompile body still contains stale token {stale!r}")
        if OLD_UNLINK_NAME in text:
            failures.append(f"{address}: decompile still contains stale name {OLD_UNLINK_NAME}")
        for token in OVERCLAIMS:
            if token_present(text, token):
                failures.append(f"{address}: decompile contains overclaim token {token!r}")


def check_rows(path: Path, expected_rows: dict[str, tuple[str, str]], label: str, failures: list[str]) -> None:
    rows = read_tsv(path)
    by_addr = {normalize_address(row.get("address", "")): row for row in rows}
    for address, (mnemonic, operands) in expected_rows.items():
        row = by_addr.get(normalize_address(address))
        if row is None:
            failures.append(f"{label}: missing row {address}")
            continue
        if row.get("mnemonic") != mnemonic or row.get("operands") != operands:
            failures.append(f"{label}: {address} expected {mnemonic} {operands}, got {row.get('mnemonic')} {row.get('operands')}")


def check_ranges(base: Path, failures: list[str]) -> None:
    check_rows(base / "link_unlink_pair_post.tsv", EXPECTED_PAIR_ROWS, "link/unlink pair range", failures)
    check_rows(base / "active_list_callsite_post.tsv", EXPECTED_CALLSITE_ROWS, "active-list callsite range", failures)


def run(base: Path) -> list[str]:
    failures: list[str] = []
    for filename, expected in EXPECTED_SUMMARIES.items():
        check_summary(base / filename, expected, filename, failures)
    check_optional_initial_apply_issue(base, failures)
    check_metadata(base, failures)
    check_tags(base, failures)
    check_xrefs(base, failures)
    check_decompile(base, failures)
    check_ranges(base, failures)
    return failures


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("expected --check")
    base = args.base if args.base.is_absolute() else ROOT / args.base
    failures = run(base)
    if failures:
        print("Wave478 particle-manager list probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave478 particle-manager list probe: PASS")
    print(f"Base: {base.relative_to(ROOT)}")
    print("Checked: dry/apply/readback summaries, metadata, tags, xrefs, decompile tokens, and focused disassembly ranges.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
