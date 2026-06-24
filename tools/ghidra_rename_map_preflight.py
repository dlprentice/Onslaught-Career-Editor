#!/usr/bin/env python3
"""Local preflight for Ghidra batch rename maps.

This tool validates the repo's strict map format before a map ever reaches
Ghidra. It is intentionally read-only and does not launch Ghidra, mutate a
project, or inspect BEA.exe.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True

ADDRESS_RE = re.compile(r"^(?:0x)?[0-9a-fA-F]{6,16}$")
NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_:$@?]{0,255}$")
WEAK_PREFIXES = ("FUN_", "__Unk_")


@dataclass(frozen=True)
class Finding:
    line: int
    code: str
    message: str


def parse_map(path: Path) -> tuple[list[tuple[int, str, str]], list[Finding]]:
    rows: list[tuple[int, str, str]] = []
    findings: list[Finding] = []
    seen_addresses: dict[str, int] = {}
    seen_names: dict[str, int] = {}
    for index, raw in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split()
        if len(parts) != 2:
            findings.append(Finding(index, "BAD_COLUMN_COUNT", "rename map rows must be exactly two columns: <address> <new_name>"))
            continue
        address, name = parts
        normalized = address.lower()
        if not normalized.startswith("0x"):
            normalized = f"0x{normalized}"
        if not ADDRESS_RE.match(address):
            findings.append(Finding(index, "BAD_ADDRESS", "address must be hex, optionally prefixed with 0x"))
            continue
        if not NAME_RE.match(name):
            findings.append(Finding(index, "BAD_NAME", "target name must be a single identifier-like token"))
            continue
        if name.startswith(WEAK_PREFIXES):
            findings.append(Finding(index, "WEAK_NAME", "target name must not keep weak FUN_/__Unk_ prefixes"))
            continue
        if normalized in seen_addresses:
            findings.append(Finding(index, "DUPLICATE_ADDRESS", f"address already appears on line {seen_addresses[normalized]}"))
            continue
        if name in seen_names:
            findings.append(Finding(index, "DUPLICATE_NAME", f"target name already appears on line {seen_names[name]}"))
            continue
        seen_addresses[normalized] = index
        seen_names[name] = index
        rows.append((index, normalized, name))
    return rows, findings


def run_self_test() -> bool:
    with tempfile.TemporaryDirectory(prefix="ghidra-rename-preflight-") as tmp:
        root = Path(tmp)
        good = root / "good.map"
        good.write_text(
            "# comment\n"
            "0x00406460 CBattleEngine__SwapPrimarySecondaryPartReadersForState\n"
            "00406560 CBattleEngine__UpdateAutoTargetSetAndFireProjectiles\n",
            encoding="utf-8",
        )
        rows, findings = parse_map(good)
        if findings or len(rows) != 2:
            print("SELFTEST FAIL: valid map did not pass")
            return False
        bad = root / "bad.map"
        bad.write_text(
            "0x00406460 CBattleEngine__Old CBattleEngine__New\n"
            "0x00406460 CBattleEngine__DuplicateAddress\n"
            "0x00406560 FUN_00406560\n"
            "not_hex CBadName\n",
            encoding="utf-8",
        )
        _rows, bad_findings = parse_map(bad)
        codes = {finding.code for finding in bad_findings}
        required = {"BAD_COLUMN_COUNT", "WEAK_NAME", "BAD_ADDRESS"}
        if not required.issubset(codes):
            print(f"SELFTEST FAIL: missing expected finding codes {sorted(required - codes)}")
            return False
    print("Ghidra rename map preflight self-test: PASS")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Ghidra rename-map format before dry/apply runs.")
    parser.add_argument("map", nargs="?", type=Path, help="rename map to validate")
    parser.add_argument("--self-test", action="store_true", help="run built-in red/green style parser checks")
    args = parser.parse_args()
    if args.self_test:
        return 0 if run_self_test() else 1
    if args.map is None:
        parser.error("expected a rename map path or --self-test")
    if not args.map.is_file():
        print(f"Rename map not found: {args.map}")
        return 1
    rows, findings = parse_map(args.map)
    print("Ghidra rename map preflight")
    print(f"Map: {args.map}")
    print(f"Rows accepted: {len(rows)}")
    print(f"Findings: {len(findings)}")
    for finding in findings:
        print(f"- line {finding.line}: {finding.code}: {finding.message}")
    return 0 if not findings and rows else 1


if __name__ == "__main__":
    raise SystemExit(main())
