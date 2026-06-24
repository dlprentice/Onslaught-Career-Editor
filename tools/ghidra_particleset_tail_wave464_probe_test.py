#!/usr/bin/env python3
"""Unit checks for the Wave464 ParticleSet tail probe helpers."""

from __future__ import annotations

import tempfile
from pathlib import Path

import ghidra_particleset_tail_wave464_probe as probe


def test_normalize_address() -> None:
    assert probe.normalize_address("004CC870") == "0x004cc870"
    assert probe.normalize_address("0x4cda60") == "0x004cda60"
    assert probe.normalize_address("<none>") == "<none>"


def test_parse_summary() -> None:
    text = "--- SUMMARY ---\nupdated=8 skipped=0 created=0 would_create=0 renamed=3 would_rename=0 missing=0 bad=0"
    assert probe.parse_summary(text) == {
        "updated": 8,
        "skipped": 0,
        "created": 0,
        "would_create": 0,
        "renamed": 3,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    }


def test_read_tsv_normalizes_addresses_and_comments() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "sample.tsv"
        path.write_text(
            "address\tfrom_addr\tcomment\n"
            "004CC870\t004CCB43\tline one\\nline two\n",
            encoding="utf-8",
        )
        rows = probe.read_tsv(path)
    assert rows == [
        {
            "address": "0x004cc870",
            "from_addr": "0x004ccb43",
            "comment": "line one\nline two",
        }
    ]


def test_target_contract_counts() -> None:
    assert len(probe.TARGETS) == 8
    assert probe.EXPECTED_DRY["skipped"] == 8
    assert probe.EXPECTED_DRY["would_rename"] == 3
    assert probe.EXPECTED_APPLY["updated"] == 8
    assert probe.EXPECTED_APPLY["renamed"] == 3


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
