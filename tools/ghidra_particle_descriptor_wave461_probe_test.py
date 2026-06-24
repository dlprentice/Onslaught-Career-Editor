#!/usr/bin/env python3
"""Unit checks for the Wave461 particle-descriptor probe helpers."""

from __future__ import annotations

import tempfile
from pathlib import Path

import ghidra_particle_descriptor_wave461_probe as probe


def test_normalize_address() -> None:
    assert probe.normalize_address("004C07F0") == "0x004c07f0"
    assert probe.normalize_address("0x4c59e0") == "0x004c59e0"
    assert probe.normalize_address("<none>") == "<none>"


def test_parse_summary() -> None:
    text = "INFO SUMMARY updated=14 skipped=0 created=0 would_create=0 renamed=14 would_rename=0 missing=0 bad=0"
    assert probe.parse_summary(text) == {
        "updated": 14,
        "skipped": 0,
        "created": 0,
        "would_create": 0,
        "renamed": 14,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    }


def test_read_tsv_normalizes_addresses_and_comments() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "sample.tsv"
        path.write_text(
            "address\tfrom_addr\tcomment\n"
            "004C07F0\t005DDF7C\tline one\\nline two\n",
            encoding="utf-8",
        )
        rows = probe.read_tsv(path)
    assert rows == [
        {
            "address": "0x004c07f0",
            "from_addr": "0x005ddf7c",
            "comment": "line one\nline two",
        }
    ]


def test_target_contract_counts() -> None:
    assert len(probe.TARGETS) == 14
    assert probe.EXPECTED_DRY["would_rename"] == 12
    assert probe.EXPECTED_APPLY["renamed"] == 12


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
