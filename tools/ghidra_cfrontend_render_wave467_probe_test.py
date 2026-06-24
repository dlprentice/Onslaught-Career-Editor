#!/usr/bin/env python3
"""Unit checks for the Wave467 CFrontEnd render probe helpers."""

from __future__ import annotations

import tempfile
from pathlib import Path

import ghidra_cfrontend_render_wave467_probe as probe


def test_normalize_address() -> None:
    assert probe.normalize_address("004685F0") == "0x004685f0"
    assert probe.normalize_address("0x466de0") == "0x00466de0"
    assert probe.normalize_address("<none>") == "<none>"


def test_parse_summary() -> None:
    text = "--- SUMMARY ---\nupdated=15 skipped=0 created=0 would_create=0 renamed=2 would_rename=0 missing=0 bad=0"
    assert probe.parse_summary(text) == {
        "updated": 15,
        "skipped": 0,
        "created": 0,
        "would_create": 0,
        "renamed": 2,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    }


def test_read_tsv_normalizes_addresses_and_comments() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "sample.tsv"
        path.write_text(
            "address\tfrom_addr\tcomment\n"
            "004685A0\t00540FA6\tline one\\nline two\n",
            encoding="utf-8",
        )
        rows = probe.read_tsv(path)
    assert rows == [
        {
            "address": "0x004685a0",
            "from_addr": "0x00540fa6",
            "comment": "line one\nline two",
        }
    ]


def test_target_contract_counts() -> None:
    assert len(probe.TARGETS) == 15
    assert probe.EXPECTED_DRY["skipped"] == 15
    assert probe.EXPECTED_DRY["would_rename"] == 2
    assert probe.EXPECTED_APPLY["updated"] == 15
    assert probe.EXPECTED_APPLY["renamed"] == 2


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
