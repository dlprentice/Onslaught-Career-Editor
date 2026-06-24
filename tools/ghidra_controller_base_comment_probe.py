#!/usr/bin/env python3
"""Validate the Wave373 controller-base Ghidra signature/comment tranche."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

DEFAULT_ROOT = Path("subagents/ghidra-static-reaudit/controller-base-wave373/current")
OUTPUT_NAME = "controller-base-comment.json"

COMMON_TAGS = {
    "static-reaudit",
    "controller-base-wave373",
    "retail-binary-evidence",
}


def target(
    name: str,
    signature: str,
    comment_tokens: list[str],
    decompile_tokens: list[str],
    tags: list[str],
) -> dict[str, object]:
    return {
        "name": name,
        "signature": signature,
        "commentTokens": comment_tokens,
        "decompileTokens": decompile_tokens,
        "tags": tags,
    }


TARGETS: dict[str, dict[str, object]] = {
    "0x0042d7a0": target(
        "CController__ResetInactivityTimerConditional",
        "void __cdecl CController__ResetInactivityTimerConditional(void)",
        [
            "source-parity CController::ResetInactivityTimer",
            "mNonInteractiveSection",
            "mLastTimeAnythingPressed",
            "retail guard",
            "remain unproven",
        ],
        ["DAT_0066e94c", "_DAT_0066e948", "PLATFORM__GetSysTimeFloat"],
        ["controller-system", "inactivity-timer", "source-parity", "signature-hardened", "comment-hardened"],
    ),
    "0x0042d9d0": target(
        "CController__Flush",
        "void __thiscall CController__Flush(void * this)",
        [
            "source-parity CController::Flush",
            "mButtons1/2/3",
            "old-button fields",
            "vtable+0x3c",
            "remain unproven",
        ],
        ["+ 0x20", "+ 0x28", "+ 0x24", "+ 0x14", "+ 0x18", "+ 0x1c", "+ 0x3c"],
        ["controller-system", "virtual-controller", "input-flush", "source-parity", "signature-hardened", "comment-hardened"],
    ),
    "0x0042db40": target(
        "CController__DoMappings",
        "void __thiscall CController__DoMappings(void * this)",
        [
            "source-parity CController::DoMappings",
            "mapping table",
            "push_type switch",
            "demo playback/record hooks",
            "platform mouse/keyboard",
            "remain unproven",
        ],
        [
            "DAT_006254f8",
            "CController__GetMappedInputValue",
            "CController__SendButtonAction",
            "g_MouseSensitivity",
            "PlatformInput__GetKeyOn(0x2a)",
            "PlatformInput__GetKeyOn(0x36)",
        ],
        ["controller-system", "virtual-controller", "mapping-engine", "source-parity", "signature-hardened", "comment-hardened"],
    ),
}

XREF_EVIDENCE = [
    ("0x0042d7a0", "0x004efc45", "CLTShell__InitializeRuntimeAndLoadCoreResources", "UNCONDITIONAL_CALL"),
    ("0x0042d9d0", "0x005d9784", "<no_function>", "DATA"),
    ("0x0042d9d0", "0x005e48e8", "<no_function>", "DATA"),
    ("0x0042db40", "0x005d97b8", "<no_function>", "DATA"),
    ("0x0042db40", "0x005e491c", "<no_function>", "DATA"),
]

INSTRUCTION_EVIDENCE = [
    ("0x0042d7a0", "0x0042d7a0", "MOV", "[0x0066e94c]"),
    ("0x0042d7a0", "0x0042d7a9", "MOV", "[0x0066e948]"),
    ("0x0042d7a0", "0x0042d7b9", "CALL", "0x005159e0"),
    ("0x0042d7a0", "0x0042d7be", "FSTP", "[0x0066e948]"),
    ("0x0042d9d0", "0x0042d9d0", "MOV", "[ECX + 0x14]"),
    ("0x0042d9d0", "0x0042d9d6", "MOV", "[ECX + 0x20]"),
    ("0x0042d9d0", "0x0042d9e6", "MOV", "[ECX + 0x14]"),
    ("0x0042d9d0", "0x0042d9ef", "JMP", "[EDX + 0x3c]"),
    ("0x0042db40", "0x0042db58", "CMP", "-0x1"),
    ("0x0042db40", "0x0042db80", "CALL", "0x00441740"),
    ("0x0042db40", "0x0042db96", "CALL", "[EDX + 0x44]"),
    ("0x0042db40", "0x0042dbe4", "MOV", "[ESI + 0x170]"),
    ("0x0042db40", "0x0042dc1d", "LEA", "[EBP + EAX*0x4 + 0x8]"),
]

STALE_SIGNATURE_TOKENS = ["undefined ", "param_1", "param_2", "unaff_"]
OVERCLAIM_TOKENS = [
    "runtime behavior proven",
    "source identity proven",
    "fully re'ed",
    "100% re",
    "rebuild parity proven",
]


def norm_addr(value: object) -> str:
    text = str(value or "").strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    if not text or text.startswith("<"):
        return text
    return "0x" + text.zfill(8)


def compact(value: str) -> str:
    return "".join(value.lower().split())


def token_present(text: str, token: str) -> bool:
    return compact(token) in compact(text)


def unescape_tsv(value: str) -> str:
    return value.replace("\\t", "\t").replace("\\n", "\n").replace("\\r", "\r").replace("\\\\", "\\")


def read_tsv(path: Path, *, unescape_comment: bool = False) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if unescape_comment:
        for row in rows:
            row["comment"] = unescape_tsv(row.get("comment", ""))
    return rows


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def parse_summary(log_text: str) -> dict[str, object]:
    match = re.search(
        r"SUMMARY:\s+updated=(\d+)\s+skipped=(\d+)\s+renamed=(\d+)\s+missing=(\d+)\s+bad=(\d+)",
        log_text,
    )
    if not match:
        return {}
    return {
        "updated": int(match.group(1)),
        "skipped": int(match.group(2)),
        "renamed": int(match.group(3)),
        "missing": int(match.group(4)),
        "bad": int(match.group(5)),
    }


def row_by_addr(rows: list[dict[str, str]], key: str = "address") -> dict[str, dict[str, str]]:
    return {norm_addr(row.get(key, "")): row for row in rows}


def decompile_for(decompile_dir: Path, address: str) -> str:
    matches = sorted(decompile_dir.glob(f"{norm_addr(address)[2:]}_*.c"))
    return "\n".join(read_text(path) for path in matches)


def any_row(rows: list[dict[str, str]], predicate) -> bool:
    return any(predicate(row) for row in rows)


def build_report(
    *,
    root: Path = DEFAULT_ROOT,
    dry_log_path: Path | None = None,
    apply_log_path: Path | None = None,
    metadata_path: Path | None = None,
    tags_path: Path | None = None,
    xrefs_path: Path | None = None,
    instructions_path: Path | None = None,
    decompile_dir: Path | None = None,
) -> dict[str, object]:
    root = Path(root)
    dry_log_path = dry_log_path or root / "controller_base_comment_dry.log"
    apply_log_path = apply_log_path or root / "controller_base_comment_apply.log"
    metadata_path = metadata_path or root / "metadata_after.tsv"
    tags_path = tags_path or root / "tags_after.tsv"
    xrefs_path = xrefs_path or root / "xrefs_after.tsv"
    instructions_path = instructions_path or root / "instructions_after.tsv"
    decompile_dir = decompile_dir or root / "decompile_after"

    failures: list[str] = []
    expected_count = len(TARGETS)
    dry_summary = parse_summary(read_text(dry_log_path))
    apply_summary = parse_summary(read_text(apply_log_path))
    if dry_summary != {"updated": 0, "skipped": expected_count, "renamed": 0, "missing": 0, "bad": 0}:
        failures.append(f"unexpected dry summary: {dry_summary}")
    if apply_summary != {"updated": expected_count, "skipped": 0, "renamed": 0, "missing": 0, "bad": 0}:
        failures.append(f"unexpected apply summary: {apply_summary}")

    metadata = row_by_addr(read_tsv(metadata_path, unescape_comment=True))
    tags = row_by_addr(read_tsv(tags_path))
    xrefs = read_tsv(xrefs_path)
    instructions = read_tsv(instructions_path)

    xref_hits = 0
    instruction_hits = 0
    stale_signature_hits = 0
    overclaim_hits = 0

    for address, spec in TARGETS.items():
        row = metadata.get(norm_addr(address))
        if not row:
            failures.append(f"{address} metadata missing")
            continue
        name = row.get("name", "")
        signature = row.get("signature", "")
        comment = row.get("comment", "")
        if row.get("status") != "OK":
            failures.append(f"{address} metadata status mismatch: {row.get('status')}")
        if name != spec["name"]:
            failures.append(f"{address} name mismatch: {name} != {spec['name']}")
        if signature != spec["signature"]:
            failures.append(f"{address} signature mismatch: {signature} != {spec['signature']}")
        for token in STALE_SIGNATURE_TOKENS:
            if token_present(signature, token):
                stale_signature_hits += 1
                failures.append(f"{address} stale signature token present: {token}")
        for token in spec["commentTokens"]:
            if not token_present(comment, str(token)):
                failures.append(f"{address} missing comment token: {token}")
        for token in OVERCLAIM_TOKENS:
            if token_present(comment, token):
                overclaim_hits += 1
                failures.append(f"{address} overclaim token present: {token}")

        tag_row = tags.get(norm_addr(address))
        if not tag_row or tag_row.get("status") != "OK":
            failures.append(f"{address} tag row missing or bad")
        else:
            actual_tags = {tag.strip() for tag in tag_row.get("tags", "").split(";") if tag.strip()}
            expected_tags = COMMON_TAGS | set(spec["tags"])
            missing_tags = sorted(expected_tags - actual_tags)
            if missing_tags:
                failures.append(f"{address} missing tags: {missing_tags}")

        decompile = decompile_for(decompile_dir, address)
        if not decompile:
            failures.append(f"{address} decompile missing")
        for token in spec["decompileTokens"]:
            if not token_present(decompile, str(token)):
                failures.append(f"{address} missing decompile token: {token}")

    for target_addr, from_addr, from_function, ref_type in XREF_EVIDENCE:
        found = any_row(
            xrefs,
            lambda row, target_addr=target_addr, from_addr=from_addr, from_function=from_function, ref_type=ref_type: (
                norm_addr(row.get("target_addr")) == norm_addr(target_addr)
                and norm_addr(row.get("from_addr")) == norm_addr(from_addr)
                and row.get("from_function") == from_function
                and row.get("ref_type") == ref_type
            ),
        )
        if found:
            xref_hits += 1
        else:
            failures.append(f"missing xref evidence {from_addr} -> {target_addr} {from_function} {ref_type}")

    for target_addr, instruction_addr, mnemonic, operand_token in INSTRUCTION_EVIDENCE:
        found = any_row(
            instructions,
            lambda row, target_addr=target_addr, instruction_addr=instruction_addr, mnemonic=mnemonic, operand_token=operand_token: (
                norm_addr(row.get("target_addr")) == norm_addr(target_addr)
                and norm_addr(row.get("instruction_addr")) == norm_addr(instruction_addr)
                and row.get("mnemonic") == mnemonic
                and token_present(row.get("operands", ""), operand_token)
            ),
        )
        if found:
            instruction_hits += 1
        else:
            failures.append(f"missing instruction evidence {target_addr} {instruction_addr} {mnemonic} {operand_token}")

    return {
        "schema": "ghidra-controller-base-comment.v1",
        "status": "PASS" if not failures else "FAIL",
        "root": str(root),
        "summary": {
            "targets": expected_count,
            "xrefEvidenceHits": xref_hits,
            "instructionEvidenceHits": instruction_hits,
            "staleSignatureHits": stale_signature_hits,
            "overclaimHits": overclaim_hits,
        },
        "targets": TARGETS,
        "failures": failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    report = build_report(root=args.root)
    args.root.mkdir(parents=True, exist_ok=True)
    output_path = args.root / OUTPUT_NAME
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{report['status']}: wrote {output_path}")
    print(json.dumps(report["summary"], sort_keys=True))
    if args.check and report["status"] != "PASS":
        for failure in report["failures"]:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
