#!/usr/bin/env python3
"""Unit checks for the Wave465 PauseMenu tail probe helpers."""

from __future__ import annotations

import tempfile
from pathlib import Path

import ghidra_pausemenu_tail_wave465_probe as probe


def test_normalize_address() -> None:
    assert probe.normalize_address("004D01C0") == "0x004d01c0"
    assert probe.normalize_address("0x4d0e40") == "0x004d0e40"
    assert probe.normalize_address("<none>") == "<none>"


def test_parse_summary() -> None:
    text = "--- SUMMARY ---\nupdated=10 skipped=0 created=0 would_create=0 renamed=6 would_rename=0 missing=0 bad=0"
    assert probe.parse_summary(text) == {
        "updated": 10,
        "skipped": 0,
        "created": 0,
        "would_create": 0,
        "renamed": 6,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    }


def test_read_tsv_normalizes_addresses_and_comments() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "sample.tsv"
        path.write_text(
            "address\tfrom_addr\tcomment\n"
            "004D04B0\t004D05E0\tline one\\nline two\n",
            encoding="utf-8",
        )
        rows = probe.read_tsv(path)
    assert rows == [
        {
            "address": "0x004d04b0",
            "from_addr": "0x004d05e0",
            "comment": "line one\nline two",
        }
    ]


def test_target_contract_counts() -> None:
    assert len(probe.TARGETS) == 10
    assert probe.EXPECTED_DRY["skipped"] == 10
    assert probe.EXPECTED_DRY["would_rename"] == 6
    assert probe.EXPECTED_APPLY["updated"] == 10
    assert probe.EXPECTED_APPLY["renamed"] == 6


def main() -> int:
    tests = [
        test_normalize_address,
        test_parse_summary,
        test_read_tsv_normalizes_addresses_and_comments,
        test_target_contract_counts,
    ]
    for test in tests:
        test()
    print(f"PASS {len(tests)}/{len(tests)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
